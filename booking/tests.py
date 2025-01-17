from django.test import TestCase
from booking.models import Booking
from tables.models import Table
from django.utils import timezone
from datetime import timedelta
from django.core.exceptions import ValidationError
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "restaurant_booking.settings")


class BookingModelTest(TestCase):

    def setUp(self):
        # Создаем столы для бронирования
        self.table_1 = Table.objects.create(number=1, capacity=4, is_available=True)
        self.table_2 = Table.objects.create(number=2, capacity=2, is_available=True)
        self.table_3 = Table.objects.create(number=3, capacity=6, is_available=True)

        # Устанавливаем время бронирования минимум через 3 часа
        future_time = timezone.now() + timedelta(hours=3)

        # Создаем бронирование для теста
        self.booking = Booking.objects.create(
            guest_name="John Doe",
            table=self.table_1,
            booking_date=future_time,
            guests_count=4,
        )

    def test_booking_creation(self):
        """Тест на создание бронирования"""
        booking = Booking.objects.get(guest_name="John Doe")
        self.assertEqual(booking.guest_name, "John Doe")
        self.assertEqual(booking.table.number, 1)
        self.assertEqual(booking.guests_count, 4)

    def test_booking_time_check(self):
        """Тест на проверку времени бронирования"""
        future_time = timezone.now() + timedelta(hours=2)  # Время меньше 3 часов

        # Проверка, что при создании бронирования выбрасывается ValidationError
        with self.assertRaises(ValidationError):
            # Попытка создать бронирование с временем меньше 3 часов
            booking = Booking(
                table=self.table_2,
                guest_name="Jane Doe",
                booking_date=future_time,
                guests_count=4,
            )
            booking.full_clean()  # Проверяем валидацию вручную (полная очистка данных)

        # Теперь проверим, что вызов метода clean() для уже созданного объекта вызовет исключение
        booking = Booking(
            table=self.table_2,
            guest_name="Jane Doe",
            booking_date=future_time,
            guests_count=4,
        )
        with self.assertRaises(ValidationError):
            booking.clean()  # Проверим вызов clean() вручную

    def test_booking_str(self):
        """Тест на строковое представление бронирования"""
        self.assertEqual(
            str(self.booking),
            f"Бронирование для {self.booking.guest_name} на {self.booking.booking_date}",
        )
