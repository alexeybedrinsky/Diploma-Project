import os
import django
from django.conf import settings
from django.test import TestCase
from tables.models import Table

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "restaurant_booking.settings")
django.setup()


class TableModelTest(TestCase):
    def setUp(self):
        """Создаем несколько столов для тестов"""
        self.table_1 = Table.objects.create(number=1, capacity=4, is_available=True)
        self.table_2 = Table.objects.create(number=2, capacity=2, is_available=True)
        self.table_3 = Table.objects.create(number=3, capacity=6, is_available=False)

    def test_table_creation(self):
        """Проверяем создание стола"""
        table = Table.objects.get(number=1)
        self.assertEqual(table.capacity, 4)
        self.assertTrue(table.is_available)

    def test_table_availability(self):
        """Проверка доступности столов"""
        table = Table.objects.get(number=3)
        self.assertFalse(table.is_available)

    def test_table_capacity(self):
        """Проверка вместимости столов"""
        table = Table.objects.get(number=2)
        self.assertEqual(table.capacity, 2)

    def test_table_str(self):
        """Проверка метода __str__"""
        self.assertEqual(str(self.table_1), "Стол №1 (вместимость: 4)")
        self.assertEqual(str(self.table_2), "Стол №2 (вместимость: 2)")
        self.assertEqual(str(self.table_3), "Стол №3 (вместимость: 6)")
