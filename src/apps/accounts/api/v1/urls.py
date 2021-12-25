from django.urls import path

from rest_framework_simplejwt.views import (
    TokenRefreshView,
)

from .views import (
    LoginView,
    LoginVerifyView,
    ResendVerificationCodeView,
    SignupVerifyView,
    SignupView,
    ProfileView,
)

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('login/verify/', LoginVerifyView.as_view(), name='login-verify'),

    path('signup/', SignupView.as_view(), name='signup'),
    path('signup/verify/', SignupVerifyView.as_view(), name='signup-verify'),

    path('code/resend/', ResendVerificationCodeView.as_view(), name='resend-code'),

    path('profile/', ProfileView.as_view(), name='profile'),
    # path('profile/2fa/', ProfileView.as_view(), name='2fa-settings'),
    # path('profile/change-password/', ProfileView.as_view(), name='chage-password'),
    # path('profile/reset-password/', ProfileView.as_view(), name='reset-password'),

    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
