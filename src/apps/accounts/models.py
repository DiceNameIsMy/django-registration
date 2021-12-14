from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class CustomUser(AbstractUser):
    class TwoFAType(models.IntegerChoices):
        EMAIL = 1, 'Email'
        PHONE = 2, 'Phone'

    phone = models.CharField(max_length=20, blank=True)

    verified = models.BooleanField(default=False)
    two_fa_enabled = models.BooleanField(default=False)
    two_fa_type = models.PositiveSmallIntegerField(choices=TwoFAType.choices, null=True, blank=True)

    REQUIRED_FIELDS = ['email', 'phone']

    class Meta:
        db_table = 'user'
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self) -> str:
        return self.username

    def sms_user(self, message):
        """Send SMS to user"""
        # TODO: Implement

    def verify_user(self, save: bool = True):
        self.last_login = timezone.now()
        self.verified = True

        if save:
            self.save(update_fields=['last_login', 'verified'])
