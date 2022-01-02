from rest_framework import serializers

from rest_framework_simplejwt.serializers import PasswordField
from rest_framework_simplejwt.exceptions import AuthenticationFailed

from accounts.models import CustomUser, VerificationCode
from accounts.authentication import get_token_pair, get_verification_token
from accounts.tokens import VerificationToken


class CurrentJTIDefault:
    requires_context = True

    def __call__(self, serializer_field):
        return serializer_field.context['request'].auth['jti']

    def __repr__(self):
        return '%s()' % self.__class__.__name__


class VerifyCodeSerializer(serializers.Serializer):
    """Verify code that was being sent to users contact address"""

    _instance: VerificationCode = None
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    jwt_jti = serializers.HiddenField(default=CurrentJTIDefault())

    type = serializers.IntegerField()
    code = serializers.IntegerField()

    def validate(self, attrs):
        if attrs['type'] not in (valid_code_types := VerificationCode.Type.values):
            raise serializers.ValidationError(f'Invalid code type. Allowed types: {valid_code_types}')
        try:
            self._instance = VerificationCode.objects.get(
                user=attrs['user'],
                type=attrs['type'],
                code=attrs['code'],
                is_used=False,
                jwt_jti=attrs['jwt_jti'],
            )
        except VerificationCode.DoesNotExist:
            raise serializers.ValidationError('Invalid code')

        return attrs

    def use_code(self):
        assert hasattr(self, '_validated_data'), '`.is_valid()` must be called before `.use_code()`'
        self._instance.use()

    def get_token_pair(self) -> dict:
        return get_token_pair(self.validated_data['user'])


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = PasswordField()

    _user: CustomUser

    def validate(self, attrs):
        self._user: CustomUser = CustomUser.objects.filter(username=attrs['username']).first()
        if (self._user is None) or (not self._user.check_password(attrs['password'])):
            raise AuthenticationFailed('Invalid username or password')

        if not self._user.is_active:
            raise AuthenticationFailed('Account is not active')
        if not self._user.is_verified:
            raise AuthenticationFailed('Account is not verified')

        return attrs

    def get_user(self) -> CustomUser:
        return self._user

    def get_token_pair(self) -> dict:
        return get_token_pair(self._user)

    def get_verification_token(self) -> VerificationToken:
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
            raise serializers.ValidationError('Email is already used')
        return value

    def validate_phone(self, value):
        if CustomUser.objects.filter(phone=value).exists():
            raise serializers.ValidationError('Phone is already used')
        return value

    def validate(self, attrs):
        if attrs['password1'] != attrs['password2']:
            raise serializers.ValidationError('Passwords do not match')

        if not any({attrs.get('email'), attrs.get('phone')}):
            raise serializers.ValidationError('email or phone should be provided')

        return attrs

    def get_verification_token(self) -> VerificationToken:
        return get_verification_token(self._user)

    def save(self, **kwargs) -> CustomUser:
        user_kwargs = {
            'username': self.validated_data['username'],
            'password': self.validated_data['password1'],
            'two_fa_enabled': True,
            **kwargs,
        }
        if phone := self.validated_data.get('phone'):
            user_kwargs['phone'] = phone
            user_kwargs['two_fa_type'] = CustomUser.TwoFAType.PHONE
        if email := self.validated_data.get('email'):
            user_kwargs['email'] = email
            user_kwargs['two_fa_type'] = CustomUser.TwoFAType.EMAIL

        self._user = CustomUser.objects.create_user(**user_kwargs)
        return self._user


class ResendVerificationCodeSerializer(serializers.Serializer):
    type = serializers.IntegerField()

    def validate_type(self, value):
        # TODO check if user can ask to resend code
        valid_code_types = VerificationCode.Type.values
        if value not in valid_code_types:
            raise serializers.ValidationError(f'Invalid code type. Allowed types: {valid_code_types}')
        return value


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = (
            'username',
            'email',
            'phone',
            'first_name',
            'last_name',
            'two_fa_enabled',
            'two_fa_type',
            'last_login',
            'date_joined',
        )
        read_only_fields = (
            'username',
            'email',
            'phone',
            'two_fa_enabled',
            'two_fa_type',
            'last_login',
            'date_joined',
        )
