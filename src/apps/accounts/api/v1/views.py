from django.contrib.auth.models import update_last_login

from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework import status

from apps.accounts.authentication import VerificationJWTAuthentication
from apps.accounts.tasks import send_verification_code

from .serializers import LoginSerializer, LoginVerifySerializer


class LoginView(GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request):
        serializer: LoginSerializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.get_user()
        # TODO check if user can ask to resend code

        if user.two_fa_enabled:
            send_verification_code.delay(user.id)
            return Response(serializer.get_verification_token(), status=status.HTTP_201_CREATED)
        else:
            update_last_login(None, user)
            return Response(serializer.get_token_pair(), status=status.HTTP_200_OK)


class LoginVerifyView(GenericAPIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (VerificationJWTAuthentication, )

    serializer_class = LoginVerifySerializer

    def post(self, request):
        serializer: LoginVerifySerializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        update_last_login(None, request.user)
        return Response(serializer.get_token_pair(), status=status.HTTP_200_OK)
