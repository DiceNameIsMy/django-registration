from random import randint

from django.utils import timezone
from django.conf import settings

from .models import VerificationCode, CustomUser


class VerificationCodeSender:
    dummy: bool = settings.DUMMY_CODE_SENDER

    def __init__(self, user: CustomUser, code_type: int):
        self.user = user
        self.code = self.create_code(code_type)

        self.sending_method = self.user.two_fa_type

    def send(self):
        """Send verification code to user"""
        if self.dummy:
            self.send_dummy_code()
        elif self.user.two_fa_type == CustomUser.TwoFAType.EMAIL:
            self.send_email_code()
        elif self.user.two_fa_type == CustomUser.TwoFAType.PHONE:
            self.send_phone_code()

    def create_code(self, code_type) -> VerificationCode:
        code = randint(100000, 999999)
        valid_until = timezone.now() + settings.VERIFICATION_CODE_LIFETIME
        return VerificationCode.objects.create(
            user=self.user,
            code=str(code),
            type=code_type,
            valid_until=valid_until,
        )

    # TODO load message template from settings
    def send_email_code(self):
        self.user.email_user(
            f'Verification code is: {self.code.code}',
            '',
        )

    def send_phone_code(self):
        self.user.sms_user(f'Verification code is: {self.code.code}')

    def send_dummy_code(self):
        print(f"Sending dummy code to {self.user.username}")
        print(f"Dummy code is: {self.code.code}")
