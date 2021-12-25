from rest_framework_simplejwt.tokens import AccessToken
from django.conf import settings


class VerificationToken(AccessToken):
    token_type = 'verification'
    lifetime = settings.VERIFICATION_TOKEN_LIFETIME
