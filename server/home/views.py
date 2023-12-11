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
        "expr": "",
        "query": query_text,
        "limit": 10,
    }).json()

    meta_ids = list({o["meta_id"] for o in api_result})
    metas = MetaData.objects.filter(meta_id__in=meta_ids).all()

    results = [api_result.filter(lambda x: x["meta_id"] == meta.meta_id) for meta in metas]
    print(results)

    # Process and display results
    for meta in metas:
        # item = o.properties
        # print(o.uuid, o.metadata)
        # if o.metadata.certainty < 0.75:
        #     continue
        # results.append({
        #     'image_url': ('data:image/png;base64,' + item['image']) if item.get('location') else False,
        #     'title': "",
        #     'description': item['description'],
        #     'read_more_url': getattr(settings, "MEDIA_URL", None) + item.get('location') if item.get(
        #         'location') else False,
        # }, )
        pass

    return render(request, 'home/search.html', {'query': query_text, 'results': []})
