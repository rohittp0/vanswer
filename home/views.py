import requests
from django.conf import settings
from django.contrib.postgres.search import SearchQuery
from django.core.paginator import PageNotAnInteger, EmptyPage, Paginator
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import render
from pgvector.django import MaxInnerProduct

from home.constants import get_display_name, category_choices
from home.models import MetaData, Organization
from vector.models import Embedding
from vector.operations import texts_to_embeddings


def home(request):
    return render(request, 'home/home.html')


def search(request):
    query_text = request.GET.get('query') or ""

    if not request.GET.getlist('format'):
        return HttpResponseRedirect('/')

    results = []

    embeddings = Embedding.objects.filter(verified=True)

    query_emdeddings = texts_to_embeddings(query_text)
    embeddings = embeddings.order_by(MaxInnerProduct('embedding', query_emdeddings[0]))

    org = request.GET.get('org')
    org_data = None
    if org:
        embeddings = embeddings.filter(meta_data__organization=org)
        org_data = Organization.objects.get(id=org)

    start_year = request.GET.get('date-from')
    end_year = request.GET.get('date-to')
    if start_year:
        embeddings = embeddings.filter(meta_data__date__year__gte=start_year)
    if end_year:
        embeddings = embeddings.filter(meta_data__date__year__lte=end_year)

    language = request.GET.getlist('language')
    if language:
        embeddings = embeddings.filter(meta_data__language__in=language)

    category = request.GET.getlist('format')
    if category:
        embeddings = embeddings.filter(meta_data__category__in=category)

    location = request.GET.getlist('location')
    if location:
        query = Q(meta_data__states__contains=[location[0]])
        for state in location[1:]:
            query |= Q(meta_data__states__contains=[state])
        embeddings = embeddings.filter(query)

    sort = request.GET.get('sort_by')
    if sort == "oldest":
        embeddings = embeddings.order_by('-meta_data__date')
    elif sort == "latest":
        embeddings = embeddings.order_by('meta_data__date')

    for emb in embeddings:
        results.append({
            'image_url': emb.meta_data.preview_image,
            'title': f"{emb.meta_data.title} - Page No: {emb.offset + 1}",
            'description': emb.meta_data.description,
            'read_more_url': f"{emb.meta_data.file_data.all()[emb.index].file.url}#page={emb.offset + 1}",
            'contributor': emb.meta_data.contributor,
            'category': emb.meta_data.get_category_display(),
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


def themes(request):
    return render(request, 'home/themes.html')
