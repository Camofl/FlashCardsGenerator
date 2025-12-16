from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, ListView, UpdateView, \
    DeleteView

from ..forms import DeckForm
from ..models import Deck


class DeckListView(ListView):
    model = Deck
    template_name = "cards/decks/list.html"
    context_object_name = "decks"


class DeckCreateView(LoginRequiredMixin, CreateView):
    model = Deck
    template_name = "cards/decks/form.html"
    form_class = DeckForm
    success_url = reverse_lazy("deck-list")

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)


class DeckDetailView(DetailView):
    model = Deck
    template_name = "cards/decks/detail.html"
    context_object_name = "deck"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        deck = self.object

        context["flashcards"] = deck.flashcards.all()
        return context


class DeckUpdateView(UpdateView):
    model = Deck
    template_name = "cards/decks/form.html"
    form_class = DeckForm
    success_url = reverse_lazy("deck-list")


class DeckDeleteView(DeleteView):
    model = Deck
    template_name = "cards/decks/confirm_delete.html"
    success_url = reverse_lazy("deck-list")
