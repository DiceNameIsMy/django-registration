from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken

from .tokens import VerificationToken


class VerificationJWTAuthentication(JWTAuthentication):
    def get_validated_token(self, raw_token):
        try:
            return VerificationToken(raw_token)
        except TokenError as e:
            raise InvalidToken(
                {
                    'detail': 'Given token not valid for any token type',
                    'messages': {
                        'token_class': VerificationToken.__name__,
                        'token_type': VerificationToken.token_type,
                        'message': e.args[0],
                    },
                }
            )
