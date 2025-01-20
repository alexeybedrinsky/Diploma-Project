
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from .forms import CustomUserCreationForm

def register(request):
    """
    Обрабатывает регистрацию нового пользователя.
    При GET-запросе отображает форму регистрации.
    При POST-запросе создает нового пользователя, если данные валидны.
    """
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Регистрация прошла успешно!')
            return redirect("home")
        else:
            messages.error(request, 'Ошибка при регистрации. Пожалуйста, проверьте введенные данные.')
    else:
        form = CustomUserCreationForm()
    return render(request, "accounts/register.html", {"form": form})

def login_view(request):
    """
    Обрабатывает вход пользователя в систему.
    """
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Добро пожаловать, {username}!")
                return redirect("home")
        else:
            messages.error(request, "Неверное имя пользователя или пароль.")
    else:
        form = AuthenticationForm()
    return render(request, "accounts/login.html", {"form": form})

@login_required
def profile(request):
    """
    Отображает профиль пользователя.
    Доступ к этому представлению имеют только аутентифицированные пользователи.
    """
    return render(request, "accounts/profile.html")
