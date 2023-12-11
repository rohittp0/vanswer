import requests
from django.conf import settings
from django.shortcuts import render

from home.models import MetaData

collection_name = "main"


def search(request):
    query_text = request.GET.get('query')

    if not query_text:
        return render(request, 'home/search.html', {'query': "", 'results': []})

    api_result = requests.get(settings.VECTOR_API_URL + "/search/elements", params={
        "expr": "type == 0",
        "query": query_text,
        "limit": 10,
    }).json()

    meta_ids = list({o["meta_id"] for o in api_result})
    metas = MetaData.objects.filter(meta_id__in=meta_ids).all()

    results = []

    # Process and display results
    for meta in metas:
        for element in filter(lambda x: x["meta_id"] == meta.meta_id, api_result):
            results.append({
                'image_url': f"{meta.file.url}#page={element['index']}",
                'title': f"{meta.name} - Page No: {element['index']}",
                'description': meta.description,
                'read_more_url': meta.file.url,
            })

    return render(request, 'home/search.html', {'query': query_text, 'results': results})
