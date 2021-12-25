from django.conf import settings

from .models import VerificationCode, CustomUser


class VerificationCodeSender:
    dummy: bool = settings.DUMMY_CODE_SENDER
    _verification_code: VerificationCode = None

    def __init__(self, user: CustomUser, jti: str, code_type: int):
        self.user: CustomUser = user
        self.jti: str = jti
        self.code_type: int = code_type
        self.sending_method: int = self.user.two_fa_type

    @property
    def verification_code(self) -> VerificationCode:
        if self._verification_code is None:
            self._verification_code = VerificationCode.objects.create_for_user(
                self.user,
                self.jti,
                self.code_type,
            )
        return self._verification_code

    def send(self):
        """Send verification code to user"""
        if self.dummy:
            self._send_dummy_code()
        elif self.user.two_fa_type == CustomUser.TwoFAType.EMAIL:
            self._send_email_code()
        elif self.user.two_fa_type == CustomUser.TwoFAType.PHONE:
            self._send_phone_code()

    # TODO load message template from settings
    def _send_email_code(self):
        self.user.email_user(
            f'Verification code is: {self.verification_code.code}',
            '',
        )

    def _send_phone_code(self):
        self.user.sms_user(f'Verification code is: {self.verification_code.code}')

    def _send_dummy_code(self):
        print(f"Sending dummy code to {self.user.username}")
        print(f"Dummy code is: {self.verification_code.code}")
