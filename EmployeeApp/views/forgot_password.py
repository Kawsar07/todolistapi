from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.contrib.auth.models import User
from ..models import OTP
from ..serializers import ForgotPasswordSerializer
import random
import string
from datetime import timedelta


class ForgotPasswordView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description="Request OTP for password reset",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_EMAIL, description='User email'),
            },
            required=['email']
        ),
        consumes=['application/json'],
        responses={200: 'OTP sent', 400: 'Invalid email', 500: 'Failed to send OTP'}
    )
    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            user = User.objects.filter(email=email).first()
            if not user:
                return Response({"error": "Email not found"}, status=status.HTTP_400_BAD_REQUEST)
            otp = ''.join(random.choices(string.digits, k=6))
            expiry_time = timezone.now() + timedelta(minutes=10)
            OTP.objects.create(user=user, otp=otp, expires_at=expiry_time)
            try:
                send_mail(
                    subject="Your OTP Code",
                    message=f"Your OTP is {otp}. It expires in 10 minutes.",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[email],
                    fail_silently=False,
                )
            except Exception as e:
                print(f"Email sending failed: {str(e)}")
                return Response({"error": f"Failed to send OTP email: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            return Response({"message": "OTP sent to your email"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)