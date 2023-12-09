import csv
import os
import pickle
from io import BytesIO
from typing import List

from tqdm import tqdm

from vector.db import MetaData, Embedding
from vector.operations import process_pdf, elements_to_embeddings, texts_to_embeddings


def read_csv_and_create_meta_data(file_path):
    meta_data_list = []

    with open(file_path, 'r') as f:
        reader = csv.reader(f)
        next(reader)  # Skip the header row

        for row in reader:
            path = os.path.join("..", "res", row[1])
            meta_data = MetaData(
                name=row[0],
                language=row[2],
                type=row[3],
                tags=[t.strip() for t in row[4].split(',')],
                state=row[5],
                description=row[6],
                organization=row[9]
            )
            meta_data_list.append((path, meta_data))

    return meta_data_list


def save_data_to_file_with_pickle(meta: MetaData, embeddings: List[Embedding], output_file: str):
    with open(output_file, 'wb') as f:
        pickle.dump({'meta': meta, 'embeddings': embeddings}, f)


def main():
    metas = read_csv_and_create_meta_data('../res/paths.csv')

    # Create save directory
    save_dir = '../res/embeddings'
    os.makedirs(save_dir, exist_ok=True)
    i = 0

    for path, meta in tqdm(metas):
        with open(path, 'rb') as f:
            pdf = BytesIO(f.read())
            elements = process_pdf(pdf)
            embeds = elements_to_embeddings(elements)

        if isinstance(meta.description, str):
            meta.description = texts_to_embeddings([meta.description])[0]
        else:
            raise ValueError("Description is not a string")

        save_data_to_file_with_pickle(meta, embeds, os.path.join(save_dir, f'{i}.pkl'))
        i += 1


if __name__ == '__main__':
    main()
