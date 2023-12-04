import weaviate
import weaviate.classes as wvc


client = weaviate.connect_to_local()
collection_name = "main"
# client.collections.delete(collection_name)

# Create a collection with multi2vec-clip as the vectorizer
collection = client.collections.create(
    name=collection_name,
    vectorizer_config=wvc.Configure.Vectorizer.multi2vec_clip(["image"], ["description"]),
    properties=[
        wvc.Property(
            name="image",
            data_type=wvc.DataType.BLOB
        ),
        wvc.Property(
            name="description",
            data_type=wvc.DataType.TEXT
        ),
        # wvc.Property(
        #     name="category",
        #     data_type=wvc.DataType.TEXT
        # ),
        wvc.Property(
            name="location",
            data_type=wvc.DataType.TEXT,
            skip_vectorization=True
        ),
    ]
)
