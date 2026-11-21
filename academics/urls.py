from django.urls import include, path
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('subjects', views.SubjectViewSet, basename='subject')
router.register('units', views.UnitViewSet, basename='unit')
router.register('topics', views.TopicViewSet, basename='topic')
urlpatterns = [path("", include(router.urls))]
