from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

urlpatterns = [
    path("setup/", views.SecuritySetupView.as_view(), name="security-setup"),
    path("unlock/", views.SecurityUnlockView.as_view(), name="security-unlock"),
    path("recover/", views.SecurityRecoverView.as_view(), name="security-recover"),
    path("change-pin/", views.ChangePinView.as_view(), name="security-change-pin"),
    path("status/", views.security_status, name="security-status"),
    path("refresh/", TokenRefreshView.as_view(), name="security-refresh"),
]
