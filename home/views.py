import base64
import io

import filetype
from PyPDF2 import PdfReader
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.http import JsonResponse
from django.shortcuts import render
from pdf2image import convert_from_path
import weaviate
import weaviate.classes as wvc
import uuid

client = weaviate.connect_to_local()

collection_name = "main"


def upload(request):
    results = []

    if request.method == 'POST':
        # Access form data
        desc = request.POST.get('file_desc')  # Example of accessing a text field
        text = request.POST.get('text_doc')

        if text:
            data_object = {
                "description": text[:228],
                "location": ""
            }
            id = client.collections.get(collection_name).data.insert(properties=data_object)
            print("added text", id)
            return render(request, 'home/upload.html', context={'uploaded': True})

        # Access the file
        uploaded_file = request.FILES.get('file')

        if not uploaded_file:
            return JsonResponse({'error': 'No file provided'}, status=400)
        else:
            ext = uploaded_file.name.split('.')[-1]
            filename = "%s.%s" % (uuid.uuid4(), ext)

            fs = FileSystemStorage()
            filename = fs.save(filename, uploaded_file)
            print(filename)

            path = getattr(settings, "MEDIA_ROOT", None) / filename

            if filetype.is_image(path):
                with open(path, 'rb') as file:
                    image_data = io.BytesIO(file.read())
                    encoded_image = base64.b64encode(image_data.read()).decode()

                data_object = {
                    "image": encoded_image,
                    "description": desc[:228],
                    "location": filename
                }
                id = client.collections.get(collection_name).data.insert(properties=data_object)
                print("added image", id)

                return render(request, 'home/upload.html', context={'uploaded': True})

            try:
                reader = PdfReader(path)

                num_pages = len(reader.pages)

                for i in range(num_pages):
                    # Extract text
                    page = reader.pages[i]
                    text = page.extract_text() or ""

                    # Convert the first image of the page to base64
                    images = convert_from_path(path, first_page=i + 1, last_page=i + 1, fmt='jpeg')
                    image_base64 = ""

                    if images:
                        buffered = io.BytesIO()
                        images[0].save(buffered, format="JPEG")
                        image_base64 = base64.b64encode(buffered.getvalue()).decode()

                    print(len(text))
                    # Add to Weaviate
                    data_object = {
                        "image": image_base64,
                        "description": text[:228],
                        "location": filename
                    }
                    client.collections.get(collection_name).data.insert(properties=data_object)
            except Exception as e:
                return render(request, 'home/upload.html', context={'error': True})

            return render(request, 'home/upload.html', context={'uploaded': True})

    return render(request, 'home/upload.html')


def search(request):
    results = []


    if request.method == 'POST':
        query_text = request.POST.get('query')

        response = client.collections.get(collection_name).query.near_text(
            query=query_text,
            return_properties=["description", "location", "image"],
            limit=5,
            return_metadata=wvc.MetadataQuery(certainty=True, distance=True),
        )

        # res = client.collections.get(collection_name).query.fetch_objects(
        #     filters=wvc.Filter(path="location").equal("9e654e30-1b0f-49b3-85e8-7a52e2af0ff8.pdf"),
        # )
        #
        # for o in res.objects:
        #     if o.properties.get('location'):
        #         client.collections.get(collection_name).data.delete_by_id(o.uuid)

        results = []

        # Process and display results
        for o in response.objects:
            item = o.properties
            print(o.uuid, o.metadata)
            if o.metadata.certainty < 0.75:
                continue
            results.append({
                'image_url': ('data:image/png;base64,' + item['image'] )if item.get('location') else False,
                'title': "",
                'description': item['description'],
                'read_more_url': getattr(settings, "MEDIA_URL", None) + item.get('location') if item.get('location') else False,
            }, )

        return render(request, 'home/search.html', {'query': query_text, 'results': results})

    return render(request, 'home/search.html', {'query': "", 'results': results})
