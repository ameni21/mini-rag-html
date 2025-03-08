import psycopg2
import logging
from typing import List
from ..VectorDBInterface import VectorDBInterface
from ..VectorDBEnums import DistanceMethodEnums
from models.db_schemes import RetrievedDocument

class PgVectorDBProvider(VectorDBInterface):
    def __init__(self, db_config: dict, distance_method: str):
        self.conn = None
        self.db_config = db_config
        self.distance_method = distance_method  # Distance method not needed for pgvector
        self.logger = logging.getLogger(__name__)
    
    def connect(self):
        try:
            self.conn = psycopg2.connect(**self.db_config)
            self.logger.info("Connected to PostgreSQL with pgvector.")
        except Exception as e:
            self.logger.error(f"Connection failed: {e}")
            raise
    
    def disconnect(self):
        if self.conn:
            self.conn.close()
            self.conn = None
            self.logger.info("Disconnected from PostgreSQL.")
    
    def is_collection_existed(self, collection_name: str) -> bool:
        with self.conn.cursor() as cur:
            cur.execute("SELECT to_regclass(%s)", (collection_name,))
            return cur.fetchone()[0] is not None
    
    def list_all_collections(self) -> List:
        with self.conn.cursor() as cur:
            cur.execute("SELECT tablename FROM pg_tables WHERE schemaname='public'")
            return [row[0] for row in cur.fetchall()]
    
    def get_collection_info(self, collection_name: str) -> dict:
        return {"exists": self.is_collection_existed(collection_name)}
    
    def delete_collection(self, collection_name: str):
        with self.conn.cursor() as cur:
            cur.execute(f"DROP TABLE IF EXISTS {collection_name}")
            self.conn.commit()
    
    def create_collection(self, collection_name: str, embedding_size: int, do_reset: bool = False):
        if do_reset:
            self.delete_collection(collection_name)
        
        with self.conn.cursor() as cur:
            cur.execute(f'''
                CREATE TABLE IF NOT EXISTS {collection_name} (
                    id SERIAL PRIMARY KEY,
                    text TEXT NOT NULL,
                    embedding VECTOR({embedding_size}),
                    metadata JSONB
                )
            ''')
            self.conn.commit()
        return True
    
    def insert_one(self, collection_name: str, text: str, vector: list, metadata: dict = None, record_id: str = None):
        with self.conn.cursor() as cur:
            cur.execute(f'''
                INSERT INTO {collection_name} (text, embedding, metadata) VALUES (%s, %s, %s)
            ''', (text, vector, metadata))
            self.conn.commit()
        return True
    
    def insert_many(self, collection_name: str, texts: list, vectors: list, metadata: list = None, batch_size: int = 50):
        if metadata is None:
            metadata = [None] * len(texts)
        
        with self.conn.cursor() as cur:
            for i in range(0, len(texts), batch_size):
                batch_texts = texts[i:i+batch_size]
                batch_vectors = vectors[i:i+batch_size]
                batch_metadata = metadata[i:i+batch_size]
                
                args = [(t, v, m) for t, v, m in zip(batch_texts, batch_vectors, batch_metadata)]
                query = f'INSERT INTO {collection_name} (text, embedding, metadata) VALUES %s'
                psycopg2.extras.execute_values(cur, query, args)
            self.conn.commit()
        return True
    
    def search_by_vector(self, collection_name: str, vector: list, limit: int = 5):
        with self.conn.cursor() as cur:
            cur.execute(f'''
                SELECT text, 1 - (embedding <=> %s) AS similarity
                FROM {collection_name}
                ORDER BY similarity DESC
                LIMIT %s
            ''', (vector, limit))
            results = cur.fetchall()
        
        if not results:
            return None
        
        return [RetrievedDocument(score=row[1], text=row[0]) for row in results]
