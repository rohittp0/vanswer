import numpy as np
import requests
from django.conf import settings
from django.contrib.postgres.search import SearchQuery
from django.core.paginator import PageNotAnInteger, EmptyPage, Paginator
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import render
from pgvector.django import L2Distance

from home.constants import get_display_name, category_choices
from home.models import MetaData, Organization
from vector.models import Embedding
from vector.operations import texts_to_embeddings
from vector.tasks import get_embeddings

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
    metadata = MetaData.objects.all()

    if not request.GET.getlist('format'):
        return HttpResponseRedirect('/')

    results = []

    if query_text:
        print("searching", flush=True)
        query_emdeddings = texts_to_embeddings(query_text)
        embeddings = Embedding.objects.order_by(L2Distance('embedding', query_emdeddings[0]))
        metadata = metadata.filter(meta_id__in=[emb.meta_data for emb in embeddings])

        # filtering

    org = request.GET.get('org')
    org_data = None
    if org:
        metadata = metadata.filter(organization=org)
        org_data = Organization.objects.get(id=org)

    start_year = request.GET.get('date-from')
    end_year = request.GET.get('date-to')
    if start_year:
        metadata = metadata.filter(date__year__gte=start_year)
    if end_year:
        metadata = metadata.filter(date__year__lte=end_year)

    language = request.GET.getlist('language')
    if language:
        metadata = metadata.filter(language__in=language)

    category = request.GET.getlist('format')
    if format:
        metadata = metadata.filter(category__in=category)

    location = request.GET.getlist('location')
    if location:
        metadata = metadata.filter(states__contains=location)

    sort = request.GET.get('sort_by')
    if sort == "oldest":
        metadata = metadata.order_by('-date')
    elif sort == "latest":
        metadata = metadata.order_by('date')

    if query_text:
        for emb in embeddings:
            meta_data = metadata.get(meta_id=emb.meta_data)
            if meta_data:
                results.append({
                    'image_url': meta_data.preview_image,
                    'title': f"{meta_data.title} - Page No: {emb.index + 1}",
                    'description': meta_data.description,
                    'read_more_url': f"{meta_data.file_data.first().file.url}#page={emb.index + 1}",
                    'contributor': meta_data.contributor,
                    'category': meta_data.get_category_display(),
                })
    else:
        for meta in metadata:
            results.append({
                'image_url': meta.preview_image,
                'title': f"{meta.title}",
                'description': meta.description,
                'read_more_url': f"{meta.file_data.first().file.url}",
                'contributor': meta.contributor,
                'category': meta.get_category_display(),
            })

    paginator = Paginator(results, 10)
    page_number = request.GET.get('page')

    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    return render(request, 'home/searchresult.html',
                  {'query': query_text, 'page_obj': page_obj, 'org': org_data,
                   'format': get_display_name(category_choices, category[0])})


def organization(request):
    details = Organization.objects.all()
    return render(request, 'home/organization.html', {'details': details})
