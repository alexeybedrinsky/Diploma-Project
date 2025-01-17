from django.urls import path
from . import views

urlpatterns = [
    path("create/", views.create_reservation, name="create_reservation"),
    path("list/", views.reservation_list, name="reservation_list"),
    path("<int:pk>/", views.reservation_detail, name="reservation_detail"),
    path("<int:pk>/confirm/", views.confirm_reservation, name="confirm_reservation"),
    path("<int:pk>/cancel/", views.cancel_reservation, name="cancel_reservation"),
    path("admin-dashboard/", views.admin_dashboard, name="admin_dashboard"),
    path("check-availability/", views.check_availability, name="check_availability"),
    path("my-reservations/", views.user_reservations, name="user_reservations"),
    path("feedback/", views.feedback, name="feedback"),
    path("about/", views.about, name="about"),
]
