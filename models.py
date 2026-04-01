from typing import Any, Dict

from openenv.core.env_server import Action, Observation, State


class CodeDebugAction(Action):
    fixed_code: str = ""
    task_id: str = ""


class CodeDebugObservation(Observation):
    task_id: str = ""
    difficulty: str = ""
    broken_code: str = ""
    description: str = ""
    score: float = 0.0
    tests_passed: int = 0
    total_tests: int = 0
    feedback: str = ""


class CodeDebugState(State):
    current_task_id: str = ""
    difficulty: str = ""
