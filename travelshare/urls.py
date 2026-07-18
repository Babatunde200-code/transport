"""
URL configuration for travelshare project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from django.http import JsonResponse

def root_view(request):
    import subprocess
    import os
    try:
        commit = subprocess.check_output(["git", "rev-parse", "HEAD"]).decode("utf-8").strip()
    except Exception as e:
        commit = f"Unknown: {str(e)}"
    
    try:
        from django.conf import settings as django_settings
        with open(os.path.join(django_settings.BASE_DIR, "accounts/views.py"), "r") as f:
            content_preview = f.read(500)
    except Exception as e:
        content_preview = f"Error reading file: {str(e)}"

    return JsonResponse({
        "status": "Server is live",
        "commit": commit,
        "content_preview_has_try_except": "Unhandled Server Error" in content_preview
    })

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", root_view),

    # API routes
    path("api/", include("accounts.urls")),
    path("api/", include("travels.urls")),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
