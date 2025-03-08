from enum import Enum

class VectorDBEnums(Enum):
    PGVECTOR = "pgvector"

class DistanceMethodEnums(Enum):
    COSINE = "cosine"
    DOT = "dot"