from rest_framework_simplejwt.tokens import AccessToken

from django.conf import settings


class VerificationToken(AccessToken):
    token_type = settings.VERIFICATION_TOKEN_TYPE
