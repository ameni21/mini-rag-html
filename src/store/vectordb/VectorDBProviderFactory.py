from .providers import PgvectorDBProvider
from .VectorDBEnums import VectorDBEnums
from  services.BaseService import BaseService

class VectorDBProviderFactory:
    def __init__(self, config):
        self.config = config
        self.base_service= BaseService()

    def create(self, provider: str):
        if provider == VectorDBEnums.PGVECTOR.value:
            db_path = self.base_service.get_database_path(db_name=self.config.VECTOR_DB_PATH)

            return PgvectorDBProvider(
                db_path=db_path,
                distance_method=self.config.VECTOR_DB_DISTANCE_METHOD,
            )
        
        return None