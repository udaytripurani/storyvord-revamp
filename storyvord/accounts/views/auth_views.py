from django.db import IntegrityError
from rest_framework import status
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework.permissions import IsAuthenticated
from django.utils.timezone import now
from accounts.utils import send_verification_email, get_tokens_for_user
from ..serializers.serializers_v2 import V2RegisterSerializer, V2LoginSerializer, V2UserDataSerializer
from accounts.models import User
import logging

logger = logging.getLogger(__name__)

class RegisterViewV2(APIView):
    serializer_class = V2RegisterSerializer

    def post(self, request, *args, **kwargs):
        """
        Register a new user and send a verification email.
        """
        serializer = self.serializer_class(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            user = serializer.save()
            tokens = get_tokens_for_user(user)
            send_verification_email(user, tokens['access'])

            logger.info(f"User {user.email} registered successfully")
            return Response({
                "status": status.HTTP_201_CREATED,
                "message": "User created successfully. Verification email sent.",
                "data": {
                    "user": serializer.data,
                    "tokens": tokens,
                },
            }, status=status.HTTP_201_CREATED)

        except serializers.ValidationError as e:
            logger.error(f"User registration failed: {str(e)}")
            return Response({
                "status": status.HTTP_400_BAD_REQUEST,
                "message": "Registration failed.",
                "data": e.detail,
            }, status=status.HTTP_400_BAD_REQUEST)

        except IntegrityError:
            logger.error("User registration failed: Email already exists.")
            return Response({
                "status": status.HTTP_409_CONFLICT,
                "message": "Email already exists.",
                "data": None,
            }, status=status.HTTP_409_CONFLICT)

        except Exception as e:
            logger.error(f"User registration failed: {str(e)}")
            return Response({
                "status": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "message": "An error occurred during registration.",
                "data": str(e),
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class LoginViewV2(APIView):
    serializer_class = V2LoginSerializer

    def post(self, request, *args, **kwargs):
        """
        Log in a user and return tokens and user data.
        """
        serializer = self.serializer_class(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            user = serializer.context['user']

            if not user.verified:
                tokens = get_tokens_for_user(user)
                send_verification_email(user, tokens['access'])
                logger.warning(f"User {user.email} attempted login without verifying email.")
                return Response({
                    "status": status.HTTP_403_FORBIDDEN,
                    "message": "Email not verified. Verification email sent.",
                }, status=status.HTTP_403_FORBIDDEN)

            user.last_login = now()
            user.save()

            tokens = get_tokens_for_user(user)
            logger.info(f"User {user.email} logged in successfully.")
            return Response({
                "status": status.HTTP_200_OK,
                "message": "User logged in successfully.",
                "data": {
                    "user": V2UserDataSerializer(user).data,
                    "tokens": tokens,
                },
            }, status=status.HTTP_200_OK)

        except serializers.ValidationError as e:
            logger.error(f"Login failed: {str(e)}")
            return Response({
                "status": status.HTTP_400_BAD_REQUEST,
                "message": "Invalid credentials.",
                "data": e.detail,
            }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            logger.error(f"Login failed: {str(e)}")
            return Response({
                "status": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "message": "An error occurred during login.",
                "data": str(e),
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class LogoutViewV2(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        """
        Logs out a user by blacklisting the refresh token and returns a success message.

        Args:
            request (object): The request object.

        Returns:
            Response (object): A response object with the status code and message.
        """
        try:
            # Extract the refresh token from the request
            refresh_token = request.data.get("refresh")
            if not refresh_token:
                logger.error("No refresh token provided")
                return Response({
                    "status": status.HTTP_400_BAD_REQUEST,
                    "message": "No refresh token provided.",
                }, status=status.HTTP_400_BAD_REQUEST)

            # Blacklist the refresh token
            try:
                token = RefreshToken(refresh_token)
                token.blacklist()
                logger.info(f"Refresh token blacklisted for user {request.user.email}")
            except TokenError:
                logger.error("Invalid or expired refresh token")
                return Response({
                    "status": status.HTTP_401_UNAUTHORIZED,
                    "message": "Invalid or expired refresh token.",
                }, status=status.HTTP_401_UNAUTHORIZED)

            logger.info(f"User {request.user.email} logged out successfully")
            return Response({
                "status": status.HTTP_200_OK,
                "message": "User logged out successfully.",
            }, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Logout failed: {str(e)}")
            return Response({
                "status": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "message": "An error occurred during logout.",
                "data": str(e),
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
