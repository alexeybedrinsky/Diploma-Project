from django.contrib import admin
from .models import Table


@admin.register(Table)
class TableAdmin(admin.ModelAdmin):
    """
    Административный интерфейс для управления столиками ресторана.
    """
    list_display = ("number", "capacity", "is_available")
    list_filter = ("is_available", "capacity")
    ordering = ("-capacity", "number")  # Сортировка по вместимости (по убыванию), затем по номеру

    def get_ordering(self, request):
        """
        Определяет порядок сортировки столиков в зависимости от параметров запроса.

        Args:
            request: HTTP-запрос

        Returns:
            tuple: Кортеж с полями для сортировки
        """
        if "capacity" in request.GET:
            return ("-capacity",)
        elif "number" in request.GET:
            return ("number",)
        return super().get_ordering(request)
