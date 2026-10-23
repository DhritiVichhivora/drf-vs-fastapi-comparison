from django.urls import path

from . import views

urlpatterns = [
    path("countries", views.CountryList.as_view()),
    path("countries/<str:code>", views.CountryDetail.as_view()),
]