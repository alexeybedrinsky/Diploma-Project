from django.db import models
from django.utils import timezone
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from django.core.exceptions import ValidationError
from django.db import connection
from tables.models import Table


def validate_positive_guests(value):
    """
    Валидатор для проверки положительного количества гостей.
    """
    if value < 1:
        raise ValidationError("Количество гостей должно быть положительным числом.")


class Reservation(models.Model):
    """
    Модель для представления бронирования столика в ресторане.
    """
    STATUS_CHOICES = [
        ("pending", "Ожидание"),
        ("confirmed", "Подтверждено"),
        ("rejected", "Отклонено"),
        ("cancelled", "Отменено"),
    ]

    date = models.DateField(verbose_name="Дата бронирования")
    time = models.TimeField(verbose_name="Время бронирования")
    guests = models.IntegerField(validators=[validate_positive_guests], verbose_name="Количество гостей")
    phone = models.CharField(max_length=15, verbose_name="Номер телефона")
    email = models.EmailField(default="default@example.com", verbose_name="Email")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending", verbose_name="Статус")
    table = models.ForeignKey(Table, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Столик")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    class Meta:
        indexes = [
            models.Index(fields=["date", "time"]),
            models.Index(fields=["status"]),
        ]
        verbose_name = "Бронирование"
        verbose_name_plural = "Бронирования"

    def __str__(self):
        return f"Бронь на {self.date} в {self.time} для {self.guests} гостей"

    def save(self, *args, **kwargs):
        """
        Переопределенный метод сохранения.
        Проверяет, что бронирование создается не менее чем за 3 часа до желаемого времени.
        """
        if not self.pk:  # Только для новых объектов
            current_time = timezone.now()
            if (
                self.date == current_time.date() and
                (current_time + timezone.timedelta(hours=3)).time() > self.time
            ):
                raise ValueError(
                    "Бронирование должно быть сделано не менее чем за 3 часа"
                )
        super().save(*args, **kwargs)

    def cancel(self):
        """
        Отменяет бронирование и освобождает столик.
        """
        self.status = "cancelled"
        self.save()
        if self.table:
            self.table.is_available = True
            self.table.save()


@receiver(pre_delete, sender=Reservation)
def release_table(sender, instance, **kwargs):
    """
    Сигнал, который освобождает столик при удалении бронирования.
    """
    if instance.table:
        instance.table.is_available = True
        instance.table.save()


def reset_tables_availability():
    """
    Функция для сброса доступности всех столов.
    """
    Table.objects.update(is_available=True)
    print("Все столы были сброшены в статус 'доступен'")
