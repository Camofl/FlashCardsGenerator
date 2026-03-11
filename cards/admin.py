from django.contrib import admin

from .models import Deck, Flashcard


@admin.register(Flashcard)
class FlashcardAdmin(admin.ModelAdmin):
    list_display = ("front", "hidden", "created_by", "created", "updated")
    search_fields = ("front", "back", "created_by__username")
    list_filter = ("hidden", "created", "updated", "created_by")
    readonly_fields = ("created", "updated", "created_by")
    ordering = ("-created",)
    list_select_related = ("created_by",)


@admin.register(Deck)
class DeckAdmin(admin.ModelAdmin):
    list_display = ("name", "hidden", "created_by", "flashcards_count", "created",
                    "updated")
    search_fields = ("name", "flashcards__front", "flashcards__back",
                     "created_by__username")
    list_filter = ("hidden", "created", "updated", "created_by")
    readonly_fields = ("created", "updated", "created_by")
    ordering = ("-created",)
    list_select_related = ("created_by",)
    filter_horizontal = ("flashcards",)

    @admin.display(description="Flashcards")
    def flashcards_count(self, obj):
        return obj.flashcards.count()
