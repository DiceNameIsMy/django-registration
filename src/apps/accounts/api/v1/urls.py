from django.urls import path

from rest_framework_simplejwt.views import (
    TokenRefreshView,
)

from .views import LoginView, LoginVerifyView, SignupVerifyView, SignupView

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('login/verify/', LoginVerifyView.as_view(), name='login-verify'),

    path('signup/', SignupView.as_view(), name='signup'),
    path('signup/verify/', SignupVerifyView.as_view(), name='signup'),

    # !idea: require secret question and answer to reset password

    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
