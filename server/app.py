from openenv.core.env_server import create_fastapi_app

from models import CodeDebugAction, CodeDebugObservation
from server.environment import CodeDebugEnvironment

app = create_fastapi_app(
    CodeDebugEnvironment,
    CodeDebugAction,
    CodeDebugObservation,
)
