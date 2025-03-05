from fastapi import FastAPI

from controllers import baseController, dataController
from helpers.config import get_settings
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from helpers.config import get_settings



app = FastAPI()

async def startup_span():
    settings = get_settings()

    postgres_conn = f"postgresql+asyncpg://{settings.POSTGRES_USERNAME}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_MAIN_DATABASE}"
    app.db_engine = create_async_engine(postgres_conn)
    app.db_client = sessionmaker(
        app.db_engine, class_=AsyncSession, expire_on_commit=False
    )

async def shutdown_span():
    app.db_engine

app.on_event("startup")(startup_span)
app.on_event("shutdown")(shutdown_span)  

app.include_router(baseController.base_router)
app.include_router(dataController.data_router)