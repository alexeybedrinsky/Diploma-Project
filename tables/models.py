from django.db import models


class Table(models.Model):
    number = models.IntegerField(unique=True)
    capacity = models.IntegerField()
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return f"Стол №{self.number} (вместимость: {self.capacity})"
