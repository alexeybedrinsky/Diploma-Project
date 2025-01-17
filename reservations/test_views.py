from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from reservations.models import Reservation
from tables.models import Table
from django.utils import timezone
from datetime import timedelta
from unittest.mock import patch
from django.core import mail


class ReservationViewsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="testuser", password="12345")
        self.table = Table.objects.create(number=1, capacity=4, is_available=True)
        future_time = timezone.now() + timedelta(hours=4)
        self.reservation = Reservation.objects.create(
            date=future_time.date(),
            time=future_time.time(),
            guests=2,
            email="test@example.com",
            phone="1234567890",
            table=self.table,
        )

    def test_create_reservation_view(self):
        url = reverse("create_reservation")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "reservations/create_reservation.html")

    def test_create_reservation_post_success(self):
        url = reverse("create_reservation")
        data = {
            "date": (timezone.now() + timedelta(days=1)).date(),
            "time": "12:00",
            "guests": 2,
            "email": "test@example.com",
            "phone": "1234567890",
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Reservation.objects.filter(email="test@example.com").exists())

    def test_create_reservation_post_no_tables(self):
        Table.objects.all().delete()
        url = reverse("create_reservation")
        data = {
            "date": (timezone.now() + timedelta(days=1)).date(),
            "time": "12:00",
            "guests": 2,
            "email": "test@example.com",
            "phone": "1234567890",
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response, "К сожалению, нет доступных столиков на это время."
        )

    def test_reservation_list_view(self):
        self.client.login(username="testuser", password="12345")
        url = reverse("reservation_list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "reservations/reservation_list.html")

    def test_reservation_detail_view(self):
        self.client.login(username="testuser", password="12345")
        url = reverse("reservation_detail", args=[self.reservation.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "reservations/reservation_detail.html")

    def test_cancel_reservation_view(self):
        self.client.login(username="testuser", password="12345")
        url = reverse("cancel_reservation", args=[self.reservation.pk])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.reservation.refresh_from_db()
        self.assertEqual(self.reservation.status, "cancelled")

    def test_user_reservations_view(self):
        self.client.login(username="testuser", password="12345")
        url = reverse("user_reservations")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "reservations/user_reservations.html")

    @patch("django.utils.timezone.now")
    def test_admin_dashboard_view(self, mock_now):
        mock_now.return_value = timezone.make_aware(
            timezone.datetime(2023, 1, 1, 12, 0, 0)
        )
        admin_user = User.objects.create_superuser(
            "admin", "admin@example.com", "adminpass"
        )
        self.client.login(username="admin", password="adminpass")
        url = reverse("admin_dashboard")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "reservations/admin_dashboard.html")

    def test_confirm_reservation(self):
        self.client.login(username="testuser", password="12345")
        url = reverse("confirm_reservation", args=[self.reservation.pk])
        data = {"table": self.table.id}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        self.reservation.refresh_from_db()
        self.assertEqual(self.reservation.status, "confirmed")

    def test_check_availability(self):
        url = reverse("check_availability")
        data = {
            "date": (timezone.now() + timedelta(days=1)).strftime("%Y-%m-%d"),
            "time": "12:00",
            "guests": 2,
        }
        response = self.client.get(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {"available": True})

    @patch("reservations.views.send_mail")
    def test_feedback(self, mock_send_mail):
        url = reverse("feedback")
        data = {
            "name": "Test User",
            "email": "test@example.com",
            "message": "Test feedback message",
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(mock_send_mail.called)

    def test_about_page(self):
        url = reverse("about")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "about.html")
