from typing import List

from pydantic import BaseModel

from vector.store import ElementType


class MetaData(BaseModel):
    name: str
    language: str
    type: str
    tags: list
    state: str
    description: str
    organization: str


class Embedding(BaseModel):
    embedding: list
    index: int
    offset: int
    text: str
    type: ElementType

    def __init__(self, **data):
        data['type'] = data['type'].value
        data['embedding'] = data['embedding'] if 'embedding' in data else []
        super().__init__(**data)


def get_or_create_collection():
    pass


def store_in_milvus(embeddings: List[Embedding], references: MetaData):
    collection = get_or_create_collection()
