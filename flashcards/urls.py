from django.urls import include, path
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('decks', views.DeckViewSet, basename='deck')
router.register('flashcards', views.FlashcardViewSet, basename='flashcard')
router.register('reviews', views.ReviewViewSet, basename='review')
urlpatterns = [path("", include(router.urls))]
