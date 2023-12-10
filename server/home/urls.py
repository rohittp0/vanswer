from django.urls import path

from home import views

urlpatterns = [
    path('upload', views.upload, name='upload'),
    path('', views.search, name='search'),
]
