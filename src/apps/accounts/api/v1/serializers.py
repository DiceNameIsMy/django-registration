from django.core.cache import caches

from rest_framework import serializers

from rest_framework_simplejwt.serializers import PasswordField
from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.models import CustomUser
from apps.accounts.tokens import VerificationToken


cache = caches['default']


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = PasswordField()

    _user: CustomUser

    def validate(self, attrs):
        self._user: CustomUser = CustomUser.objects.filter(username=attrs['username']).first()

        if (self._user is None) or (not self._user.check_password(attrs['password'])):
            raise serializers.ValidationError('Invalid username or password')

        return attrs

    def get_user(self) -> CustomUser:
        return self._user

    def get_token_pair(self) -> dict:
        token = RefreshToken.for_user(self._user)
        return {
            'refresh': str(token),
            'access': str(token.access_token),
        }
    
    def get_verification_token(self) -> dict:
        token = VerificationToken.for_user(self._user)
        return {
            'method': self._user.two_fa_type,
            'verfication': str(token),
        }


class LoginVerifySerializer(serializers.Serializer):
    """ Two factor authentication code serializer """
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    code = serializers.CharField()

    def validate(self, attrs):
        code = cache.get(attrs['user'].pk)

        if attrs['code'] != code:
            raise serializers.ValidationError('Invalid code')

        return attrs
    
    def get_token_pair(self) -> dict:
        token = RefreshToken.for_user(self.validated_data['user'])
        return {
            'refresh': str(token),
            'access': str(token.access_token),
        }
