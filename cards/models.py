from django.db import models

from django_currentuser.db.models import CurrentUserField


class Flashcard(models.Model):
    front = models.TextField()
    back = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    created_by = CurrentUserField(editable=False)
    hidden = models.BooleanField(default=False)

    def __str__(self):
        return self.front


class Deck(models.Model):
    name = models.TextField()
    flashcards = models.ManyToManyField(Flashcard)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    created_by = CurrentUserField(editable=False)
    hidden = models.BooleanField(default=False)

    def __str__(self):
        return self.name
