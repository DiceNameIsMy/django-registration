from random import randint

from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.conf import settings


class CustomUser(AbstractUser):
    class TwoFAType(models.IntegerChoices):
        EMAIL = 1, 'Email'
        PHONE = 2, 'Phone'

    phone = models.CharField(max_length=20, blank=True)

    is_verified = models.BooleanField(default=False)
    two_fa_enabled = models.BooleanField(default=False)
    two_fa_type = models.PositiveSmallIntegerField(choices=TwoFAType.choices, null=True, blank=True)

    REQUIRED_FIELDS = []

    class Meta:
        db_table = 'user'
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self) -> str:
        return self.username

    def sms_user(self, message):
        """Send SMS to user"""
        raise NotImplementedError('SMS sending is not implemented')

    def verify_user(self, save: bool = True):
        self.last_login = timezone.now()
        self.is_verified = True

        if save:
            self.save(update_fields=['last_login', 'is_verified'])


class VerificationCodeManager(models.Manager):
    def create_for_user(self, user: CustomUser, jti: str, code_type: int):
        """Create verification code for user"""
        code = str(randint(100000, 999999))
        valid_until = timezone.now() + settings.VERIFICATION_CODE_LIFETIME
        return self.create(
            user=user,
            code=code,
            jwt_jti=jti,
            type=code_type,
            valid_until=valid_until,
        )


class VerificationCode(models.Model):
    class Type(models.IntegerChoices):
        SIGN_UP = 1, 'Sign Up'
        LOG_IN = 2, 'Log In'

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    type = models.PositiveSmallIntegerField(choices=Type.choices)
    code = models.PositiveIntegerField(
        validators=(MaxValueValidator(999999), MinValueValidator(100000)),
    )
    # JWT JTI is stored to keep verf code and client paired
    # it's done to prevent same user but
    # different client from using the same code
    jwt_jti = models.CharField(max_length=32)

    created_at = models.DateTimeField(auto_now_add=True)
    valid_until = models.DateTimeField()
    is_used = models.BooleanField(default=False)

    objects = VerificationCodeManager()

    class Meta:
        # TODO make indexes
        db_table = 'verification_code'
        verbose_name = 'Verification Code'
        verbose_name_plural = 'Verification Codes'

    def use(self) -> bool:
        if not self.is_used:
            self.is_used = True
            self.save(update_fields=['is_used'])
            return True
        else:
            return False
