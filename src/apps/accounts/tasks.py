from random import randint

from django.utils import timezone
from django.conf import settings

from config import celery_app

from .models import CustomUser, VerificationCode


@celery_app.task()
def send_sign_up_verification_code(user_id: int) -> bool:
    user: CustomUser = CustomUser.objects.filter(id=user_id).first()
    if user is None or user.verified:
        return False

    return send_verification_code(user, VerificationCode.Type.SIGN_UP)


@celery_app.task()
def send_log_in_verification_code(user_id: int) -> bool:
    user: CustomUser = CustomUser.objects.filter(id=user_id).first()
    if user is None:
        return False

    return send_verification_code(user, VerificationCode.Type.LOG_IN)


@celery_app.task()
def resend_verification_code(user_id: int, code_type: int) -> bool:
    user: CustomUser = CustomUser.objects.filter(id=user_id).first()
    if user is None:
        return False

    return send_verification_code(user, code_type)


# TODO implement sending verification code with
# differend templates according to the code type
def send_verification_code(user: CustomUser, type: int) -> bool:
    """Try to send verification code to user via his 2fa method"""
    if user.two_fa_enabled is False:
        return False

    code = randint(100000, 999999)
    valid_until = timezone.now() + settings.VERIFICATION_CODE_LIFETIME
    VerificationCode.objects.create(
        user=user,
        code=str(code),
        type=type,
        valid_until=valid_until,
    )

    if settings.DEBUG:
        print(f'Verification code for user `{user}`: {code}')

    if user.two_fa_type == CustomUser.TwoFAType.EMAIL:
        user.email_user(
            'Verification code',
            f'Code is: {code}',
        )
        return True
    else:
        # TODO: Implement
        user.sms_user()
        return False
