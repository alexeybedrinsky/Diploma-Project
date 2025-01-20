from django.contrib import admin
from django.urls import path, include
from reservations import views as reservation_views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("reservations/", include("reservations.urls")),
    path("tables/", include("tables.urls")),
    path("users/", include("users.urls")),
    path('accounts/', include('django.contrib.auth.urls')),
    path("accounts/", include("accounts.urls")),
    path("", reservation_views.home, name="home"),
]
