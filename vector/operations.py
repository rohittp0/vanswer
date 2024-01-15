from io import BytesIO
from typing import List, Dict

import fitz

import torch
import torch.nn.functional as F
from PIL import Image
from tqdm import tqdm

from vector.store import EmbeddingParams, get_embedder, device, Embeds, get_image_embedder


def mean_pooling(model_output, attention_mask):
    token_embeddings = model_output[0]
    input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
    return torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(input_mask_expanded.sum(1), min=1e-9)


def generate_image_description(image: BytesIO) -> str:
    image = Image.open(image)
    processor, model = get_image_embedder()

    inputs = processor(images=image, text="What do you see in the image? The image", return_tensors="pt").to(device)

    predictions = model.generate(**inputs, max_new_tokens=3000)
    texts = processor.batch_decode(predictions, skip_special_tokens=True)
    return "\n".join(texts)


def texts_to_embeddings(text: List[str]) -> List[float]:
    tokenizer, model = get_embedder()

    encoded_input = tokenizer(text, padding=True, truncation=True, return_tensors='pt')
    encoded_input.to(device)

    with torch.no_grad():
        model_output = model(**encoded_input)

    embeddings = mean_pooling(model_output, encoded_input['attention_mask'])
    return F.normalize(embeddings, p=2, dim=0).tolist()


def elements_to_embeddings(pdf_elements: List[Embeds]) -> List[Embeds]:
    embeddings = []

    for index in tqdm(range(0, len(pdf_elements), EmbeddingParams.BATCH_SIZE.value), desc="Elements to embeddings"):
        batch = pdf_elements[index:index + EmbeddingParams.BATCH_SIZE.value]
        texts = [element["text"] for element in batch]
        texts = texts_to_embeddings(texts)

        for j, text in enumerate(texts):
            pdf_elements[index + j]["embedding"] = text

        embeddings.extend(batch)

    return embeddings


def process_pdf(file_path: str) -> List[Dict[str, str | int]]:
    # noinspection PyUnresolvedReferences
    doc = fitz.open(file_path)
    tokenizer = get_embedder()[0]

    chunks = []

    for page_num in tqdm(range(len(doc)), desc="Processing PDF"):
        page = doc.load_page(page_num)
        text = page.get_text()

        # Tokenize the text
        tokens = tokenizer.tokenize(text)

        # Split tokens into chunks
        for i in range(0, len(tokens), EmbeddingParams.CHUNK_SIZE.value):
            chunk_tokens = tokens[i:i + EmbeddingParams.CHUNK_SIZE.value]
            chunk_text = tokenizer.convert_tokens_to_string(chunk_tokens)
            chunks.append({"text": chunk_text, "index": page_num})

        # Process images on the page
        # for index, img in enumerate(page.get_images(full=True)):
        #     image_bytes = doc.extract_image(img[0])["image"]
        #     text = generate_image_description(BytesIO(image_bytes))
        #     chunks.append({"text": text, "index": page_num})

    doc.close()
    return chunks
