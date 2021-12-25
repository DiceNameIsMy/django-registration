from django.contrib.auth.models import update_last_login

from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import GenericAPIView, RetrieveUpdateDestroyAPIView, get_object_or_404
from rest_framework.response import Response
from rest_framework import status

from accounts.authentication import VerificationJWTAuthentication
from accounts.models import CustomUser, VerificationCode
from accounts.tasks import send_verification_code

from .serializers import (
    LoginSerializer,
    ProfileSerializer,
    ResendVerificationCodeSerializer,
    VerifyCodeSerializer,
    SignupSerializer,
)


class LoginView(GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request):
        serializer: LoginSerializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.get_user()

        if user.two_fa_enabled:
            token = serializer.get_verification_token()
            send_verification_code.delay(user.pk, token['jti'], VerificationCode.Type.LOG_IN)
            return Response(
                data={
                    'method': user.two_fa_type,
                    'verification': str(token),
                },
                status=status.HTTP_201_CREATED,
            )
        else:
            update_last_login(None, user)
            return Response(
                data=serializer.get_token_pair(),
                status=status.HTTP_200_OK,
            )


class LoginVerifyView(GenericAPIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (VerificationJWTAuthentication,)

    serializer_class = VerifyCodeSerializer

    def post(self, request):
        serializer: VerifyCodeSerializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.use_code()

        update_last_login(None, request.user)
        return Response(serializer.get_token_pair(), status=status.HTTP_200_OK)


class SignupView(GenericAPIView):
    serializer_class = SignupSerializer

    def post(self, request):
        serializer: SignupSerializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        token = serializer.get_verification_token()

        send_verification_code.delay(user.pk, token['jti'], VerificationCode.Type.SIGN_UP)
        return Response(
            data={
                'method': user.two_fa_type,
                'verification': str(token),
            },
            status=status.HTTP_201_CREATED,
        )


class SignupVerifyView(GenericAPIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (VerificationJWTAuthentication,)

    serializer_class = VerifyCodeSerializer

    def post(self, request):
        serializer: VerifyCodeSerializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.use_code()

        # also updates last_login
        # TODO refactor this line
        request.user.verify_user()

        return Response(serializer.get_token_pair(), status=status.HTTP_200_OK)


class ResendVerificationCodeView(GenericAPIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (VerificationJWTAuthentication,)

    serializer_class = ResendVerificationCodeSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        send_verification_code.delay(request.user.pk, request.auth['jti'], serializer.validated_data['type'])
        return Response(status=status.HTTP_201_CREATED)


class ProfileView(RetrieveUpdateDestroyAPIView):
    serializer_class = ProfileSerializer
    queryset = CustomUser.objects.all()

    def get_object(self):
        return get_object_or_404(self.get_queryset(), pk=self.request.user.pk)

    def perform_destroy(self, instance: CustomUser):
        instance.is_active = False
        instance.save(update_fields=['is_active'])
