from django.urls import path
from .views import (
    FlashcardListView, FlashcardDetailView,
    FlashcardCreateView, FlashcardUpdateView, FlashcardDeleteView
)

urlpatterns = [
    path("", FlashcardListView.as_view(), name="flashcard-list"),
    path("<int:pk>/", FlashcardDetailView.as_view(), name="flashcard-detail"),
    path("new/", FlashcardCreateView.as_view(), name="flashcard-create"),
    path("<int:pk>/edit/", FlashcardUpdateView.as_view(), name="flashcard-update"),
    path("<int:pk>/delete/", FlashcardDeleteView.as_view(), name="flashcard-delete"),
]
