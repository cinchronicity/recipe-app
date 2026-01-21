"""
URL configuration for recipe_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse


def favicon_view(request):
    """Return empty response for favicon requests to prevent 404 errors."""
    return HttpResponse(status=204)  # No content


# Tells Django which app handles which URL paths.
urlpatterns = [
    # Admin panel route
    path("admin/", admin.site.urls),
    # Favicon handler to prevent 404 errors
    path("favicon.ico", favicon_view, name="favicon"),
    # Authentication routes
    path("", include("accounts.urls")),
    # Root URL (homepage) is handled by the recipes app
    path("", include("recipes.urls")),
]
# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
