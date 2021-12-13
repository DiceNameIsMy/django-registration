from django.urls import path

from rest_framework_simplejwt.views import (
    TokenRefreshView,
)

from .views import LoginView, LoginVerifyView

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('login/verify/', LoginVerifyView.as_view(), name='login-verify'),

    # signup
    # confirm registration by verification code

    # !idea: require secret question and answer to reset password

    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]