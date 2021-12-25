import pytest

from rest_framework.test import APIClient

from accounts.models import CustomUser


@pytest.fixture
def api_client() -> APIClient:
    return APIClient()


@pytest.fixture
def user() -> CustomUser:
    return CustomUser.objects.create_user(
        username='default_user',
        password='password',
        email='dummy@dummy.dummy',
    )


@pytest.fixture
def user_with_email_2fa() -> CustomUser:
    return CustomUser.objects.create_user(
        username='2fa_email_user',
        password='password',
        email='dummy@dummy.dummy',
        two_fa_enabled=True,
        two_fa_type=CustomUser.TwoFAType.EMAIL,
    )


@pytest.fixture
def user_with_phone_2fa() -> CustomUser:
    return CustomUser.objects.create_user(
        username='2fa_phone_user',
        password='password',
        phone='77777777777',
        two_fa_enabled=True,
        two_fa_type=CustomUser.TwoFAType.PHONE,
    )
