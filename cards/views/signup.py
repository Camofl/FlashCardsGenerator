from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.views.generic.edit import FormView


class SignUpView(FormView):
    template_name = "cards/registration/signup.html"
    form_class = UserCreationForm
    success_url = reverse_lazy("flashcard-list")

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return super().form_valid(form)
