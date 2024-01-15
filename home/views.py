from django.contrib.postgres.search import SearchQuery
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import render
from pgvector.django import CosineDistance

from home.constants import get_display_name, category_choices
from home.models import Organization, MetaData
from vector.models import Embedding
from vector.operations import texts_to_embeddings


def to_result(meta_data: MetaData, offset, index):
    return {
        'image_url': meta_data.preview_image,
        'title': f"{meta_data.title} - Page No: {offset + 1}",
        'description': meta_data.description,
        'read_more_url': f"{meta_data.file_data.all()[index].file.url}#page={offset + 1}",
        'contributor': meta_data.contributor or "Anonymous",
        'category': meta_data.get_category_display(),
    }


def home(request):
    return render(request, 'home/home.html')


def search(request):
    query_text = request.GET.get('query') or ""

    if not request.GET.getlist('format'):
        return HttpResponseRedirect('/')

    results = []

    embeddings = Embedding.objects.filter(meta_data__verified=True)
    metas = MetaData.objects.filter(verified=True)

    if query_text:
        query = SearchQuery("|".join(query_text.split(" ")), search_type="raw")
        metas = metas.filter(description_vector=query)

    query_emdeddings = texts_to_embeddings(query_text)[0]
    embeddings = (embeddings.alias(distance=CosineDistance('embedding', query_emdeddings))
                  .filter(distance__lt=0.6).order_by("distance"))

    org = request.GET.get('org')
    org_data = None
    if org:
        embeddings = embeddings.filter(meta_data__organization=org)
        metas = metas.filter(organization=org)
        org_data = Organization.objects.get(id=org)

    start_year = request.GET.get('date-from')
    end_year = request.GET.get('date-to')
    if start_year:
        embeddings = embeddings.filter(meta_data__date__year__gte=start_year)
        metas = metas.filter(date__year__gte=start_year)
    if end_year:
        embeddings = embeddings.filter(meta_data__date__year__lte=end_year)
        metas = metas.filter(date__year__lte=end_year)

    language = request.GET.getlist('language')
    if language:
        metas = metas.filter(language__in=language)
        embeddings = embeddings.filter(meta_data__language__in=language)

    category = request.GET.getlist('format')
    if category:
        metas = metas.filter(category__in=category)
        embeddings = embeddings.filter(meta_data__category__in=category)

    location = request.GET.getlist('location')
    if location:
        query = Q(meta_data__states__contains=[location[0]])
        query_meta = Q(states__contains=[location[0]])
        for state in location[1:]:
            query |= Q(meta_data__states__contains=[state])
            query_meta |= Q(states__contains=[state])

        embeddings = embeddings.filter(query)
        metas = metas.filter(query_meta)

    sort = request.GET.get('sort_by')
    if sort == "oldest":
        embeddings = embeddings.order_by('-meta_data__date')
        metas = metas.order_by('-date')
    elif sort == "latest":
        embeddings = embeddings.order_by('meta_data__date')
        metas = metas.order_by('date')

    page_number = int(request.GET.get('page') or '1')
    page_count = (len(metas) + len(embeddings)) // 10 + 1

    for meta in metas[(page_number - 1) * 10:page_number * 10]:
        results.append(to_result(meta, 0, 0))

    for embedding in embeddings[(page_number - 1) * 10:page_number * 10]:
        results.append(to_result(embedding.meta_data, embedding.offset, embedding.index))

    page_range = range(max(1, page_number - 2), min(page_count + 1, page_number + 3))
    page_obj = {"has_previous": page_number > 1, "number": page_number, "page_range": page_range,
                "has_next": page_number < page_count, "num_pages": page_count}

    return render(request, 'home/searchresult.html',
                  {'query': query_text, 'page_obj': page_obj, 'org': org_data, 'results': results,
                   'format': get_display_name(category_choices, category[0])})


def organization(request):
    details = Organization.objects.all()
    return render(request, 'home/organization.html', {'details': details})


def themes(request):
    return render(request, 'home/themes.html')
