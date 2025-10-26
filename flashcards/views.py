from django.views.generic import ListView, DetailView, CreateView, UpdateView, \
    DeleteView
from django.urls import reverse_lazy
from .models import Flashcard


class FlashcardListView(ListView):
    model = Flashcard
    template_name = "flashcards/flashcard_list.html"
    context_object_name = "flashcards"


class FlashcardDetailView(DetailView):
    model = Flashcard
    template_name = "flashcards/flashcard_detail.html"
    context_object_name = "flashcard"


class FlashcardCreateView(CreateView):
    model = Flashcard
    template_name = "flashcards/flashcard_form.html"
    fields = ["front", "back", "hidden"]
    success_url = reverse_lazy("flashcard-list")


class FlashcardUpdateView(UpdateView):
    model = Flashcard
    template_name = "flashcards/flashcard_form.html"
    fields = ["front", "back", "hidden"]
    success_url = reverse_lazy("flashcard-list")


class FlashcardDeleteView(DeleteView):
    model = Flashcard
    template_name = "flashcards/flashcard_confirm_delete.html"
    success_url = reverse_lazy("flashcard-list")
