from django import template

from home.constants import language_choices, category_choices, state_choices

register = template.Library()


@register.simple_tag
def get_categories():
    # Define your list here
    return category_choices


@register.simple_tag
def get_filters():
    filters = {
        "Language": ["language", language_choices, "checkbox"],
        "Formats": ["format", category_choices, "radio"],
        # "file_type": [file_types],
        "Location": ["location", state_choices, "checkbox"],
        # "url_type": [url_types],
    }

    return filters

@register.simple_tag
def get_themes():
    themes = {
        "Backyard Poultry": "Poultry Logo.png",
        "Natural Farming": "Natural Farming Logo.png",
        "Entrepreneurship": "Rural Entrepreneurship Logo.png",
        "Bamboo": "Bamboo Logo.png",
        "Waste Mgmt. ": "Waste Mgmt Logo.png",
        "Farm Innovations. ": "Settings Logo.png",

    }

    return themes


@register.filter
def get_querydict_list(dictionary, key):
    return dictionary.getlist(key, None)


@register.filter
def get_querydict_item(dictionary, key):
    return dictionary.get(key, None)


@register.filter
def filter_in(filter_list, value):
    if filter_list:
        return value in filter_list


@register.simple_tag
def query_transform(request, **kwargs):
    updated = request.GET.copy()
    updated.update(kwargs)
    return updated.urlencode()
