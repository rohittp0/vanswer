import csv
import os
import pickle
from io import BytesIO
from typing import List

from tqdm import tqdm

from db import MetaData, Embedding, store_in_milvus, get_or_create_collections
from operations import process_pdf, elements_to_embeddings, texts_to_embeddings

save_dir = '../res/embeddings'


def read_csv_and_create_meta_data(file_path):
    meta_data_list = []

    with open(file_path, 'r') as f:
        reader = csv.reader(f)
        next(reader)  # Skip the header row

        for row in reader:
            path = os.path.join("../res", row[1])
            meta_data = MetaData(
                name=row[0],
                language=row[2],
                type=row[3],
                tags=[t.strip()[:64] for t in row[4].split(',')],
                state=[t.strip()[:64] for t in row[5].split(',')],
                description=row[6],
                organization=row[9]
            )
            meta_data_list.append((path, meta_data))

    return meta_data_list


def save_data_to_file_with_pickle(meta: MetaData, embeddings: List[Embedding], output_file: str):
    with open(output_file, 'wb') as f:
        pickle.dump({'meta': meta, 'embeddings': embeddings}, f)


def load_data_from_file_with_pickle(file_path: str) -> (MetaData, List[Embedding]):
    with open(file_path, 'rb') as f:
        data = pickle.load(f)
    return data['meta'], data['embeddings']


def main():
    metas = read_csv_and_create_meta_data('../res/paths.csv')

    # Create save directory
    os.makedirs(save_dir, exist_ok=True)
    i = 0

    for path, meta in tqdm(metas):
        save = os.path.join(save_dir, f'{i}.pkl')

        if os.path.exists(save):
            i += 1
            continue

        try:
            with open(path, 'rb') as f:
                pdf = BytesIO(f.read())
                elements = process_pdf(pdf)
                embeds = elements_to_embeddings(elements)

            if isinstance(meta.description, str):
                meta.description = texts_to_embeddings([meta.description])[0]
            else:
                raise ValueError("Description is not a string")
        except Exception as e:
            print(f"Error processing {path}")
            print(e)
            continue

        save_data_to_file_with_pickle(meta, embeds, save)
        i += 1


def save_to_db():
    for i in tqdm(range(len(os.listdir(save_dir)))):
        file_path = os.path.join(save_dir, f'{i}.pkl')
        meta, embeddings = load_data_from_file_with_pickle(file_path)

        if "state" in {**meta.__dict__}:
            meta.states = [t[:64] for t in meta.state.split(',')]
            del meta.state

        store_in_milvus(embeddings, meta)

    meta_collection, embed_collection = get_or_create_collections()
    meta_collection.flush()
    embed_collection.flush()


if __name__ == '__main__':
    save_to_db()
