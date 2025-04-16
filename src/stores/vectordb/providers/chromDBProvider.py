#from chromadb import PersistentClient
from ..VectorDBInterface import VectorDBInterface
import logging
from typing import List
from models.db_schemes import RetrievedDocument

class ChromaDBProvider(VectorDBInterface):
    def __init__(self, db_client: str, default_vector_size: int = 786):
        #self.client = PersistentClient(path=db_client)
        self.default_vector_size = default_vector_size
        self.logger = logging.getLogger('uvicorn')

    async def connect(self):
        pass  # PersistentClient auto-connects

    async def disconnect(self):
        self.client = None

    def is_collection_existed(self, collection_name: str) -> bool:
        return any(c.name == collection_name for c in self.client.list_collections())

    async def list_all_collections(self) -> List:
        return [c.name for c in self.client.list_collections()]

    def get_collection_info(self, collection_name: str) -> dict:
        collection = self.client.get_collection(collection_name)
        return {"name": collection.name}

    async def delete_collection(self, collection_name: str):
        self.client.delete_collection(name=collection_name)

    async def create_collection(self, collection_name: str, embedding_size: int, do_reset: bool = False):
        if do_reset:
            await self.delete_collection(collection_name)
        if not self.is_collection_existed(collection_name):
            self.client.create_collection(name=collection_name)

    async def insert_one(self, collection_name: str, text: str, vector: list,
                         metadata: dict = None, record_id: str = None):
        try:
            col = self.client.get_or_create_collection(name=collection_name)
            col.add(documents=[text], embeddings=[vector], metadatas=[metadata], ids=[record_id])
            return True
        except Exception as e:
            self.logger.error(f"Insert error: {e}")
            return False

    async def insert_many(self, collection_name: str, texts: list, vectors: list,
                          metadata: list = None, record_ids: list = None, batch_size: int = 50):
        if metadata is None:
            metadata = [{} for _ in texts]
        if record_ids is None:
            record_ids = [str(i) for i in range(len(texts))]

        col = self.client.get_or_create_collection(name=collection_name)

        try:
            col.add(documents=texts, embeddings=vectors,
                    metadatas=metadata, ids=record_ids)
            return True
        except Exception as e:
            self.logger.error(f"Insert many error: {e}")
            return False

    async def search_by_vector(self, collection_name: str, vector: list, limit: int = 5):
        col = self.client.get_collection(name=collection_name)
        result = col.query(query_embeddings=[vector], n_results=limit)
        return [
            RetrievedDocument(score=score, text=text)
            for score, text in zip(result['distances'][0], result['documents'][0])
        ]
