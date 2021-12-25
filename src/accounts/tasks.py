from config import celery_app

from .models import CustomUser, VerificationCode
from .sender import VerificationCodeSender


@celery_app.task()
def send_sign_up_verification_code(user_id: int) -> int:
    user = CustomUser.objects.filter(id=user_id).first()
    if user is None or user.verified:
        return False

    return send_verification_code(user, VerificationCode.Type.SIGN_UP)


@celery_app.task()
def send_log_in_verification_code(user_id: int) -> int:
    user = CustomUser.objects.filter(id=user_id).first()
    if user is None:
        return False

    return send_verification_code(user, VerificationCode.Type.LOG_IN)


@celery_app.task()
def resend_verification_code(user_id: int, code_type: int) -> int:
    user = CustomUser.objects.filter(id=user_id).first()
    if user is None:
        return False

    return send_verification_code(user, code_type)


def send_verification_code(user: CustomUser, type: int) -> int:
    """Try to send verification code to user via his 2fa method"""
    if user.two_fa_enabled is False:
        return False

    # TODO add try-except & log errors
    sender = VerificationCodeSender(user, type)
    sender.send()

    return int(sender.code.code)
