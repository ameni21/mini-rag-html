from services.BaseService import BaseService
from stores.vectordb.providers.PgvectorDBProvider import PgVectorDBProvider
from stores.vectordb.providers.QdrantDBProvider import QdrantDBProvider
from .VectorDBEnums import VectorDBEnums


class VectorDBProviderFactory:
    def __init__(self,   config,):
        self.config = config
        self.base_service= BaseService()
        
        

    def create(self, provider: str):
        if provider == VectorDBEnums.PGVECTOR.value:
        
            
            return PgVectorDBProvider(
                self.path,
                distance_method="cosine",
            )
        
        if provider == VectorDBEnums.QDRANT.value:
            db_path = self.base_service.get_database_path(db_name=self.config.VECTOR_DB_PATH)

            return QdrantDBProvider(
                db_path=db_path,
                distance_method=self.config.VECTOR_DB_DISTANCE_METHOD,
            )

        return None
