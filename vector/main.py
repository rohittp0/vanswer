from fastapi import FastAPI, UploadFile, File
import uvicorn
from io import BytesIO

from pymilvus import Collection

from vector.db import store_in_milvus, MetaData
from vector.operations import elements_to_embeddings, process_pdf, texts_to_embeddings
from vector.store import EMBEDDINGS_COLLECTION, META_DATA_COLLECTION

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
async def upload_pdf(meta: MetaData, file: UploadFile = File(...)):
    pdf_file = BytesIO(await file.read())
    pdf_elements = process_pdf(pdf_file)
    embeddings = elements_to_embeddings(pdf_elements)

    key = store_in_milvus(embeddings, meta)

    return {"key": key}


@app.get("/search/elements/")
async def search_elements(query: str, limit: int = 10, expr: str = None):
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
    return search(
        collection=META_DATA_COLLECTION,
        query=query,
        limit=limit,
        expr=expr,
        output_fields=["id", "name", "language", "type", "tags", "states", "organization"],
        search_filed="description",
        iterables=["tags", "states"],
    )


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
