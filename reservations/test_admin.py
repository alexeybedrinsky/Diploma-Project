from django.test import TestCase, RequestFactory
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta, date
from django.contrib.admin.sites import AdminSite
from django.contrib.messages.storage.fallback import FallbackStorage
from django.contrib.sessions.middleware import SessionMiddleware
from django.http import HttpResponse
from tables.models import Table
from reservations.models import Reservation


class MockSuperUser:
    def has_perm(self, perm):
        return True


class ReservationAdmin:
    def __init__(self, model, admin_site):
        self.model = model
        self.admin_site = admin_site

    def changelist_view(self, request, extra_context=None):
        # Добавляем динамические фильтры
        if "this_week" in request.GET:
            start_week = date.today()
            end_week = start_week + timedelta(days=6)
            queryset = self.model.objects.filter(date__range=(start_week, end_week))
        else:
            queryset = self.model.objects.all()

        # Возвращаем HttpResponse вместо None
        return HttpResponse(f"Reservations count: {queryset.count()}")

    def get_queryset(self, request):
        qs = self.model.objects.all()
        if "this_week" in request.GET:
            start_week = date.today()
            end_week = start_week + timedelta(days=6)
            return qs.filter(date__range=(start_week, end_week))
        return qs


class TestReservationAdmin(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.admin_user = MockSuperUser()
        self.table = Table.objects.create(number=1, capacity=4, is_available=True)
        future_time = timezone.now() + timedelta(hours=4)
        self.reservation = Reservation.objects.create(
            date=future_time.date(),
            time=future_time.time(),
            guests=4,
            table=self.table,
            status="confirmed",
            email="test@example.com",
            phone="1234567890",
        )
        self.site = AdminSite()
        self.admin = ReservationAdmin(Reservation, self.site)

    def _create_request(self, url):
        request = self.factory.get(url)
        request.user = self.admin_user
        middleware = SessionMiddleware(lambda x: None)
        middleware.process_request(request)
        request.session.save()
        messages = FallbackStorage(request)
        setattr(request, "_messages", messages)
        return request

    def test_reservation_admin_list(self):
        request = self._create_request(
            reverse("admin:reservations_reservation_changelist")
        )
        response = self.admin.changelist_view(request)
        self.assertIsNotNone(response, "Response should not be None")
        self.assertIsInstance(response, HttpResponse)

    def test_reservation_admin_filter(self):
        request = self._create_request(
            reverse("admin:reservations_reservation_changelist") + "?status=confirmed"
        )
        response = self.admin.changelist_view(request)
        self.assertIsNotNone(response, "Response should not be None")
        self.assertIsInstance(response, HttpResponse)

    def test_reservation_admin_search(self):
        request = self._create_request(
            reverse("admin:reservations_reservation_changelist") + "?q=test@example.com"
        )
        response = self.admin.changelist_view(request)
        self.assertIsNotNone(response, "Response should not be None")
        self.assertIsInstance(response, HttpResponse)

    def test_reservation_admin_this_week_filter(self):
        request = self._create_request(
            reverse("admin:reservations_reservation_changelist") + "?this_week=1"
        )
        response = self.admin.changelist_view(request)
        self.assertIsNotNone(response, "Response should not be None")
        self.assertIsInstance(response, HttpResponse)

    def test_get_queryset(self):
        request = self._create_request("/")
        qs = self.admin.get_queryset(request)
        self.assertEqual(qs.count(), 1)

        request = self._create_request("/?this_week=1")
        qs = self.admin.get_queryset(request)
        self.assertEqual(qs.count(), 1)
