import json

from django import forms
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.forms import formset_factory
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView, \
    DeleteView

from ..forms import BulkFlashcardRowForm
from ..models import Flashcard
from ..services import DictionaryAPI, DefinitionService, InvalidRequestError, \
    UnsupportedAPIError


class FlashcardListView(ListView):
    model = Flashcard
    template_name = "cards/flashcards/list.html"
    context_object_name = "flashcards"


class FlashcardDetailView(DetailView):
    model = Flashcard
    template_name = "cards/flashcards/detail.html"
    context_object_name = "flashcard"


class OwnerRequiredMixin(LoginRequiredMixin):
    def get_queryset(self):
        return super().get_queryset().filter(created_by=self.request.user)


class FlashcardCreateView(LoginRequiredMixin, CreateView):
    model = Flashcard
    template_name = "cards/flashcards/form.html"
    fields = ["front", "back", "hidden"]
    success_url = reverse_lazy("flashcard-list")
    widgets = {"hidden": forms.CheckboxInput()}

    def form_valid(self, form):
        flashcard = form.save(commit=False)
        flashcard.created_by = self.request.user

        if not flashcard.back and flashcard.front:
            definition = DictionaryAPI.get_definition(flashcard.front)
            if definition:
                flashcard.back = definition
            else:
                flashcard.back = "[No definition found]"

        flashcard.save()
        self.object = flashcard
        return redirect(self.get_success_url())


class FlashcardUpdateView(OwnerRequiredMixin, UpdateView):
    model = Flashcard
    template_name = "cards/flashcards/form.html"
    fields = ["front", "back", "hidden"]
    success_url = reverse_lazy("flashcard-list")
    widgets = {
        "hidden": forms.CheckboxInput(),
    }


class FlashcardDeleteView(OwnerRequiredMixin, DeleteView):
    model = Flashcard
    template_name = "cards/flashcards/confirm_delete.html"
    success_url = reverse_lazy("flashcard-list")


class GetDefinitionView(LoginRequiredMixin, View):
    http_method_names = ["post"]

    def post(self, request, *args, **kwargs):
        if request.content_type != "application/json":
            return JsonResponse(
                {"error": "Unsupported content type. Expected application/json"},
                status=415,
            )

        try:
            payload = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON body"}, status=400)

        try:
            definition = DefinitionService.fetch_definition(
                word_raw=payload.get("word", ""),
                api=payload.get("api"),
                language=payload.get("language", "en"),
            )
        except InvalidRequestError as exc:
            return JsonResponse({"error": str(exc)}, status=400)
        except UnsupportedAPIError as exc:
            return JsonResponse({"error": str(exc)}, status=400)

        if not definition:
            return JsonResponse({"error": "No definition found"}, status=404)

        return JsonResponse({"definition": definition})



class BulkPasteView(LoginRequiredMixin, View):
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


class BulkReviewCreateView(LoginRequiredMixin, View):
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


class BulkGetDefinitionsView(LoginRequiredMixin, View):
    http_method_names = ["post"]

    def post(self, request, *args, **kwargs):
        if request.content_type != "application/json":
            return JsonResponse(
                {"error": "Unsupported content type. Expected application/json"},
                status=415,
            )

        try:
            payload = json.loads(request.body or "{}")
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON body"}, status=400)

        words = payload.get("words", [])
        api = payload.get("api")
        language = payload.get("language", "en")

        if not isinstance(words, list) or not words:
            return JsonResponse({"error": "No words provided"}, status=400)

        if api and not DictionaryAPI.has_provider(api):
            return JsonResponse({"error": f"Unsupported API: {api}"}, status=400)

        definitions: list[str] = []

        for raw_word in words:
            word = (raw_word or "").strip()
            if not word:
                definitions.append("")
                continue

            try:
                definition = DefinitionService.fetch_definition(
                    word_raw=word,
                    api=api,
                    language=language,
                )
            except InvalidRequestError:
                definitions.append("")
                continue
            except UnsupportedAPIError as exc:
                return JsonResponse({"error": str(exc)}, status=400)

            definitions.append(definition or "")

        return JsonResponse({
            "definitions": definitions,
            "api": (api or DefinitionService.DEFAULT_API),
            "language": (language or "en").lower(),
        })
