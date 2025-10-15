from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.parsers import MultiPartParser, FormParser
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from ..serializers import RegistrationSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model

User = get_user_model()

class RegisterView(APIView):
    permission_classes = [AllowAny]
    parser_classes = [MultiPartParser, FormParser]

    @swagger_auto_schema(
        operation_description="Register a new user with form data (auto-approval)",
        manual_parameters=[
            openapi.Parameter('email', openapi.IN_FORM, type=openapi.TYPE_STRING, format=openapi.FORMAT_EMAIL, description='User email', required=True),
            openapi.Parameter('password', openapi.IN_FORM, type=openapi.TYPE_STRING, description='User password', required=True),
            openapi.Parameter('name', openapi.IN_FORM, type=openapi.TYPE_STRING, description='User name', required=True),
            openapi.Parameter('location', openapi.IN_FORM, type=openapi.TYPE_STRING, description='User location (optional)'),
            openapi.Parameter('image', openapi.IN_FORM, type=openapi.TYPE_FILE, description='Profile image (optional)'),
        ],
        consumes=['multipart/form-data'],
        responses={201: 'Success with tokens', 400: 'Invalid input'}
    )
    def post(self, request):
        try:
            serializer = RegistrationSerializer(data=request.data)
            if serializer.is_valid():
                user = serializer.save()  # Calls the new create method
                refresh = RefreshToken.for_user(user)
                return Response({
                    'message': 'Registration successful',
                    'access': str(refresh.access_token),
                    'refresh': str(refresh),
                    'user': {
                        'id': user.id,
                        'email': user.email,
                    }
                }, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            # Log the error (in production, use logger)
            print(f"Registration error: {str(e)}")  # Replace with import logging; logging.error(str(e))
            return Response({'error': 'Internal server error during registration', 'details': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)