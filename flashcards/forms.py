from django import forms


class BulkFlashcardRowForm(forms.Form):
    front = forms.CharField(max_length=255)
    back = forms.CharField(required=False, widget=forms.Textarea(attrs={"rows": 2}))
    hidden = forms.BooleanField(required=False, initial=False)
