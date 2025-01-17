from django.test import TestCase, Client
from django.urls import reverse, resolve
from django.contrib.auth.models import User
from accounts.forms import CustomUserCreationForm
from accounts.views import register, profile
from django.contrib.auth.views import LoginView, LogoutView


# Тесты для пользовательской формы регистрации
class CustomUserCreationFormTest(TestCase):
    def test_form_valid_data(self):
        """Проверяет, что форма валидна при корректных входных данных."""
        form_data = {
            "username": "testuser",
            "email": "testuser@example.com",
            "password1": "strongpassword123",
            "password2": "strongpassword123",
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertTrue(
            form.is_valid(), "Форма должна быть валидной с корректными данными"
        )

    def test_form_missing_email(self):
        """Проверяет, что форма невалидна при отсутствии email."""
        form_data = {
            "username": "testuser",
            "password1": "strongpassword123",
            "password2": "strongpassword123",
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertFalse(form.is_valid(), "Форма должна быть невалидной без email")
        self.assertIn(
            "email", form.errors, "Ошибки формы должны содержать ключ 'email'"
        )

    def test_form_password_mismatch(self):
        """Проверяет, что форма невалидна при несовпадении паролей."""
        form_data = {
            "username": "testuser",
            "email": "testuser@example.com",
            "password1": "strongpassword123",
            "password2": "differentpassword123",
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertFalse(
            form.is_valid(), "Форма должна быть невалидной при несовпадении паролей"
        )
        self.assertIn(
            "password2", form.errors, "Ошибки формы должны содержать ключ 'password2'"
        )

    def test_form_saves_user(self):
        """Проверяет, что форма корректно сохраняет пользователя."""
        form_data = {
            "username": "testuser",
            "email": "testuser@example.com",
            "password1": "strongpassword123",
            "password2": "strongpassword123",
        }
        form = CustomUserCreationForm(data=form_data)
        if form.is_valid():
            user = form.save()
            self.assertEqual(
                user.username, "testuser", "Имя пользователя должно совпадать"
            )
            self.assertEqual(
                user.email, "testuser@example.com", "Email должен совпадать"
            )
        else:
            self.fail("Форма должна быть валидной и сохранять пользователя")

# Тесты для представлений аккаунта
class AccountViewsTest(TestCase):
    def setUp(self):
        """Настройка начальных данных для тестов."""
        self.client = Client()
        self.register_url = reverse("register")
        self.profile_url = reverse("profile")
        self.login_url = reverse("login")
        self.logout_url = reverse("logout")
        self.user_data = {
            "username": "testuser",
            "email": "testuser@example.com",
            "password1": "strongpassword123",
            "password2": "strongpassword123",
        }

    def test_register_view_GET(self):
        """Проверяет GET-запрос к странице регистрации."""
        response = self.client.get(self.register_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/register.html")

    def test_register_view_POST_valid(self):
        """Проверяет успешную регистрацию пользователя."""
        response = self.client.post(self.register_url, self.user_data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username="testuser").exists())

    def test_register_view_POST_invalid(self):
        """Проверяет неудачную регистрацию с неверными данными."""
        invalid_data = self.user_data.copy()
        invalid_data["password2"] = "differentpassword"
        response = self.client.post(self.register_url, invalid_data)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username="testuser").exists())

    def test_profile_view_authenticated(self):
        """Проверяет доступ к профилю для аутентифицированного пользователя."""
        user = User.objects.create_user(username="testuser", password="12345")
        self.client.login(username="testuser", password="12345")
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/profile.html")

    def test_profile_view_not_authenticated(self):
        """Проверяет редирект на страницу входа для неаутентифицированного пользователя."""
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f"{self.login_url}?next={self.profile_url}")

    def test_login_view(self):
        """Проверяет страницу входа."""
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/login.html")

    def test_logout_view(self):
        """Проверяет процесс выхода пользователя."""
        user = User.objects.create_user(username="testuser", password="12345")
        self.client.login(username="testuser", password="12345")
        response = self.client.post(self.logout_url)
        self.assertEqual(response.status_code, 302)  # Ожидаем перенаправление
        self.assertRedirects(
            response, reverse("login")
        )  # Проверяем, что перенаправление идет на страницу входа
        self.assertFalse("_auth_user_id" in self.client.session)

# Тесты для URL-адресов аккаунта
class AccountUrlsTest(TestCase):
    def test_register_url_resolves(self):
        """Проверяет, что URL регистрации соответствует правильному представлению."""
        url = reverse("register")
        self.assertEqual(resolve(url).func, register)

    def test_profile_url_resolves(self):
        """Проверяет, что URL профиля соответствует правильному представлению."""
        url = reverse("profile")
        self.assertEqual(resolve(url).func, profile)

    def test_login_url_resolves(self):
        """Проверяет, что URL входа соответствует правильному представлению."""
        url = reverse("login")
        self.assertEqual(resolve(url).func.view_class, LoginView)

    def test_logout_url_resolves(self):
        """Проверяет, что URL выхода соответствует правильному представлению."""
        url = reverse("logout")
        self.assertEqual(resolve(url).func.view_class, LogoutView)