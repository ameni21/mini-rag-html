from enum import Enum

class VectorDBEnums(Enum):
    PGVECTOR = "PGVECTOR"
    QDRANT = "QDRANT"

class DistanceMethodEnums(Enum):
    COSINE = "cosine"
    DOT = "dot"