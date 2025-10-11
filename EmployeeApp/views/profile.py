from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from ..models import Profile, Category
from ..serializers import ProfileSerializer


class ProfileView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    @swagger_auto_schema(
        operation_description="Retrieve user profile",
        responses={200: ProfileSerializer},
        manual_parameters=[
            openapi.Parameter('Authorization', openapi.IN_HEADER, type=openapi.TYPE_STRING, description='Bearer token')
        ]
    )
    def get(self, request):
        profile, _ = Profile.objects.get_or_create(user=request.user)
        if not profile.default_category:
            profile.default_category = Category.get_default_category()
            profile.save(update_fields=['default_category'])
        serializer = ProfileSerializer(profile, context={'request': request})
        data = serializer.data
        data['email'] = request.user.email
        return Response(data)

    @swagger_auto_schema(
        operation_description="Update user profile with form data",
        manual_parameters=[
            openapi.Parameter('name', openapi.IN_FORM, type=openapi.TYPE_STRING, description='User name', required=True),
            openapi.Parameter('location', openapi.IN_FORM, type=openapi.TYPE_STRING, description='User location (optional)'),
            openapi.Parameter('image', openapi.IN_FORM, type=openapi.TYPE_FILE, description='Profile image (optional)'),
            openapi.Parameter('default_category_id', openapi.IN_FORM, type=openapi.TYPE_INTEGER, description='Default category ID (optional)'),
            openapi.Parameter('Authorization', openapi.IN_HEADER, type=openapi.TYPE_STRING, description='Bearer token')
        ],
        consumes=['multipart/form-data'],
        responses={200: 'Success', 400: 'Invalid input'}
    )
    def put(self, request):
        profile, _ = Profile.objects.get_or_create(user=request.user)
        serializer = ProfileSerializer(profile, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Profile updated successfully"})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)