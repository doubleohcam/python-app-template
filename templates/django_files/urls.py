"""{app_name_pretty} URL configuration."""

from django.contrib import admin
from django.http import JsonResponse
from django.urls import path


def health(request):
    """Health check endpoint for container orchestration."""
    return JsonResponse({"status": "ok"})


urlpatterns = [
    path("admin/", admin.site.urls),
    path("health/", health),
]
