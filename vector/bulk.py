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
    relative_path = os.path.dirname(file_path)

    with open(file_path, 'r') as f:
        reader = csv.reader(f)
        next(reader)  # Skip the header row

        for row in reader:
            path = os.path.join(relative_path, row[1])
            meta_data = MetaData(
                name=row[0],
                language=row[2],
                type=row[3],
                tags=[t.strip()[:64] for t in row[4].split(',')],
                states=[t.strip()[:64] for t in row[5].split(',')],
                description=row[6],
                organization=row[9]
            )
            meta_data_list.append((path, meta_data))

    return meta_data_list


def main():
    metas = read_csv_and_create_meta_data('../res/paths.csv')

    # Create save directory
    os.makedirs(save_dir, exist_ok=True)

    for path, meta in tqdm(metas, "Processing PDFs, creating embeddings"):
        save = os.path.join(save_dir, f'{os.path.basename(path)}.pkl')

        if os.path.exists(save):
            continue

        try:
            with open(path, 'rb') as f:
                pdf = BytesIO(f.read())
                elements = process_pdf(pdf)

            embeds = elements_to_embeddings(elements)
            description = meta.description

            assert isinstance(description, str)

            meta.description = texts_to_embeddings([description])[0]

            with open(save, 'wb') as f:
                pickle.dump({
                    'meta': meta, 'embeddings': embeds, "description": description, 'path': path
                }, f)
        except Exception as e:
            print(f"Error processing {path}")
            print(e)
            raise e


def save_to_db(clean=False):
    results = []

    meta_collection, embed_collection = get_or_create_collections()

    if clean:
        meta_collection.drop()
        embed_collection.drop()
        meta_collection, embed_collection = get_or_create_collections()

    inserted = set()

    for file_path in tqdm(os.listdir(save_dir), "Inserting to DB"):
        with open(os.path.join(save_dir, file_path), 'rb') as f:
            data = pickle.load(f)

        if data["path"] in inserted:
            continue

        inserted.add(data["path"])

        meta, embeddings = data["meta"], data["embeddings"]

        meat_id = store_in_milvus(embeddings, meta)
        meta.description = data["description"]

        results.append((meat_id, meta.model_dump(), data["path"]))

    with open('results.pkl', 'wb') as f:
        pickle.dump(results, f)

    print("Inserted", len(results), "files")

    meta_collection.flush()
    embed_collection.flush()


if __name__ == '__main__':
    main()
    save_to_db(clean=True)
