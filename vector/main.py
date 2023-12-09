from fastapi import FastAPI, UploadFile, File
import uvicorn
from io import BytesIO

from vector.db import store_in_milvus, MetaData
from vector.operations import convert_to_embeddings, process_pdf

app = FastAPI()


@app.post("/upload/")
async def upload_pdf(meta: MetaData, file: UploadFile = File(...)):
    pdf_file = BytesIO(await file.read())
    pdf_elements = process_pdf(pdf_file)
    embeddings = convert_to_embeddings(pdf_elements)

    store_in_milvus(embeddings, meta)

    return {"status": "Processed and stored"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
