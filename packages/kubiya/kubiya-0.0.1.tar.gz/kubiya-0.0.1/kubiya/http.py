from operator import ge
from fastapi import FastAPI
import uvicorn
from .kubiya_integration import KubiyaIntegraion
from typing import List, Dict, Any
from uvicorn import run
from pydantic import BaseModel

from kubiya.get_env import get_env


class Request(BaseModel):
    action: str
    input: Any


def serve(integration: KubiyaIntegraion, filename=None):
    kubiya_server = FastAPI(openapi_url=None)

    @kubiya_server.get("/")
    async def root() -> Any:
        return {
            "name": integration.get_name(),
            "version": integration.get_version(),
            "registered_actions": integration.get_registered_actions(),
        }

    @kubiya_server.post("/")
    async def root(request: Request) -> Any:
        try:
            return integration.execute_action(request.action, request.input)
        except Exception as e:
            return {"error": str(e)}

    uvicorn.run(kubiya_server, host="0.0.0.0", port=8080)