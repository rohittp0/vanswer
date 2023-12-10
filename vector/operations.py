from io import BytesIO
from typing import List

import fitz
from PIL import Image

import torch
import torch.nn.functional as F

from store import EmbeddingParams, ElementType, get_embedder, device
from db import Embedding


def mean_pooling(model_output, attention_mask):
    token_embeddings = model_output[0]
    input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
    return torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(input_mask_expanded.sum(1), min=1e-9)


def generate_image_description(image: BytesIO) -> str:
    # Process the image
    # image = Image.open(image)
    # model = Pix2StructForConditionalGeneration.from_pretrained("google/pix2struct-ai2d-base")
    # processor = Pix2StructProcessor.from_pretrained("google/pix2struct-ai2d-base")
    #
    # inputs = processor(images=image, return_tensors="pt")
    #
    # predictions = model.generate(**inputs, max_new_tokens=3000)
    # texts = processor.batch_decode(predictions, skip_special_tokens=True)
    # return "\n".join(texts)[:8000]
    return ""


def texts_to_embeddings(text: List[str]) -> List[float]:
    tokenizer, model = get_embedder()

    encoded_input = tokenizer(text, padding=True, truncation=True, return_tensors='pt')
    encoded_input.to(device)

    with torch.no_grad():
        model_output = model(**encoded_input)

    embeddings = mean_pooling(model_output, encoded_input['attention_mask'])
    return F.normalize(embeddings, p=2, dim=0).tolist()


def elements_to_embeddings(pdf_elements: List[Embedding]) -> List[Embedding]:
    embeddings = []

    for index in range(0, len(pdf_elements), EmbeddingParams.BATCH_SIZE.value):
        batch = pdf_elements[index:index + EmbeddingParams.BATCH_SIZE.value]
        texts = [element.text for element in batch]
        texts = texts_to_embeddings(texts)

        for j, text in enumerate(texts):
            pdf_elements[index + j].embedding = text

        embeddings.extend(batch)

    return embeddings


def process_pdf(pdf_file: BytesIO) -> List[Embedding]:
    doc = fitz.open(stream=pdf_file, filetype="pdf")
    chunks = []
    current_chunk = ''
    start_page = None
    end_page = None

    for page_num in range(len(doc)):
        page = doc.load_page(page_num)

        # Extract text
        text = page.get_text()
        if start_page is None:
            start_page = page_num

        if len(current_chunk) + len(text) <= EmbeddingParams.CHUNK_SIZE.value:
            current_chunk += text
            end_page = page_num
        else:
            current_chunk = current_chunk[:EmbeddingParams.CHUNK_SIZE.value]
            embedding = Embedding(type=ElementType.TEXT, index=start_page,
                                  offset=end_page - start_page, text=current_chunk)
            chunks.append(embedding)
            current_chunk, start_page, end_page = text, page_num, page_num

        for index, img in enumerate(page.get_images(full=True)):
            xref = img[0]
            image_bytes = doc.extract_image(xref)["image"]
            text = generate_image_description(BytesIO(image_bytes))
            embedding = Embedding(type=ElementType.IMAGE, index=page_num, offset=index, text=text)
            chunks.append(embedding)

    if current_chunk:
        embedding = Embedding(type=ElementType.TEXT, index=start_page, offset=end_page - start_page,
                              text=current_chunk)
        chunks.append(embedding)

    doc.close()
    return chunks
