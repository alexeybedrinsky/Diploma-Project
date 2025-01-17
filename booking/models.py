from django.db import models
from django.core.exceptions import ValidationError
from datetime import timedelta
from django.utils import timezone

class Booking(models.Model):
    """
    Модель для представления бронирования столика в ресторане.
    """
    guest_name = models.CharField(max_length=100, verbose_name="Имя гостя")
    table = models.ForeignKey("tables.Table", on_delete=models.CASCADE, verbose_name="Столик")
    booking_date = models.DateTimeField(verbose_name="Дата и время бронирования")
    guests_count = models.IntegerField(verbose_name="Количество гостей")

    def clean(self):
        """
        Проверяет валидность данных бронирования.
        Убеждается, что бронирование делается не менее чем за 3 часа до желаемого времени.
        """
        if self.booking_date < timezone.now() + timedelta(hours=3):
            raise ValidationError(
                "Бронирование должно быть сделано не менее чем за 3 часа"
            )

    def save(self, *args, **kwargs):
        """
        Переопределенный метод сохранения.
        Вызывает метод clean() перед сохранением для валидации данных.
        """
        self.clean()  # Вызов чистки данных перед сохранением
        super().save(*args, **kwargs)

    def __str__(self):
        """
        Возвращает строковое представление объекта бронирования.
        """
        return f"Бронирование для {self.guest_name} на {self.booking_date}"

    class Meta:
        verbose_name = "Бронирование"
        verbose_name_plural = "Бронирования"