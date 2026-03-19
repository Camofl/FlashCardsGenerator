import json

from django import forms
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView, \
    DeleteView

from .models import Flashcard
from .services import DictionaryAPI


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
    widgets = {'hidden': forms.CheckboxInput()}

    def form_valid(self, form):
        flashcard = form.save(commit=False)

        if not flashcard.back and flashcard.front:
            definition = DictionaryAPI.get_definition(flashcard.front, api="wordsapi")
            if definition:
                flashcard.back = definition
            else:
                flashcard.back = "[No definition found]"

        return super().form_valid(form)


class FlashcardUpdateView(UpdateView):
    model = Flashcard
    template_name = "flashcards/flashcard_form.html"
    fields = ["front", "back", "hidden"]
    success_url = reverse_lazy("flashcard-list")
    widgets = {
        'hidden': forms.CheckboxInput(),
    }


class FlashcardDeleteView(DeleteView):
    model = Flashcard
    template_name = "flashcards/flashcard_confirm_delete.html"
    success_url = reverse_lazy("flashcard-list")

class GetDefinitionView(View):
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        word_raw = data.get("word", "").strip()
        api = data.get("api", "freedictionary")

        if not word_raw:
            return JsonResponse({"error": "No word provided"}, status=400)

        word = word_raw

        if word_raw.lower().startswith("to "):
            preferred_pos = ["verb"]
            word = word_raw[3:]
        elif word_raw.lower().startswith("the "):
            preferred_pos = ["noun"]
            word = word_raw[4:]
        else:
            preferred_pos = ["pronoun", "adjective", "adverb", "preposition",
                             "conjunction", "interjection"]

        definition = DictionaryAPI.get_definition(
            word=word,
            api=api,
            preferred_pos=preferred_pos
        )

        if definition:
            return JsonResponse({"definition": definition})
        return JsonResponse({"error": "No definition found"}, status=404)
