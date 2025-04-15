from fastapi import FastAPI

from controllers import baseController, dataController, nlpController
from helpers.config import get_settings
from stores.vectordb.VectorDBProviderFactory import VectorDBProviderFactory
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from stores.llm.LLMProviderFactory import LLMProviderFactory
from stores.llm.templates.template_parser import TemplateParser
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

    llm_provider_factory = LLMProviderFactory(settings)
    vectordb_provider_factory = VectorDBProviderFactory(settings)

    # generation client
    app.generation_client = llm_provider_factory.create(provider=settings.GENERATION_BACKEND)
    app.generation_client.set_generation_model(model_id = settings.GENERATION_MODEL_ID)

    # embedding client
    app.embedding_client = llm_provider_factory.create(provider=settings.EMBEDDING_BACKEND)
    app.embedding_client.set_embedding_model(model_id=settings.EMBEDDING_MODEL_ID,
                                             embedding_size=settings.EMBEDDING_MODEL_SIZE)
    
    # vector db client
    app.vectordb_client = vectordb_provider_factory.create(
        provider=settings.VECTOR_DB_BACKEND
    )
    app.vectordb_client.connect()
    

    app.template_parser = TemplateParser(
        language=settings.PRIMARY_LANG,
        default_language=settings.DEFAULT_LANG
    )

async def shutdown_span():
    app.db_engine
    app.vectordb_client.disconnect()

app.on_event("startup")(startup_span)
app.on_event("shutdown")(shutdown_span)  

app.include_router(baseController.base_router)
app.include_router(dataController.data_router)
app.include_router(nlpController.nlp_router)