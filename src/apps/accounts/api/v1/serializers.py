from django.core.cache import caches

from rest_framework import serializers

from rest_framework_simplejwt.serializers import PasswordField

from apps.accounts.models import CustomUser
from apps.accounts.authentication import get_token_pair, get_verification_token


cache = caches['default']


class VerifyCodeSerializer(serializers.Serializer):
    """Two factor authentication code serializer"""

    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    code = serializers.IntegerField()

    def validate(self, attrs):
        code = cache.get(attrs['user'].pk)

        if attrs['code'] != code:
            raise serializers.ValidationError('Invalid code')

        return attrs

    def get_token_pair(self) -> dict:
        return get_token_pair(self.validated_data['user'])


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = PasswordField()

    _user: CustomUser

    def validate(self, attrs):
        self._user: CustomUser = CustomUser.objects.filter(username=attrs['username']).first()

        if (self._user is None) or (not self._user.check_password(attrs['password'])):
            raise serializers.ValidationError('Invalid username or password')

        if not self._user.is_active:
            raise serializers.ValidationError('Account is not active')

        return attrs

    def get_user(self) -> CustomUser:
        return self._user

    def get_token_pair(self) -> dict:
        return get_token_pair(self._user)

    def get_verification_token(self) -> dict:
        return get_verification_token(self._user)


class SignupSerializer(serializers.Serializer):
    username = serializers.CharField()
    email = serializers.EmailField(required=False)
    phone = serializers.CharField(required=False)
    password1 = PasswordField()
    password2 = PasswordField()

    _user: CustomUser

    # TODO decrease db hits amount
    def validate_username(self, value):
        if CustomUser.objects.filter(username=value).exists():
            raise serializers.ValidationError('Username is taken')
        return value

    def validate_email(self, value):
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError('Email already exists')
        return value

    def validate_phone(self, value):
        if CustomUser.objects.filter(phone=value).exists():
            raise serializers.ValidationError('Phone already exists')
        return value

    def validate(self, attrs):
        if attrs['password1'] != attrs['password2']:
            raise serializers.ValidationError('Passwords do not match')

        if not any({attrs.get('email'), attrs.get('phone')}):
            raise serializers.ValidationError('email or phone should be provided')

        return attrs

    def get_token_pair(self) -> dict:
        return get_token_pair(self._user)

    def get_verification_token(self) -> dict:
        return get_verification_token(self._user)

    def save(self, **kwargs) -> CustomUser:
        user_kwargs = {
            'username': self.validated_data['username'],
            'password': self.validated_data['password1'],
            **kwargs,
        }
        if self.validated_data.get('email'):
            user_kwargs['email'] = self.validated_data['email']
        if self.validated_data.get('phone'):
            user_kwargs['phone'] = self.validated_data['phone']

        if 'email' in user_kwargs:
            user_kwargs['two_fa_type'] = CustomUser.TwoFAType.EMAIL
        elif 'phone' in user_kwargs:
            user_kwargs['two_fa_type'] = CustomUser.TwoFAType.PHONE

        self._user = CustomUser.objects.create_user(**user_kwargs)
        return self._user
