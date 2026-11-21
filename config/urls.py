from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/security/", include("security.urls")),
    path("api/v1/", include("academics.urls")),
    path("api/v1/", include("planner.urls")),
    path("api/v1/", include("flashcards.urls")),
    path("api/v1/progress/", include("progress.urls")),
    path("api/v1/", include("core.urls")),
]
