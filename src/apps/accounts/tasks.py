from random import randint

from django.core.cache import caches
from django.conf import settings

from config import celery_app

from .models import CustomUser

cache = caches['default']


@celery_app.task()
def send_verification_code(user_id: int) -> bool:
    user: CustomUser = CustomUser.objects.filter(id=user_id).first()
    if user is None:
        return False

    code = randint(100000, 999999)
    cache.set(user_id, code, timeout=settings.VERIFICATION_CODE_LIFETIME.seconds)

    if user.two_fa_type == CustomUser.TwoFAType.EMAIL:
        user.email_user(
            'Verification code',
            f'Code is: {code}',
        )
        return True
    else:
        user.sms_user()
        return False
