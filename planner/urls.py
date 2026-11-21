from django.urls import include, path
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('tasks', views.TaskViewSet, basename='task')
router.register('reminders', views.ReminderViewSet, basename='reminder')
urlpatterns = [path("", include(router.urls))]
