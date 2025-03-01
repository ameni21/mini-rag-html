from fastapi import  APIRouter, Depends
from controllers.baseController import BaseController
from helpers.config import get_settings, Settings


base_router = APIRouter(
    prefix="/api/v1",
    tags= ["api_v1"],
)

@base_router.get("/")
async def welcome(app_settings: Settings = Depends(get_settings)):
    return await BaseController().welcome(app_settings)

    
    