from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm


def register(request):
    """
    Обрабатывает регистрацию нового пользователя.

    При GET-запросе отображает форму регистрации.
    При POST-запросе создает нового пользователя, если данные валидны.

    Args:
        request: объект HttpRequest

    Returns:
        HttpResponse: отрендеренная страница регистрации или редирект на главную
    """
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Автоматически входим пользователя после регистрации
            return redirect("home")
    else:
        form = CustomUserCreationForm()
    return render(request, "accounts/register.html", {"form": form})


@login_required
def profile(request):
    """
    Отображает профиль пользователя.

    Доступ к этому представлению имеют только аутентифицированные пользователи.

    Args:
        request: объект HttpRequest

    Returns:
        HttpResponse: отрендеренная страница профиля
    """
    return render(request, "accounts/profile.html")