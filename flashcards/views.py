"""Feature-facing view exports. Business logic remains in study.views for DB compatibility."""
from study.views import (
    DeckViewSet,
    FlashcardViewSet,
    ReviewViewSet,
)

__all__ = ['DeckViewSet', 'FlashcardViewSet', 'ReviewViewSet']
