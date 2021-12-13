from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    class TwoFAType(models.IntegerChoices):
        EMAIL = 1, 'Email'
        PHONE = 2, 'Phone'

    phone = models.CharField(max_length=20, blank=True)

    two_fa_enabled = models.BooleanField(default=False)
    two_fa_type = models.PositiveSmallIntegerField(choices=TwoFAType.choices, null=True)

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
    