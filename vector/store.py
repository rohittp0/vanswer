from enum import Enum

import torch
from pymilvus import Milvus
from transformers import AutoTokenizer, AutoModel


class ElementType(Enum):
    IMAGE = 0
    TEXT = 1


class EmbeddingParams(Enum):
    MODEL = 'jinaai/jina-embeddings-v2-base-en'
    TOKENIZER = 'jinaai/jina-embeddings-v2-base-en'
    CHUNK_SIZE = 8000
    BATCH_SIZE = 8
    DIMENSION = 768


MILVUS_HOST = 'localhost'
MILVUS_PORT = 19530
MILVUS_COLLECTION = 'pdf'

device = 'cuda' if torch.cuda.is_available() else 'cpu'
embedder = None
milvus = None


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


def get_milvus():
    global milvus
    if milvus is None:
        milvus = Milvus(host=MILVUS_HOST, port=MILVUS_PORT)

    return milvus
