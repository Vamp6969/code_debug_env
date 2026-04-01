from openenv.core.env_server import create_fastapi_app

from models import CodeDebugAction, CodeDebugObservation
from server.environment import CodeDebugEnvironment

app = create_fastapi_app(
    CodeDebugEnvironment,
    CodeDebugAction,
    CodeDebugObservation,
)

import uvicorn

def main():
    uvicorn.run(app, host="0.0.0.0", port=7860)

if __name__ == '__main__':
    main()
