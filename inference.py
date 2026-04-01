import os

from openai import OpenAI

from client import CodeDebugEnv
from models import CodeDebugAction

API_BASE_URL = os.getenv("API_BASE_URL", "https://router.huggingface.co/v1")
API_KEY = os.getenv("HF_TOKEN") or os.getenv("API_KEY")
MODEL_NAME = os.getenv("MODEL_NAME")
MAX_STEPS = 5

client_llm = OpenAI(base_url=API_BASE_URL, api_key=API_KEY)

SYSTEM_PROMPT = """You are an expert Python debugger.
You will be given broken Python code. Fix ALL bugs and return ONLY the corrected code.
No explanations. No markdown. Just the fixed Python code."""


def run_task(env_url: str, task_id: str, difficulty: str) -> float:
    with CodeDebugEnv(base_url=env_url).sync() as env:
        result = env.reset(episode_id=task_id)
        obs = result.observation
        print(f"\nTask: {task_id} ({difficulty})")
        print(f"Broken code:\n{obs.broken_code}")

        for step in range(MAX_STEPS):
            response = client_llm.chat.completions.create(
                model=MODEL_NAME,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {
                        "role": "user",
                        "content": (
                            f"Fix this Python code:\n\n{obs.broken_code}\n\n"
                            f"Feedback from last attempt: {obs.feedback}"
                        ),
                    },
                ],
                max_tokens=500,
                temperature=0.2,
            )
            fixed_code = response.choices[0].message.content.strip()

            # Strip markdown code fences if present
            if fixed_code.startswith("```"):
                lines = fixed_code.split("\n")
                lines = lines[1:]  # remove opening fence
                if lines and lines[-1].strip() == "```":
                    lines = lines[:-1]
                fixed_code = "\n".join(lines)

            result = env.step(
                CodeDebugAction(fixed_code=fixed_code, task_id=task_id)
            )
            obs = result.observation
            print(
                f"Step {step + 1}: score={obs.score} "
                f"tests={obs.tests_passed}/{obs.total_tests}"
            )
            if result.done:
                break

        return obs.score


if __name__ == "__main__":
    ENV_URL = os.getenv("ENV_URL", "http://localhost:7860")
    tasks = [
        ("easy_001", "easy"),
        ("medium_001", "medium"),
        ("hard_001", "hard"),
    ]
    scores: dict[str, float] = {}
    for task_id, difficulty in tasks:
        scores[task_id] = run_task(ENV_URL, task_id, difficulty)

    print("\n=== BASELINE SCORES ===")
    for task_id, score in scores.items():
        print(f"{task_id}: {score:.2f}")
    print(f"Average: {sum(scores.values()) / len(scores):.2f}")
