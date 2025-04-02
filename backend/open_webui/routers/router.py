from fastapi import (
    Depends,
    FastAPI,
    HTTPException,
    status,
    APIRouter,
)
from pydantic import BaseModel
from typing import List, Dict, Any
import logging

from open_webui.utils.auth import get_admin_user
from open_webui.env import SRC_LOG_LEVELS
from open_webui.utils.Routers.tool_router import ToolRouter
from open_webui.utils.Routers.model_router import ModelRouter
from open_webui.utils.Routers.guardrail_router import GuardrailRouter

log = logging.getLogger(__name__)
log.setLevel(SRC_LOG_LEVELS["MAIN"])

# Update the RouterSettings class to match the actual structure used
class RouterSettings(BaseModel):
    enabled: bool = False
    classifier: str = "zero-shot-classification"
    model: str = ""
    n: int = 1
    threshold: float = 0.1

class Router(BaseModel):
    id: str
    name: str
    settings: RouterSettings

class RoutersResponse(BaseModel):
    routers: List[Router]

# Updated router database with three different routers
routers_db = [
    {
        "id": "1",
        "name": "Model Router",
        "settings": {
            "enabled": True,
            "classifier": "zero-shot-classification",
            "model": "facebook/bart-large-mnli", 
            "n": 1,
            "threshold": 0.1
        }
    },
    {
        "id": "2",
        "name": "Tool Router",
        "settings": {
            "enabled": True,
            "classifier": "zero-shot-classification",
            "model": "facebook/bart-large-mnli",
            "n": 3,
            "threshold": 0.08
        }
    },
    {
        "id": "3",
        "name": "Guardrail Router",
        "settings": {
            "enabled": True,
            "classifier": "zero-shot-classification",
            "model": "facebook/bart-large-mnli",
            "n": 1,
            "threshold": 0.169
        }
    }
]

router = APIRouter()

@router.get("/", response_model=RoutersResponse)
async def get_routers(admin_user: str = Depends(get_admin_user)):
    return {"routers": routers_db}

@router.put("/{router_id}", response_model=bool)
async def update_router_settings(router_id: str, settings: RouterSettings, admin_user: str = Depends(get_admin_user)):
    for router in routers_db:
        if router["id"] == router_id:
            router["settings"] = settings.dict()
            return True
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Router not found")

@router.post("/initialize", response_model=bool)
async def initialize_routers(admin_user: str = Depends(get_admin_user)):
    """Initialize router instances based on their settings"""
    try:
        for router in routers_db:
            if router["name"] == "Model Router":
                ModelRouter(**router["settings"].dict())
            elif router["name"] == "Tool Router":
                ToolRouter(**router["settings"].dict())
            elif router["name"] == "Guardrail Router":
                GuardrailRouter(**router["settings"].dict())
        return True
    except Exception as e:
        log.error(f"Error initializing routers: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error initializing routers")