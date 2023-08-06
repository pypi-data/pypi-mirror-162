from operator import ge
from fastapi import FastAPI
import uvicorn
from .actions_store import ActionsStore
from typing import List, Dict, Any
from uvicorn import run
from pydantic import BaseModel

class Request(BaseModel):
    action: str
    input: Any


def serve(actions_store: ActionsStore, filename=None):
    kubiya_server = FastAPI(openapi_url=None)

    @kubiya_server.get("/")
    async def root() -> Any:
        return {
            "name": actions_store.get_name(),
            "version": actions_store.get_version(),
            "registered_actions": actions_store.get_registered_actions(),
        }

    @kubiya_server.post("/")
    async def root(request: Request) -> Any:
        try:
            return actions_store.execute_action(request.action, request.input)
        except Exception as e:
            return {"error": str(e)}

    uvicorn.run(kubiya_server, host="0.0.0.0", port=8080)
