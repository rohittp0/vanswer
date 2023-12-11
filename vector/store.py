import os
from enum import Enum

import torch
from pymilvus import connections
from transformers import AutoTokenizer, AutoModel


class ElementType(Enum):
    IMAGE = 0
    TEXT = 1


class EmbeddingParams(Enum):
    MODEL = 'sentence-transformers/all-MiniLM-L6-v2'
    TOKENIZER = 'sentence-transformers/all-MiniLM-L6-v2'
    CHUNK_SIZE = 512
    BATCH_SIZE = 8
    DIMENSION = 384


MILVUS_HOST = os.getenv('MILVUS_HOST', 'localhost')
MILVUS_PORT = os.getenv('MILVUS_PORT', '19530')
META_DATA_COLLECTION = 'pdf_metadata'
EMBEDDINGS_COLLECTION = 'pdf_embeddings'

device = 'cuda' if torch.cuda.is_available() else 'cpu'
connections.connect("default", host=MILVUS_HOST, port=MILVUS_PORT)

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
