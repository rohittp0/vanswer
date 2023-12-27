from django.urls import path

from home import views

urlpatterns = [
    path('', views.home, name='home'),
    path('navbar', views.navbar, name='navbar'),
    path('search/', views.search, name='search'),
    path('organization/',views.organization, name='organization'),
    path('searchresult/', views.searchresult, name='searchresult'),
]
