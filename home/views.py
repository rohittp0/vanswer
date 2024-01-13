import requests
from django.conf import settings
from django.contrib.postgres.search import SearchQuery
from django.db.models import Q
from django.shortcuts import render
from pdf2image import convert_from_path
from home.models import MetaData, Organization

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


def home(request):
    return render(request, 'home/home.html')


# =================================================================================================


def search(request):
    query_text = request.GET.get('query')
    search_type = request.GET.get('search_type')
    metadata = MetaData.objects.all()
    results = []


    if query_text:
        api_result, metas = get_from_api("meta" if search_type is None else search_type, query_text)
        metadata = metadata.filter(meta_id__in=[meta.meta_id for meta in metas])

        # filtering


        org = request.GET.get('org')
        if org:
            metadata = metadata.filter(organization=org)

        language = request.GET.getlist('language')
        if language:
            metadata = metadata.filter(language__in=language)

        format = request.GET.getlist('format')
        if language:
            metadata = metadata.filter(category__contains=format)

        location = request.GET.getlist('location')
        if language:
            metadata = metadata.filter(states__contains=location)


    if query_text:
        for meta in metas:
            for element in filter(lambda x: x[0] == meta.meta_id, api_result):
                meta_data = metadata.get(meta_id=meta.meta_id)
                results.append({
                    'image_url': meta_data.preview_image,
                    'title': f"{meta.title} - Page No: {element[1] + 1}",
                    'description': meta.description,
                    'read_more_url': f"{meta.file_data.first().file.url}#page={element[1] + 1}",
                    'contributor': meta_data.contributor,
                    'category': meta_data.category,
                })
    else:
        for meta in metadata:
            results.append({
                'image_url': meta.preview_image,
                'title': f"{meta.title}",
                'description': meta.description,
                'read_more_url': f"{meta.file_data.first().file.url}",
                'contributor': meta.contributor,
                'category': meta.category,
            })





    return render(request, 'home/searchresult.html', {'query': query_text, 'results': results})


def organization(request):
    details = Organization.objects.all()
    return render(request, 'home/organization.html', {'details': details})
