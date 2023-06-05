from django.urls import path
from . import views

urlpatterns = [
    path("", views.UploadPage.as_view(), name="top"),
]
