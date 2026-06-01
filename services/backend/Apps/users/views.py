from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.core.mail import send_mail
from django.conf import settings
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import PendingUser, ForgotPasswordRequest
from .serializers import (
    RegisterSerializer,
    VerifyOTPSerializer,
    ResendOTPSerializer,
    CustomTokenObtainPairSerializer,
    ForgotPasswordSerializer,
    ResetPasswordSerializer,
    ChangePasswordSerializer,
    UserSerializer,
    UserUpdateSerializer,
    UserListSerializer,
)
from .permissions import IsAdminUser, IsOwnerOrAdmin
from .utils import success_response, error_response
import logging

logger = logging.getLogger(__name__)
User = get_user_model()


# ==============================================================================
# REGISTRATION VIEWS
# ==============================================================================
class RegisterView(APIView):
    """Register a new user. Sends OTP to email for verification."""
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description="Register a new user (client or barber). An OTP will be sent to the provided email.",
        request_body=RegisterSerializer,
        responses={
            201: openapi.Response(description="OTP sent to email"),
            400: openapi.Response(description="Validation error"),
        },
        tags=['Authentication'],
    )
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        full_name = serializer.validated_data['full_name']
        password = serializer.validated_data['password']
        role = serializer.validated_data.get('role', 'client')

        # Create or update pending user
        pending_user, created = PendingUser.objects.update_or_create(
            email=email,
            defaults={
                'full_name': full_name,
                'password': make_password(password),
                'role': role,
            }
        )
        otp = pending_user.generate_otp()

        # Send OTP email
        try:
            send_mail(
                subject='HairIQ - Email Verification OTP',
                message=f'Your verification code is: {otp}\n\nThis code expires in 15 minutes.',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=False,
            )
        except Exception as e:
            logger.error(f"Failed to send OTP email to {email}: {e}")

        return success_response(
            message="OTP sent to your email. Please verify to complete registration.",
            status_code=201,
        )


class VerifyOTPView(APIView):
    """Verify OTP and activate user account."""
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description="Verify OTP sent during registration to activate the account.",
        request_body=VerifyOTPSerializer,
        responses={
            200: openapi.Response(description="Account activated with JWT tokens"),
            400: openapi.Response(description="Invalid or expired OTP"),
        },
        tags=['Authentication'],
    )
    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email'].lower().strip()
        otp = serializer.validated_data['otp']

        try:
            pending_user = PendingUser.objects.get(email=email)
        except PendingUser.DoesNotExist:
            return error_response("No pending registration found for this email.", status_code=404)

        is_valid, error_msg = pending_user.verify_otp(otp)
        if not is_valid:
            return error_response(error_msg, status_code=400)

        # Create actual user
        user = User.objects.create_user(
            email=pending_user.email,
            password=None,
            full_name=pending_user.full_name,
            role=pending_user.role,
            is_active=True,
            is_verified=True,
        )
        user.password = pending_user.password  # Already hashed
        user.save(update_fields=['password'])

        # Clean up
        pending_user.delete()

        # Generate tokens
        refresh = RefreshToken.for_user(user)

        return success_response(
            data={
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                },
                'user': UserSerializer(user).data,
            },
            message="Account verified and activated successfully.",
        )


class ResendOTPView(APIView):
    """Resend OTP for email verification."""
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description="Resend OTP to the provided email for verification.",
        request_body=ResendOTPSerializer,
        responses={
            200: openapi.Response(description="OTP resent"),
            404: openapi.Response(description="No pending registration found"),
        },
        tags=['Authentication'],
    )
    def post(self, request):
        serializer = ResendOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email'].lower().strip()

        try:
            pending_user = PendingUser.objects.get(email=email)
        except PendingUser.DoesNotExist:
            return error_response("No pending registration found for this email.", status_code=404)

        otp = pending_user.generate_otp()

        try:
            send_mail(
                subject='HairIQ - Email Verification OTP (Resent)',
                message=f'Your verification code is: {otp}\n\nThis code expires in 15 minutes.',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=False,
            )
        except Exception as e:
            logger.error(f"Failed to resend OTP email to {email}: {e}")

        return success_response(message="OTP resent to your email.")


# ==============================================================================
# LOGIN / TOKEN VIEWS
# ==============================================================================
class LoginView(TokenObtainPairView):
    """Authenticate user and return JWT tokens."""
    permission_classes = [AllowAny]
    serializer_class = CustomTokenObtainPairSerializer

    @swagger_auto_schema(
        operation_description="Login with email and password to get JWT tokens.",
        tags=['Authentication'],
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class TokenRefreshAPIView(TokenRefreshView):
    """Refresh JWT access token using refresh token."""
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description="Refresh your JWT access token using a valid refresh token.",
        tags=['Authentication'],
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class LogoutView(APIView):
    """Logout and blacklist the refresh token."""
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Logout by blacklisting the refresh token.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['refresh'],
            properties={
                'refresh': openapi.Schema(type=openapi.TYPE_STRING, description='Refresh token'),
            },
        ),
        responses={
            200: openapi.Response(description="Successfully logged out"),
            400: openapi.Response(description="Invalid token"),
        },
        tags=['Authentication'],
    )
    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            if not refresh_token:
                return error_response("Refresh token is required.", status_code=400)

            token = RefreshToken(refresh_token)
            token.blacklist()
            return success_response(message="Successfully logged out.")
        except Exception:
            return error_response("Invalid or expired token.", status_code=400)


# ==============================================================================
# PASSWORD MANAGEMENT VIEWS
# ==============================================================================
class ForgotPasswordView(APIView):
    """Request a password reset OTP."""
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description="Request a password reset OTP sent to your email.",
        request_body=ForgotPasswordSerializer,
        responses={
            200: openapi.Response(description="OTP sent"),
            404: openapi.Response(description="User not found"),
        },
        tags=['Authentication'],
    )
    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email'].lower().strip()

        if not User.objects.filter(email=email).exists():
            # Return success to prevent email enumeration
            return success_response(message="If this email is registered, you will receive an OTP.")

        forgot_req, _ = ForgotPasswordRequest.objects.update_or_create(
            email=email,
            defaults={}
        )
        otp = forgot_req.generate_otp()

        try:
            send_mail(
                subject='HairIQ - Password Reset OTP',
                message=f'Your password reset code is: {otp}\n\nThis code expires in 15 minutes.',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=False,
            )
        except Exception as e:
            logger.error(f"Failed to send password reset OTP to {email}: {e}")

        return success_response(message="If this email is registered, you will receive an OTP.")


class ResetPasswordView(APIView):
    """Reset password with OTP verification."""
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description="Reset your password using the OTP received via email.",
        request_body=ResetPasswordSerializer,
        responses={
            200: openapi.Response(description="Password reset successfully"),
            400: openapi.Response(description="Invalid OTP or validation error"),
        },
        tags=['Authentication'],
    )
    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email'].lower().strip()
        otp = serializer.validated_data['otp']
        new_password = serializer.validated_data['new_password']

        try:
            forgot_req = ForgotPasswordRequest.objects.get(email=email)
        except ForgotPasswordRequest.DoesNotExist:
            return error_response("No password reset request found.", status_code=404)

        is_valid, error_msg = forgot_req.verify_otp(otp)
        if not is_valid:
            return error_response(error_msg, status_code=400)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return error_response("User not found.", status_code=404)

        user.set_password(new_password)
        user.save(update_fields=['password'])
        forgot_req.delete()

        return success_response(message="Password reset successfully. You can now login.")


class ChangePasswordView(APIView):
    """Change password for authenticated users."""
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Change your password (requires current password).",
        request_body=ChangePasswordSerializer,
        responses={
            200: openapi.Response(description="Password changed"),
            400: openapi.Response(description="Invalid current password"),
        },
        tags=['Authentication'],
    )
    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if not request.user.check_password(serializer.validated_data['old_password']):
            return error_response("Current password is incorrect.", status_code=400)

        request.user.set_password(serializer.validated_data['new_password'])
        request.user.save(update_fields=['password'])

        return success_response(message="Password changed successfully.")


# ==============================================================================
# USER PROFILE VIEWS
# ==============================================================================
class UserMeView(APIView):
    """Get/Update current authenticated user's details."""
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Get the currently authenticated user's details.",
        responses={200: UserSerializer},
        tags=['User Profile'],
    )
    def get(self, request):
        serializer = UserSerializer(request.user)
        return success_response(data=serializer.data)

    @swagger_auto_schema(
        operation_description="Update the currently authenticated user's details.",
        request_body=UserUpdateSerializer,
        responses={200: UserSerializer},
        tags=['User Profile'],
    )
    def patch(self, request):
        serializer = UserUpdateSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return success_response(
            data=UserSerializer(request.user).data,
            message="Profile updated successfully.",
        )


class UserListView(generics.ListAPIView):
    """List all users (admin only)."""
    serializer_class = UserListSerializer
    permission_classes = [IsAdminUser]
    filterset_fields = ['role', 'is_active', 'is_verified']
    search_fields = ['email', 'full_name']
    ordering_fields = ['date_joined', 'email']

    @swagger_auto_schema(
        operation_description="List all users (admin only). Supports filtering by role, status.",
        tags=['Admin'],
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        return User.objects.all()


class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a user (admin only)."""
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]
    lookup_field = 'pk'

    @swagger_auto_schema(tags=['Admin'])
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(tags=['Admin'])
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @swagger_auto_schema(tags=['Admin'])
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)

    @swagger_auto_schema(tags=['Admin'])
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)

    def get_queryset(self):
        return User.objects.all()
