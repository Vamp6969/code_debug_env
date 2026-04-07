"""
Inference Script — Code Debug Environment
==========================================
Structured stdout format: [START], [STEP], [END]
"""

import os
from typing import List

from openai import OpenAI

from client import CodeDebugEnv
from models import CodeDebugAction

API_BASE_URL = os.getenv("API_BASE_URL") or "https://router.huggingface.co/v1"
MODEL_NAME = os.getenv("MODEL_NAME") or "meta-llama/Llama-3.1-8B-Instruct"
API_KEY = os.getenv("HF_TOKEN") or os.getenv("API_KEY")

BENCHMARK = "code-debug-env"
MAX_STEPS = 5

client_llm = OpenAI(base_url=API_BASE_URL, api_key=API_KEY)

SYSTEM_PROMPT = """You are an expert Python debugger.
You will be given broken Python code. Fix ALL bugs and return ONLY the corrected code.
No explanations. No markdown. Just the fixed Python code."""


def run_task(env_url: str, task_id: str, difficulty: str) -> float:
    rewards: List[float] = []
    steps = 0
    success = False
    score = 0.0

    print(f"[START] task={task_id} env={BENCHMARK} model={MODEL_NAME}")

    try:
        with CodeDebugEnv(base_url=env_url).sync() as env:
            result = env.reset(episode_id=task_id)
            obs = result.observation

            for step in range(1, MAX_STEPS + 1):
                try:
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
                        max_tokens=800,
                        temperature=0.2,
                    )
                    fixed_code = response.choices[0].message.content.strip()
                except Exception as e:
                    reward = 0.0
                    rewards.append(reward)
                    steps = step
                    print(f"[STEP] step={step} action=fix_code reward={reward:.2f} done=true error={e}")
                    break

                # Strip markdown code fences if present
                if fixed_code.startswith("```"):
                    lines = fixed_code.split("\n")
                    lines = lines[1:]
                    if lines and lines[-1].strip() == "```":
                        lines = lines[:-1]
                    fixed_code = "\n".join(lines)

                result = env.step(
                    CodeDebugAction(fixed_code=fixed_code, task_id=task_id)
                )
                obs = result.observation
                reward = obs.score
                done = result.done
                rewards.append(reward)
                steps = step

                done_str = "true" if done else "false"
                print(f"[STEP] step={step} action=fix_code reward={reward:.2f} done={done_str} error=null")

                if done:
                    break

            score = obs.score
            success = score == 1.0

    except Exception as e:
        print(f"[STEP] step=1 action=fix_code reward=0.00 done=true error={e}")
        steps = 1
        rewards = [0.0]

    success_str = "true" if success else "false"
    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
    print(f"[END] success={success_str} steps={steps} score={score:.2f} rewards={rewards_str}")

    return score


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
