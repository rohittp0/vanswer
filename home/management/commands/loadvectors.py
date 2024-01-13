import pickle
from pathlib import Path

from django.core.management.base import BaseCommand
from django.core.files import File

from home.models import MetaData
from tqdm import tqdm


class Command(BaseCommand):
    help = 'Loads vector data from pkl file'

    def add_arguments(self, parser):
        parser.add_argument('path', type=str)
        parser.add_argument('file_root', type=str)
        parser.add_argument('--clean', action='store_false')

    def handle(self, *args, **kwargs):
        path = Path(kwargs['path'])
        file_root = Path(kwargs['file_root'])

        if not path.exists():
            return print("File does not exist")

        if not file_root.exists() or not file_root.is_dir():
            return print("File root does not exist or is not a directory")

        if kwargs['clean']:
            MetaData.objects.all().delete()

        with open(str(path), "rb") as f:
            data = pickle.load(f)

        for meta_id, item, file in tqdm(data):
            file = Path(file).name

            try:
                with open(str(file_root.joinpath(file)), "rb") as f:
                    file = File(f)

                    meta = MetaData.objects.create(
                        name=item['name'],
                        language=item['language'],
                        type=item['type'],
                        tags=item['tags'],
                        states=item['states'],
                        description=item['description'],
                        organization=item['organization'],
                        meta_id=meta_id,
                        file=file
                    )
                    meta.save()

            except FileNotFoundError:
                print(f"File {file} not found")
