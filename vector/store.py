from enum import Enum

import torch
from pymilvus import Milvus, connections
from transformers import AutoTokenizer, AutoModel


class ElementType(Enum):
    IMAGE = 0
    TEXT = 1


class EmbeddingParams(Enum):
    MODEL = 'jinaai/jina-embeddings-v2-base-en'
    TOKENIZER = 'jinaai/jina-embeddings-v2-base-en'
    CHUNK_SIZE = 8000
    BATCH_SIZE = 1
    DIMENSION = 768


MILVUS_HOST = 'localhost'
MILVUS_PORT = 19530
META_DATA_COLLECTION = 'pdf_metadata'
EMBEDDINGS_COLLECTION = 'pdf_embeddings'

device = 'cuda' if torch.cuda.is_available() else 'cpu'
connections.connect("default", host="localhost", port="19530")

embedder = None


def get_embedder():
    global embedder
    if embedder is None:
        embedder = (
            AutoTokenizer.from_pretrained(EmbeddingParams.TOKENIZER.value),
            AutoModel.from_pretrained(EmbeddingParams.MODEL.value, trust_remote_code=True)
        )

        embedder[1].to(device)
        embedder[1].eval()

    return embedder
