from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class CustomUserCreationForm(UserCreationForm):
    """
    Пользовательская форма создания пользователя, расширяющая стандартную форму Django.
    Добавляет обязательное поле email.
    """

    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def save(self, commit=True):
        """
        Сохраняет пользователя, добавляя email к стандартным полям.

        Args:
            commit (bool): Если True, сохраняет пользователя в базу данных.

        Returns:
            User: Созданный объект пользователя.
        """
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user