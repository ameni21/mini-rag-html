from fastapi import FastAPI, APIRouter, Depends
import os 
from helpers.config import get_settings, Settings

class BaseController:

    async def welcome(self, app_settings: Settings):
        
        self.app_name = app_settings.APP_NAME
        self.app_version = app_settings.APP_VERSION

        return {
            "app_name": self.app_name,
            "app_version": self.app_version,
        }