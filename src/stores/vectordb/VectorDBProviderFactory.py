from services.BaseService import BaseService
from stores.vectordb.providers.QdrantDBProvider import QdrantDBProvider
from stores.vectordb.providers.chromDBProvider import ChromaDBProvider
from .VectorDBEnums import VectorDBEnums
from sqlalchemy.orm import sessionmaker


class VectorDBProviderFactory:
    def __init__(self,   config, db_client: sessionmaker=None):
        self.config = config
        self.base_service= BaseService()
        self.db_client = db_client
        
        

    def create(self, provider: str):
                
        if provider == VectorDBEnums.QDRANT.value:
            qdrant_db_client = self.base_service.get_database_path(db_name=self.config.VECTOR_DB_PATH)

            return QdrantDBProvider(
                db_client=qdrant_db_client,
                distance_method=self.config.VECTOR_DB_DISTANCE_METHOD,
                default_vector_size=self.config.EMBEDDING_MODEL_SIZE,
                index_threshold=self.config.VECTOR_DB_PGVEC_INDEX_THRESHOLD,
            )
        if provider == VectorDBEnums.CHROMADB.value:
            chroma_db_client = self.base_service.get_database_path(db_name=self.config.VECTOR_DB_PATH)
            return ChromaDBProvider(
                db_client=chroma_db_client,
                default_vector_size=self.config.EMBEDDING_MODEL_SIZE,
            )

        return None
