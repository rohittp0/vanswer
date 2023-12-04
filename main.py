import base64
from io import BytesIO

import requests
import weaviate

client = weaviate.connect_to_local()
collection_name = "main"



while True:
    url = input("Enter image URL (leave empty to exit): ")
    if not url:
        break

    description = input("Enter description: ")
    category = input("Enter category: ")

    # Download the image
    # response = requests.get(url)

    image_data = None
    # Read the image
    with open('media/page_1_image_1.jpg', 'rb') as file:
        image_data = BytesIO(file.read())



    # Convert the image to base64
    encoded_image = base64.b64encode(image_data.read()).decode()

    # Create the sample data
    sample_data = {
        "image": encoded_image,
        "description": description,
        "category": category
    }

    # Insert the object into the collection
    uuid = client.collections.get(collection_name).data.insert(properties=sample_data)
    print(f"Inserted object with UUID: {uuid}")
