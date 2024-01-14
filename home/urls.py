from django.urls import path

from home import views

urlpatterns = [
    path('', views.home, name='home'),
    path('search/', views.search, name='search'),
    path('themes/', views.themes, name='themes'),
    path('organization/',views.organization, name='organization'),
]
