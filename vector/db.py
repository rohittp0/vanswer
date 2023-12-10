from typing import List

from pydantic import BaseModel
from pymilvus import utility, Collection, CollectionSchema, FieldSchema, DataType, connections

from store import ElementType, EmbeddingParams, META_DATA_COLLECTION, EMBEDDINGS_COLLECTION


class MetaData(BaseModel):
    name: str
    language: str
    type: str
    tags: list
    states: List[str]
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

        assert len(data['text']) <= EmbeddingParams.CHUNK_SIZE.value

        super().__init__(**data)

    def db_dict(self, meta_id):
        return {**self.model_dump(exclude={'text'}), "meta_id": meta_id, "type": self.type.value}


def get_or_create_meta_data_collection():
    if utility.has_collection(META_DATA_COLLECTION):
        return Collection(name=META_DATA_COLLECTION)

    schema = CollectionSchema(
        fields=[
            FieldSchema("id", DataType.INT64, is_primary=True, auto_id=True),
            FieldSchema("name", DataType.VARCHAR, max_length=256, default=""),
            FieldSchema("language", DataType.VARCHAR, max_length=256, default=""),
            FieldSchema("type", DataType.VARCHAR, max_length=256, default="Other"),
            FieldSchema("tags", DataType.ARRAY, element_type=DataType.VARCHAR, max_capacity=50, max_length=64),
            FieldSchema("states", DataType.ARRAY, element_type=DataType.VARCHAR, max_capacity=32, max_length=64),
            FieldSchema("description", DataType.FLOAT_VECTOR, dim=EmbeddingParams.DIMENSION.value),
            FieldSchema("organization", DataType.VARCHAR, max_length=256, default="")
        ],
        description="PDF metadata"
    )

    collection = Collection(name=META_DATA_COLLECTION, schema=schema)

    index_param = {"metric_type": "IP", "index_type": "GPU_IVF_FLAT", "params": {"nlist": 128}}

    collection.create_index(field_name="description", index_params=index_param)
    collection.create_index(field_name="id", index_name="id_index")
    collection.create_index(field_name="type", index_name="type_index")

    return collection


def get_or_create_embeddings_collection():
    if utility.has_collection(EMBEDDINGS_COLLECTION):
        return Collection(name=EMBEDDINGS_COLLECTION)

    schema = CollectionSchema(
        fields=[
            FieldSchema("id", DataType.INT64, is_primary=True, auto_id=True),
            FieldSchema("embedding", DataType.FLOAT_VECTOR, dim=EmbeddingParams.DIMENSION.value),
            FieldSchema("index", DataType.INT16),
            FieldSchema("offset", DataType.INT16, default=-1),
            FieldSchema("type", DataType.INT8, description="text-0, image-1, etc."),
            FieldSchema("meta_id", DataType.INT64)
        ],
        description="PDF documents"
    )

    collection = Collection(name=EMBEDDINGS_COLLECTION, schema=schema)
    index_param = {"metric_type": "IP", "index_type": "GPU_IVF_FLAT", "params": {"nlist": 128}}

    collection.create_index(field_name="embedding", index_params=index_param)
    collection.create_index(field_name="meta_id", index_name="meta_id_index")
    collection.create_index(field_name="type", index_name="type_index")

    return collection


def get_or_create_collections():
    connections.connect("default", host="localhost", port="19530")
    meta = get_or_create_meta_data_collection()
    embeddings = get_or_create_embeddings_collection()

    return meta, embeddings


def store_in_milvus(embeddings: List[Embedding], meta: MetaData):
    meta_collection, embedding_collection = get_or_create_collections()

    key = meta_collection.insert(meta.model_dump()).primary_keys[0]

    # Prepare records for insertion
    records = []
    for embedding in embeddings:
        records.append(embedding.db_dict(key))

        if len(records) > 40:
            embedding_collection.insert(records)
            records = []

    if len(records) > 0:
        embedding_collection.insert(records)

    return key
