from django.conf import settings
from django.shortcuts import render

collection_name = "main"


def search(request):
    results = []

    if request.method == 'POST':
        query_text = request.POST.get('query')

        # Process and display results
        for o in response.objects:
            item = o.properties
            print(o.uuid, o.metadata)
            if o.metadata.certainty < 0.75:
                continue
            results.append({
                'image_url': ('data:image/png;base64,' + item['image']) if item.get('location') else False,
                'title': "",
                'description': item['description'],
                'read_more_url': getattr(settings, "MEDIA_URL", None) + item.get('location') if item.get(
                    'location') else False,
            }, )

        return render(request, 'home/search.html', {'query': query_text, 'results': results})

    return render(request, 'home/search.html', {'query': "", 'results': results})
