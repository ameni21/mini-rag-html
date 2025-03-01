from fastapi import FastAPI
import routes

from helpers.config import get_settings



app = FastAPI()

app.include_router(routes.base_router)