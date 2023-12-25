import json
from typing import Annotated

from fastapi import FastAPI, Form, File
import uvicorn
from io import BytesIO

from pymilvus import Collection

from db import store_in_milvus, MetaData, get_or_create_embeddings_collection, get_or_create_meta_data_collection
from operations import elements_to_embeddings, process_pdf, texts_to_embeddings
from store import EMBEDDINGS_COLLECTION, META_DATA_COLLECTION

app = FastAPI()


def search(collection, query, limit, expr, output_fields, search_filed, iterables):
    search_params = {
        "metric_type": "IP",
        "params": {"nlist": 128}
    }

    collection = Collection(collection)
    collection.load()

    vector = texts_to_embeddings([query])

    results = collection.search(
        data=vector,
        anns_field=search_filed,
        param=search_params,
        limit=limit,
        output_fields=output_fields,
        expr=expr
    )
    rets = []

    for result in results[0]:
        ret = {}
        for key, value in result.entity.fields.items():
            ret[key] = list(value) if key in iterables else value

        rets.append(ret)

    # Convert to dictionary
    return rets


@app.post("/upload/")
async def upload_pdf(file: Annotated[bytes, File()], meta: Annotated[str, Form()]):
    try:
        pdf_elements = process_pdf(BytesIO(file))
        embeddings = elements_to_embeddings(pdf_elements)

        meta = MetaData(**json.loads(meta))

        key = store_in_milvus(embeddings, meta)
        return {"key": key, "status": "success"}

    except Exception as e:
        return {"error": str(e), "status": "failed"}


@app.get("/search/elements/")
async def search_elements(query: str, limit: int = 10, expr: str = None):
    get_or_create_embeddings_collection()

    return search(
        collection=EMBEDDINGS_COLLECTION,
        query=query,
        limit=limit,
        expr=expr,
        output_fields=["id", "meta_id", "type", "offset", "index"],
        search_filed="embedding",
        iterables=[],
    )


@app.get("/search/meta/")
async def search_meta(query: str, limit: int = 10, expr: str = None):
    get_or_create_meta_data_collection()

    return search(
        collection=META_DATA_COLLECTION,
        query=query,
        limit=limit,
        expr=expr,
        output_fields=["id", "name", "language", "type", "tags", "states", "organization"],
        search_filed="description",
        iterables=["tags", "states"],
    )


@app.get("/health/")
async def health():
    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="localhost", port=4000, reload=True)
