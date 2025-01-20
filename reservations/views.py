from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.db.models import Prefetch
from .forms import ReservationForm
from .models import Reservation
from tables.models import Table
import logging
from datetime import datetime, timedelta
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

logger = logging.getLogger(__name__)


def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('home')


@login_required
def user_reservations(request):
    reservations = Reservation.objects.filter(user=request.user)
    return render(request, 'user_reservations.html', {'reservations': reservations})


@login_required
def create_reservation(request):
    if request.method == 'POST':
        form = ReservationForm(request.POST)
        if form.is_valid():
            reservation = form.save(commit=False)
            reservation.email = request.user.email  # Автоматически устанавливаем email пользователя
            current_time = timezone.now()
            reservation_datetime = timezone.make_aware(datetime.combine(reservation.date, reservation.time))

            # Проверяем, что бронирование делается не менее чем за 3 часа
            if reservation_datetime <= current_time + timedelta(hours=3):
                form.add_error(None, 'Бронирование должно быть сделано не менее чем за 3 часа до выбранного времени')
            else:
                # Проверяем доступность столиков
                available_tables = Table.objects.filter(capacity__gte=reservation.guests, is_available=True).exists()
                if not available_tables:
                    form.add_error(None, 'К сожалению, нет доступных столиков на выбранное время')
                else:
                    reservation.save()
                    messages.success(request, 'Бронирование успешно создано.')
                    return redirect('reservation_detail', pk=reservation.pk)

        # Если форма невалидна или есть ошибки, рендерим форму снова
        return render(request, 'reservations/create_reservation.html', {'form': form})
    else:
        form = ReservationForm()
    return render(request, 'reservations/create_reservation.html', {'form': form})


@login_required
def reservation_list(request):
    reservations = Reservation.objects.select_related("table").all()
    return render(request, "reservations/reservation_list.html", {"reservations": reservations})


@login_required
def reservation_detail(request, pk):
    reservation = get_object_or_404(Reservation.objects.select_related("table"), pk=pk)
    return render(request, "reservations/reservation_detail.html", {"reservation": reservation})


@login_required
def confirm_reservation(request, pk):
    reservation = get_object_or_404(Reservation, pk=pk)
    available_tables = Table.objects.filter(capacity__gte=reservation.guests, is_available=True)

    if request.method == "POST":
        table_id = request.POST.get("table")
        if table_id:
            table = Table.objects.get(id=table_id)
            reservation.status = "confirmed"
            reservation.table = table
            reservation.save()
            table.is_available = False
            table.save()
            send_reservation_email(reservation, "подтверждено")
            confirmation_message = f"Ваше бронирование на {reservation.time} на {reservation.guests} гостей подтверждено котами! Ожидаем вас, мур-мяу"
            logger.info(f"Adding message: {confirmation_message}")
            messages.success(request, confirmation_message)
            return redirect("reservation_detail", pk=reservation.pk)
        else:
            messages.error(request, "Пожалуйста, выберите стол.")

    return render(request, "reservations/confirm_reservation.html",
                  {"reservation": reservation, "available_tables": available_tables})


@login_required
def user_reservations(request):
    reservations = (
        Reservation.objects.filter(email=request.user.email)
        .select_related("table")
        .order_by("-date", "-time")
    )
    return render(request, "reservations/user_reservations.html", {"reservations": reservations})


def send_reservation_email(reservation, status):
    subject = f"Статус вашего бронирования: {status}"
    message = f"Ваше бронирование на {reservation.date} в {reservation.time} было {status}."
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [reservation.email]
    send_mail(subject, message, from_email, recipient_list)


@login_required
def cancel_reservation(request, pk):
    reservation = get_object_or_404(Reservation, pk=pk)
    if request.method == "POST":
        reservation.cancel()
        send_reservation_email(reservation, "отменено")
        messages.success(request, "Бронирование успешно отменено.")
        return redirect("reservation_list")
    return render(request, "reservations/cancel_reservation.html", {"reservation": reservation})


def is_admin(user):
    return user.is_authenticated and user.is_staff


@user_passes_test(is_admin)
def admin_dashboard(request):
    today = timezone.now().date()
    upcoming_reservations = (
        Reservation.objects.filter(date__gte=today)
        .select_related("table")
        .order_by("date", "time")
    )
    available_tables = Table.objects.filter(is_available=True)

    context = {
        "upcoming_reservations": upcoming_reservations,
        "available_tables": available_tables,
    }
    return render(request, "reservations/admin_dashboard.html", context)


def home(request):
    return render(request, "home.html")


@require_GET
def check_availability(request):
    date = request.GET.get("date")
    time = request.GET.get("time")
    guests = request.GET.get("guests")

    if not all([date, time, guests]):
        return JsonResponse({"error": "Не все параметры предоставлены"}, status=400)

    # Проверяем, что бронирование делается не менее чем за 3 часа
    reservation_datetime = timezone.make_aware(
        datetime.combine(datetime.strptime(date, "%Y-%m-%d").date(), datetime.strptime(time, "%H:%M").time()))
    if reservation_datetime <= timezone.now() + timedelta(hours=3):
        return JsonResponse({"available": False,
                             "error": "Бронирование должно быть сделано не менее чем за 3 часа до выбранного времени"})

    available_tables = Table.objects.filter(capacity__gte=int(guests), is_available=True).exists()
    return JsonResponse({"available": available_tables})


def feedback(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        message = request.POST.get("message")

        logger.info(f"Получена обратная связь: Имя: {name}, Email: {email}, Сообщение: {message}")

        try:
            send_mail(
                f"Обратная связь от {name}",
                message,
                settings.EMAIL_HOST_USER,
                [settings.DEFAULT_FROM_EMAIL],
                fail_silently=False,
            )
            logger.info("Электронное письмо успешно отправлено")
            messages.success(request, "Ваше сообщение успешно отправлено!")
        except Exception as e:
            logger.error(f"Ошибка при отправке электронного письма: {str(e)}")
            messages.error(request, "Произошла ошибка при отправке сообщения. Пожалуйста, попробуйте позже.")

        return redirect("home")
    return redirect("home")


def about(request):
    return render(request, "about.html")
