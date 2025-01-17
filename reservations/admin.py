from django.contrib import admin
from django.utils import timezone
from datetime import timedelta
from .models import Reservation
from django.urls import path
from django.shortcuts import redirect
from django.contrib import messages
from .models import reset_tables_availability


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    """
    Административный интерфейс для управления бронированиями.
    """
    list_display = ("date", "time", "guests", "status", "table", "email")
    list_filter = ("status", "date")
    search_fields = ("phone", "email")
    actions = ["cancel_reservations"]

    def get_urls(self):
        """
        Добавляет пользовательский URL для сброса доступности столов.
        """
        urls = super().get_urls()
        custom_urls = [
            path("reset-tables/", self.reset_tables, name="reset_tables"),
        ]
        return custom_urls + urls

    def reset_tables(self, request):
        """
        Сбрасывает доступность всех столов и отображает сообщение об успехе.
        """
        reset_tables_availability()
        self.message_user(
            request, "Все столы были сброшены в статус 'доступен'", messages.SUCCESS
        )
        return redirect("..")

    def cancel_reservations(self, request, queryset):
        """
        Отменяет выбранные бронирования и отображает сообщение об успехе.
        """
        for reservation in queryset:
            reservation.cancel()
        self.message_user(
            request, f"{queryset.count()} бронирований было отменено", messages.SUCCESS
        )
    cancel_reservations.short_description = "Отменить выбранные бронирования"

    def get_queryset(self, request):
        """
        Возвращает queryset бронирований, с возможностью фильтрации недавних бронирований.
        """
        qs = super().get_queryset(request)
        if request.GET.get("recent"):
            return qs.filter(
                created_at__gte=timezone.now() - timedelta(hours=1)
            ).order_by("-created_at")
        return qs

    def changelist_view(self, request, extra_context=None):
        """
        Настраивает отображение списка бронирований в админке.
        """
        extra_context = extra_context or {}
        if request.GET.get("recent"):
            extra_context["title"] = "Недавние бронирования (за последний час)"
        extra_context["show_reset_tables"] = True
        return super().changelist_view(request, extra_context=extra_context)
