---
title: Code Debug Environment
emoji: "\U0001F41B"
colorFrom: blue
colorTo: purple
sdk: docker
app_port: 7860
tags:
  - openenv
  - code-debugging
  - reinforcement-learning
---

# Code Debug Environment

A Python code debugging environment built on [OpenEnv](https://github.com/openenv/openenv). An AI agent receives broken Python code, fixes it, and the environment scores the fix by running it against test cases.

Built for the Meta x Scaler OpenEnv Hackathon.

---

## How It Works

1. The environment presents broken Python code to the agent
2. The agent submits fixed code
3. The environment runs the fixed code against hidden test cases
4. The agent receives a score (0.0 to 1.0) and feedback on which tests failed
5. The agent can retry up to 5 times per task

There are 8 tasks across 3 difficulty levels. The agent must fix syntax errors, logic bugs, data structure misuse, and interdependent bugs across multiple functions.

---

## Project Structure

```
code_debug_env/
  models.py            - Pydantic models (Action, Observation, State)
  client.py            - OpenEnv client for connecting to the server
  inference.py         - LLM-based agent that solves all 8 tasks
  openenv.yaml         - OpenEnv manifest
  pyproject.toml       - Python project config
  Dockerfile           - Container config for deployment
  server/
    app.py             - FastAPI app entry point
    environment.py     - Core environment logic, tasks, and grading
```

---

## Tasks

### Easy (3 tasks)

**easy_001** - Fix syntax errors (missing colons, parentheses) in a `calculate_average` function. 5 tests.

**easy_002** - Fix a missing return statement and a wrong comparison operator in `find_max`. 5 tests.

**easy_003** - Fix off-by-one errors in `repeat_string` and `first_n_chars`. 5 tests.

### Medium (3 tasks)

**medium_001** - Fix logic errors in `is_palindrome` (wrong comparison) and `count_vowels` (wrong increment). Code runs but produces wrong results. 5 tests.

**medium_002** - Fix a mutable state bug in `merge_dicts` (modifies original dict) and missing deduplication in `unique_sorted`. 5 tests.

**medium_003** - Fix a wrong list operation in `flatten_list` (append instead of extend) and an off-by-one slice in `chunk_list`. 5 tests.

### Hard (2 tasks)

**hard_001** - Fix 3 interdependent bugs across `compress_stream`, `decompress_stream`, and `stream_stats`. The bugs compensate for each other, so the broken code passes all tests as-is. Fixing only 1 or 2 bugs breaks everything. All 3 must be fixed together. 6 tests.

**hard_002** - Fix 3 bugs in a data pipeline: a boundary condition error in `filter_and_sort` (> vs >=), wrong sort order (ascending vs descending), and wrong key in `summarize` (sorts by age instead of score). 6 tests.

---

## Scoring

```
score = tests_passed / total_tests
```

- Partial credit is given. Passing 3 out of 5 tests = 0.6
- If the submitted code has a syntax error or crashes, score = 0.0
- Code that runs longer than 3 seconds is killed (catches infinite loops)
- An episode ends when score reaches 1.0 or after 5 steps

---

## Action Space

What the agent sends to the environment:

| Field | Type | Description |
|-------|------|-------------|
| `fixed_code` | str | The corrected Python code |
| `task_id` | str | Which task is being solved |

## Observation Space

What the environment sends back:

| Field | Type | Description |
|-------|------|-------------|
| `broken_code` | str | The original broken code |
| `description` | str | What the task is about |
| `score` | float | 0.0 to 1.0 |
| `tests_passed` | int | How many tests passed |
| `total_tests` | int | Total test cases |
| `feedback` | str | Which tests failed and why |
| `done` | bool | Whether the episode is over |
| `difficulty` | str | easy, medium, or hard |

---

## Setup

### Prerequisites

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) (recommended) or pip

### Install dependencies

```bash
uv sync
```

Or with pip:

```bash
pip install openenv-core fastapi uvicorn openai
```

---

## Running Locally

### Step 1: Start the server

```bash
uv run server
```

Leave this running in a terminal. The server starts on port 7860.

### Step 2: Run the agent

In a separate terminal:

```bash
export HF_TOKEN=your_huggingface_token
export MODEL_NAME=meta-llama/Llama-3.1-8B-Instruct
export ENV_URL=http://localhost:7860

uv run python inference.py
```

You should see output like:

```
[START] task=easy_001 env=code-debug-env model=meta-llama/Llama-3.1-8B-Instruct
[STEP] step=1 action=fix_code reward=0.99 done=true error=null
[END] success=true steps=1 score=0.99 rewards=0.99
...
=== BASELINE SCORES ===
easy_001: 0.99
easy_002: 0.99
easy_003: 0.99
medium_001: 0.99
medium_002: 0.99
medium_003: 0.99
hard_001: 0.99
hard_002: 0.83
Average: 0.97
```

---

## Docker

### Build

```bash
docker build -t code-debug-env .
```

### Run

```bash
docker run -p 7860:7860 code-debug-env
```

The server will be available at `http://localhost:7860`.

---

## Deploy to Hugging Face Spaces

```bash
openenv push --repo-id your-username/code-debug-env
```

The Dockerfile is configured to expose port 7860, which is required by Hugging Face Spaces.

---

## Baseline Scores

Tested with `meta-llama/Llama-3.1-8B-Instruct`:

| Task | Difficulty | Score | Steps |
|------|-----------|-------|-------|
| easy_001 | Easy | 0.99 | 1 |
| easy_002 | Easy | 0.99 | 1 |
| easy_003 | Easy | 0.99 | 1 |
| medium_001 | Medium | 0.99 | 1 |
| medium_002 | Medium | 0.99 | 1 |
| medium_003 | Medium | 0.99 | 1 |
| hard_001 | Hard | 0.99 | 2 |
| hard_002 | Hard | 0.83 | 5 |
| **Average** | - | **0.97** | - |

---

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `HF_TOKEN` | Yes | - | Hugging Face API token |
| `MODEL_NAME` | Yes | - | Model to use for inference |
| `API_BASE_URL` | No | `https://router.huggingface.co/v1` | LLM API endpoint |
| `ENV_URL` | No | `http://localhost:7860` | Environment server URL |
