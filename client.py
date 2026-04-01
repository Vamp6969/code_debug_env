from typing import Any, Dict

from openenv.core.client_types import StepResult
from openenv.core.env_client import EnvClient

from models import CodeDebugAction, CodeDebugObservation, CodeDebugState


class CodeDebugEnv(EnvClient[CodeDebugAction, CodeDebugObservation, CodeDebugState]):
    def _step_payload(self, action: CodeDebugAction) -> Dict[str, Any]:
        return {"fixed_code": action.fixed_code, "task_id": action.task_id}

    def _parse_result(self, payload: Dict[str, Any]) -> StepResult[CodeDebugObservation]:
        obs_data = payload.get("observation", {})
        obs = CodeDebugObservation(**obs_data)
        return StepResult(
            observation=obs,
            reward=payload.get("reward"),
            done=payload.get("done", False),
        )

    def _parse_state(self, payload: Dict[str, Any]) -> CodeDebugState:
        return CodeDebugState(**payload)
