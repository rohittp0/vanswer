import requests
from django.conf import settings
from django.contrib.postgres.search import SearchQuery
from django.db.models import Q
from django.shortcuts import render

from home.models import MetaData, Organization
from django.http import JsonResponse

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

    if not query_text:
        return render(request, 'home/search.html', {'query': "", 'results': []})

    api_result, metas = get_from_api(request.GET.get('search_type'), query_text)

    results = []
    # Process and display
    metadata = MetaData.objects.filter(id__in=[meta.meta_id for meta in metas])

    #filtering
    language = request.GET.getlist('language')
    if language:
        metadata = metadata.filter(language__in=language)

    format = request.GET.getlist('format')
    if language:
        metadata = metadata.filter(category__contains=format)

    location = request.GET.getlist('location')
    if language:
        metadata = metadata.filter(states__contains=location)

    for meta in metas:
        print(meta, "m")
        for element in filter(lambda x: x[0] == meta.meta_id, api_result):
            results.append({
                'image_url': f"{meta.file_data.first().file.url}#page={element[1] + 1}",
                'title': f"{meta.title} - Page No: {element[1] + 1}",
                'description': meta.description,
                'read_more_url': f"{meta.file_data.first().file.url}#page={element[1] + 1}",
                'contributor': metadata.contributor,
                'category': metadata.category,
            })

    return render(request, 'home/searchresult.html', {'query': query_text, 'results': results})


def organization(request):
    details = Organization.objects.all()
    return render(request, 'home/organization.html',{'details':details})


def searchresult(request):
    dropdown_values = []
    dropdown_values_unique = ""

    field = request.GET.get('field')
    data = request.GET.get('data')
    print(field, "fieldddddddd")
    print(data,"ddddddddddddddddata")

    if field:
        dropdown_values = MetaData.objects.filter(**{f"{field}__isnull": False}).values_list(field, flat=True)
        dropdown_values_lower = []

        for value in dropdown_values:
            if isinstance(value, list):
                dropdown_values_lower.extend([item.lower() for item in value])
            else:
                dropdown_values_lower.append(value.lower())

        dropdown_values_unique = set(dropdown_values_lower)
        print(dropdown_values_unique, "unique valueeeeeeeeees")

        return JsonResponse({"dropdown_values": list(dropdown_values_unique)})

    field_names = ["language", "states"]    
    messages = ['language:malayalam', 'state:kerala', 'organization: pradan']
    context = {
        "messages": messages,
        "field_names": field_names,
        "dropdown": dropdown_values_unique,
    }

    return render(request, 'home/searchresult.html', context)
