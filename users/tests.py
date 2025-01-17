from django.test import TestCase
from django.contrib.auth.models import User
from users.models import Profile


class ProfileModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="testpassword"
        )
        self.profile = Profile.objects.create(user=self.user, is_admin=True)

    def test_profile_creation(self):
        """Тест на создание профиля и связь с пользователем"""
        self.assertEqual(self.profile.user.username, "testuser")
        self.assertTrue(self.profile.is_admin)

    def test_is_admin_default_value(self):
        """Тест на значение по умолчанию для is_admin"""
        user2 = User.objects.create_user(username="user2", password="password")
        profile2 = Profile.objects.create(user=user2)
        self.assertFalse(profile2.is_admin)

    def test_profile_str(self):
        """Тест на строковое представление профиля"""
        self.assertEqual(str(self.profile), f"Профиль {self.user.username}")
