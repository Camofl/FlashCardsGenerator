from django.views.generic import ListView

from ..models import Flashcard


class FlashcardListView(ListView):
    model = Flashcard
    #template_name = "flashcards/decks/deck_list.html"
    context_object_name = "flashcards"
