from django.urls import path
from . import views


urlpatterns = [
    path("", views.index, name="index"),
    path("new_index/", views.new_index, name="new_index"),
    path("sabmus/", views.sabmus, name="sabmus"),
    path("simon/", views.simon, name="simon"),
    path("<str:name>", views.greet, name="greet")
]
