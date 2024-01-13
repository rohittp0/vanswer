from enum import Enum
from typing import List, Dict

import torch
from transformers import AutoTokenizer, AutoModel


class EmbeddingParams(Enum):
    MODEL = 'sentence-transformers/all-MiniLM-L6-v2'
    TOKENIZER = 'sentence-transformers/all-MiniLM-L6-v2'
    CHUNK_SIZE = 512
    BATCH_SIZE = 8
    DIMENSION = 384


device = 'cuda' if torch.cuda.is_available() else 'cpu'
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


Embeds = List[Dict[str, str | float]]
