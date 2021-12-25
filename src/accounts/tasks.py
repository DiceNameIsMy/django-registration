from config import celery_app

from .models import CustomUser
from .sender import VerificationCodeSender


@celery_app.task()
def send_verification_code(user_id: int, jti: str, code_type: int) -> int:
    user = CustomUser.objects.get(id=user_id)
    sender = VerificationCodeSender(user, jti, code_type)
    sender.send()

    return sender.verification_code.code
