from django import forms
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView, DetailView, CreateView, UpdateView, \
    DeleteView
from django.urls import reverse_lazy
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


@method_decorator(csrf_exempt, name="dispatch")
class GetDefinitionView(View):
    def post(self, request, *args, **kwargs):
        import json
        data = json.loads(request.body)
        word = data.get("word")
        api = data.get("api", "freedictionary")  # default to Free Dictionary

        if not word:
            return JsonResponse({"error": "No word provided"}, status=400)

        definition = DictionaryAPI.get_definition(word, api=api)

        if definition:
            return JsonResponse({"definition": definition})
        return JsonResponse({"error": "No definition found"}, status=404)
