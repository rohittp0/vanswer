import weaviate
from PIL import Image
import io
import base64

client = weaviate.connect_to_local()
collection_name = "main"


def display_image(encoded_image):
    # Convert base64 image to bytes and display it
    image_bytes = base64.b64decode(encoded_image)
    image = Image.open(io.BytesIO(image_bytes))
    image.show()


while True:
    query_text = input("Enter query text (leave empty to exit): ")
    if not query_text:
        break

    # Perform the search using near_text
    response = client.collections.get(collection_name).query.near_text(
        query=query_text,
        return_properties=["description", "category", "image"],
        limit=1
    )

    # Process and display results
    for o in response.objects:
        item = o.properties
        print(f"Description: {item['description']}")
        print(f"Category: {item['category']}")
        display_image(item['image'])
