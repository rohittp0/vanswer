import requests
from django.conf import settings
from django.contrib.postgres.search import SearchQuery
from django.db.models import Q
from django.shortcuts import render

from home.models import MetaData

collection_name = "main"


def get_from_api(api: str, query: str):
    query = query.strip()
    verified = MetaData.objects.filter(verified=True)

    result = requests.get(f"{settings.VECTOR_API_URL}/search/{api}/", params={
        "expr": "type == 0" if api == "elements" else "",
        "query": query,
        "limit": 10,
    }).json()

    if api == "elements":
        api_result = {(o["meta_id"], o["index"]): o for o in result}
    else:
        query = SearchQuery("|".join(query.split(" ")), search_type="raw")
        api_result = {(o.meta_id, 0) for o in verified.filter(description_vector=query).all()}
        api_result = api_result.union({(o["id"], 0) for o in result})

    meta_ids = list({o[0] for o in api_result})
    metas = verified.filter(Q(meta_id__in=meta_ids)).all()

    return api_result, metas


def search(request):
    query_text = request.GET.get('query')

    if not query_text:
        return render(request, 'home/search.html', {'query': "", 'results': []})

    api_result, metas = get_from_api(request.GET.get('search_type'), query_text)

    results = []

    # Process and display results
    for meta in metas:
        for element in filter(lambda x: x[0] == meta.meta_id, api_result):
            results.append({
                'image_url': f"{meta.file_data.first().file.url}#page={element[1] + 1}",
                'title': f"{meta.title} - Page No: {element[1] + 1}",
                'description': meta.description,
                'read_more_url': f"{meta.file_data.first().file.url}#page={element[1] + 1}",
            })

    return render(request, 'home/search.html', {'query': query_text, 'results': results})
