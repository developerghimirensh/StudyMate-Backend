from django.urls import include, path
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('sessions', views.StudySessionViewSet, basename='session')
router.register('topic-progress', views.TopicProgressViewSet, basename='topic-progress')
urlpatterns = [
    path("analytics/", views.progress_analytics, name="progress-analytics"),
    path("", include(router.urls)),
]
