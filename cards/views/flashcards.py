import json

from django import forms
from django.contrib import messages
from django.forms import formset_factory
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView, \
    DeleteView

from ..forms import BulkFlashcardRowForm
from ..models import Flashcard
from ..services import DictionaryAPI


class FlashcardListView(ListView):
    model = Flashcard
    template_name = "cards/flashcards/list.html"
    context_object_name = "flashcards"


class FlashcardDetailView(DetailView):
    model = Flashcard
    template_name = "cards/flashcards/detail.html"
    context_object_name = "flashcard"


class FlashcardCreateView(CreateView):
    model = Flashcard
    template_name = "cards/flashcards/form.html"
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
    template_name = "cards/flashcards/form.html"
    fields = ["front", "back", "hidden"]
    success_url = reverse_lazy("flashcard-list")
    widgets = {
        'hidden': forms.CheckboxInput(),
    }


class FlashcardDeleteView(DeleteView):
    model = Flashcard
    template_name = "cards/flashcards/confirm_delete.html"
    success_url = reverse_lazy("flashcard-list")

class GetDefinitionView(View):
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        word_raw = data.get("word", "").strip()
        api = data.get("api", "freedictionary")

        if not word_raw:
            return JsonResponse({"error": "No word provided"}, status=400)

        definition = fetch_definition_helper(word_raw, api=api)

        if definition:
            return JsonResponse({"definition": definition})
        return JsonResponse({"error": "No definition found"}, status=404)


def get_preferred_pos(word):
    if word.lower().startswith("to "):
        preferred_pos = ["verb"]
        word = word[3:]
    elif word.lower().startswith("the "):
        preferred_pos = ["noun"]
        word = word[4:]
    else:
        preferred_pos = ["pronoun", "adjective", "adverb", "preposition",
                         "conjunction", "interjection"]
    return word, preferred_pos


def fetch_definition_helper(word, api="freedictionary"):
    word, preferred_pos = get_preferred_pos(word)
    return DictionaryAPI.get_definition(
        word=word,
        api=api,
        preferred_pos=preferred_pos,
    )


class BulkPasteView(View):
    template_name = "cards/flashcards/bulk_paste.html"
    session_key = "bulk_flashcard_fronts"

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)

    def post(self, request, *args, **kwargs):
        raw = request.POST.get("vocabulary", "")
        words = [line.strip() for line in raw.splitlines() if line.strip()]

        if not words:
            messages.error(request, "Please paste at least one line.")
            return render(request, self.template_name, {"vocabulary": raw})

        seen = set()
        deduped = [
            w for w in words if (k := w.casefold()) not in seen and not seen.add(k)
        ]

        request.session[self.session_key] = deduped
        return redirect("flashcard-bulk-review")


class BulkReviewCreateView(View):
    template_name = "cards/flashcards/bulk_review.html"
    session_key = "bulk_flashcard_fronts"

    def _get_words(self, request):
        return request.session.get(self.session_key, [])

    def get(self, request, *args, **kwargs):
        words = self._get_words(request)
        if not words:
            return redirect("flashcard-bulk-paste")

        row_formset = formset_factory(BulkFlashcardRowForm, extra=0)
        initial = [{"front": w, "back": "", "hidden": False} for w in words]
        formset = row_formset(initial=initial)
        return render(request, self.template_name, {"formset": formset})

    def post(self, request, *args, **kwargs):
        words = self._get_words(request)
        if not words:
            return redirect("flashcard-bulk-paste")

        row_formset = formset_factory(BulkFlashcardRowForm, extra=0)
        initial = [{"front": w, "back": "", "hidden": False} for w in words]

        formset = row_formset(request.POST, initial=initial)

        if not formset.is_valid():
            return render(request, self.template_name, {"formset": formset})

        objs = []
        for row in formset.cleaned_data:
            front = (row.get("front") or "").strip()
            back = (row.get("back") or "").strip()
            hidden = bool(row.get("hidden"))

            if not front:
                continue

            objs.append(Flashcard(front=front, back=back, hidden=hidden))

        if not objs:
            messages.error(request, "Nothing to create.")
            return render(request, self.template_name, {"formset": formset})

        Flashcard.objects.bulk_create(objs)
        request.session.pop(self.session_key, None)
        messages.success(request, f"Created {len(objs)} flashcards.")
        return redirect("flashcard-list")


class BulkGetDefinitionsView(View):
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body or "{}")
        api = data.get("api", "freedictionary")
        words = data.get("words", [])

        if not isinstance(words, list) or not words:
            return JsonResponse({"error": "No words provided"}, status=400)

        definitions = []
        for w in words:
            w = (w or "").strip()
            if not w:
                definitions.append("")
                continue
            definition = fetch_definition_helper(w, api=api)
            definitions.append(definition or "")

        return JsonResponse({"definitions": definitions})
