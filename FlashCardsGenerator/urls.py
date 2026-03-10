from django.contrib import admin
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path, include
from django.views.generic import RedirectView
from cards.views.signup import SignUpView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('flashcards/', include("cards.urls")),
    path('', RedirectView.as_view(url='/flashcards/')),
    path("accounts/login/", LoginView.as_view(
        template_name="cards/registration/login.html",
        redirect_authenticated_user=True,
    ), name="login"),
    path("accounts/logout/", LogoutView.as_view(), name="logout"),
    path("accounts/signup/", SignUpView.as_view(), name="signup"),
]
