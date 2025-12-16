from django import forms
from .models import Deck


class BulkFlashcardRowForm(forms.Form):
    front = forms.CharField(max_length=255)
    back = forms.CharField(widget=forms.Textarea(attrs={"rows": 10}))
    hidden = forms.BooleanField(required=False, initial=False)


class DeckForm(forms.ModelForm):
    class Meta:
        model = Deck
        fields = ["name", "hidden", "flashcards"]
        widgets = {
            "name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "e.g. Biology - Chapter 1",
            }),
            "hidden": forms.CheckboxInput(),
            "flashcards": forms.CheckboxSelectMultiple(),
        }
