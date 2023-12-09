import uuid
from typing import List

from pydantic import BaseModel
from pymilvus import utility, Collection, CollectionSchema, FieldSchema, DataType

from store import ElementType, EmbeddingParams, get_milvus, MILVUS_COLLECTION


class MetaData(BaseModel):
    name: str
    language: str
    type: str
    tags: list
    state: str
    description: str | List[float]
    organization: str


class Embedding(BaseModel):
    embedding: List[float]
    index: int
    offset: int
    text: str
    type: ElementType

    def __init__(self, **data):
        data['type'] = data['type'].value

        if 'embedding' in data:
            assert len(data['embedding']) == EmbeddingParams.DIMENSION.value
        else:
            data['embedding'] = [0] * EmbeddingParams.DIMENSION.value

        super().__init__(**data)


def get_or_create_collection():
    if utility.has_collection(MILVUS_COLLECTION):
        return Collection(name=MILVUS_COLLECTION)

    schema = CollectionSchema(
        fields=[
            FieldSchema("id", DataType.INT64, is_primary=True, auto_id=True),
            FieldSchema("name", DataType.VARCHAR, max_length=256, default=""),
            FieldSchema("language", DataType.VARCHAR, max_length=256, default=""),
            FieldSchema("type", DataType.VARCHAR, max_length=256, default="Other"),
            FieldSchema("tags", DataType.ARRAY, element_type=DataType.VARCHAR, max_capacity=50),
            FieldSchema("state", DataType.VARCHAR, max_length=64, default=""),
            FieldSchema("description", DataType.FLOAT_VECTOR, dim=EmbeddingParams.DIMENSION.value),
            FieldSchema("organization", DataType.VARCHAR, max_length=256, default=""),
            FieldSchema("embedding", DataType.FLOAT_VECTOR, dim=EmbeddingParams.DIMENSION.value),
            FieldSchema("index", DataType.INT16),
            FieldSchema("offset", DataType.INT16, default=-1),
            FieldSchema("text", DataType.VARCHAR, max_length=EmbeddingParams.CHUNK_SIZE.value),
            FieldSchema("chunk_type", DataType.INT8),
            FieldSchema("file_id", DataType.VARCHAR, max_length=36),
        ],
        description="PDF documents"
    )

    collection = Collection(name=MILVUS_COLLECTION, schema=schema)
    index_param = {"metric_type": "IP", "index_type": "GPU_IVF_FLAT", "params": {"nlist": 128}}

    collection.create_index(field_name="embedding", index_params=index_param)
    collection.create_index(field_name="description", index_params=index_param)
    collection.create_index(field_name="file_id", index_name="file_id_index")
    collection.create_index(field_name="type", index_name="type_index")

    return collection


def store_in_milvus(embeddings: List[Embedding], meta: MetaData):
    collection = get_or_create_collection()
    file_id = str(uuid.uuid4())  # Generate a unique ID for each file

    # Prepare records for insertion
    records = []
    for embedding in embeddings:
        record = {**embedding, **meta, "file_id": file_id, "chunk_type": embedding.type.value}
        records.append(record)

    # Insert records into the collection
    collection.insert([records])

    return file_id


