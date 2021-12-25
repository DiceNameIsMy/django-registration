from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from rest_framework_simplejwt.tokens import RefreshToken

from .tokens import VerificationToken


class VerificationJWTAuthentication(JWTAuthentication):
    """Authentication for tokens with type 'verification'
    used to verificate user via 2FA
    """

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


# Common token related functions
def get_token_pair(user) -> dict:
    token = RefreshToken.for_user(user)
    return {
        'refresh': str(token),
        'access': str(token.access_token),
    }


def get_verification_token(user) -> VerificationToken:
    return VerificationToken.for_user(user)
