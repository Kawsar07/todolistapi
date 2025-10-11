from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework_simplejwt.tokens import RefreshToken
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from ..models import Profile, Category
from ..serializers import RegistrationSerializer, ProfileSerializer


class RegisterView(APIView):
    permission_classes = [AllowAny]
    parser_classes = [MultiPartParser, FormParser]

    @swagger_auto_schema(
        operation_description="Register a new user with form data",
        manual_parameters=[
            openapi.Parameter('email', openapi.IN_FORM, type=openapi.TYPE_STRING, format=openapi.FORMAT_EMAIL, description='User email', required=True),
            openapi.Parameter('password', openapi.IN_FORM, type=openapi.TYPE_STRING, description='User password', required=True),
            openapi.Parameter('name', openapi.IN_FORM, type=openapi.TYPE_STRING, description='User name', required=True),
            openapi.Parameter('location', openapi.IN_FORM, type=openapi.TYPE_STRING, description='User location (optional)'),
            openapi.Parameter('image', openapi.IN_FORM, type=openapi.TYPE_FILE, description='Profile image (optional)'),
        ],
        consumes=['multipart/form-data'],
        responses={201: RegistrationSerializer, 400: 'Invalid input'}
    )
    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            profile, _ = Profile.objects.get_or_create(user=user)
            if not profile.default_category:
                profile.default_category = Category.get_default_category()
                profile.save(update_fields=['default_category'])
            refresh = RefreshToken.for_user(user)
            profile_serializer = ProfileSerializer(profile, context={'request': request})
            return Response({
                'message': 'User registered successfully',
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': {'email': user.email, 'profile': profile_serializer.data}
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)