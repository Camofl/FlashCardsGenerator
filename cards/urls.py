from django.urls import path
from .views.flashcards import *
from .views.decks import *

urlpatterns = [
    path("", FlashcardListView.as_view(), name="flashcard-list"),
    path("<int:pk>/", FlashcardDetailView.as_view(), name="flashcard-detail"),
    path("new/", FlashcardCreateView.as_view(), name="flashcard-create"),
    path("<int:pk>/edit/", FlashcardUpdateView.as_view(), name="flashcard-update"),
    path("<int:pk>/delete/", FlashcardDeleteView.as_view(), name="flashcard-delete"),
    path("get-definition/", GetDefinitionView.as_view(), name="get-definition"),
    path("bulk/", BulkPasteView.as_view(), name="flashcard-bulk-paste"),
    path("bulk/review/", BulkReviewCreateView.as_view(),
         name="flashcard-bulk-review"),
    path("bulk/get-definitions/", BulkGetDefinitionsView.as_view(),
         name="get-definitions-bulk"),
    path("decks/", DeckListView.as_view(), name="deck-list"),
    path("decks/new", DeckCreateView.as_view(), name="deck-create"),
    path("decks/<int:pk>/", DeckDetailView.as_view(), name="deck-detail"),
    path("decks/<int:pk>/edit", DeckUpdateView.as_view(), name="deck-update"),
    path("decks/<int:pk>/delete", DeckDeleteView.as_view(), name="deck-delete"),
]
