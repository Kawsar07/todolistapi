from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.contrib.auth.models import User
from ..models import OTP
from ..serializers import OTPVerificationSerializer


class OTPVerificationView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description="Verify OTP and reset password",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_EMAIL, description='User email'),
                'otp': openapi.Schema(type=openapi.TYPE_STRING, description='OTP code'),
                'new_password': openapi.Schema(type=openapi.TYPE_STRING, description='New password'),
            },
            required=['email', 'otp', 'new_password']
        ),
        consumes=['application/json'],
        responses={200: 'Password reset', 400: 'Invalid or expired OTP'}
    )
    def post(self, request):
        serializer = OTPVerificationSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            otp = serializer.validated_data['otp']
            new_password = serializer.validated_data['new_password']
            user = User.objects.filter(email=email).first()
            if not user:
                return Response({"error": "Email not found"}, status=status.HTTP_400_BAD_REQUEST)
            otp_record = OTP.objects.filter(user=user, otp=otp, is_used=False).first()
            if not otp_record:
                return Response({"error": "Invalid OTP"}, status=status.HTTP_400_BAD_REQUEST)
            if timezone.now() > otp_record.expires_at:
                return Response({"error": "OTP has expired"}, status=status.HTTP_400_BAD_REQUEST)
            user.set_password(new_password)
            user.save()
            otp_record.is_used = True
            otp_record.save()
            return Response({"message": "Password reset successfully"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)