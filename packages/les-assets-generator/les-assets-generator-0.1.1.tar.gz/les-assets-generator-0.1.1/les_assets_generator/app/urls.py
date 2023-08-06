from django.urls import path

from les_assets_generator.app import views

urlpatterns = [
    path("", views.index, name="index"),
    path("<str:title>/", views.generate, name="generate"),
]
