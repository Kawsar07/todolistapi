from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework_simplejwt.tokens import RefreshToken
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.db.models import Q

from .models import TodoTask, Category, Profile
from .serializers import TodoTaskSerializer, CategorySerializer, LoginSerializer, RegistrationSerializer, ProfileSerializer

class RegisterView(APIView):
    permission_classes = [AllowAny]
    parser_classes = [MultiPartParser, FormParser]

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_EMAIL),
                'password': openapi.Schema(type=openapi.TYPE_STRING),
                'name': openapi.Schema(type=openapi.TYPE_STRING),
                'location': openapi.Schema(type=openapi.TYPE_STRING),
                'image': openapi.Schema(type=openapi.TYPE_FILE, description='Profile image'),
            },
            required=['email', 'password', 'name'],
        ),
        responses={201: openapi.Response('Success', RegistrationSerializer)}
    )
    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()

            # Ensure profile has default category (safety for older DBs/edge cases)
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
                'user': {
                    'email': user.email,
                    'profile': profile_serializer.data
                }
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
@swagger_auto_schema(
    request_body=LoginSerializer,
    responses={200: openapi.Response('Success', LoginSerializer)}
)
def login(request):
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        return Response({
            'message': 'Login successful',
            **serializer.validated_data
        }, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProfileView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    @swagger_auto_schema(
        request_body=ProfileSerializer(many=False),
        manual_parameters=[openapi.Parameter('Authorization', openapi.IN_HEADER, type=openapi.TYPE_STRING, description='Bearer token')]
    )
    def get(self, request):
        profile, created = Profile.objects.get_or_create(user=request.user)
        # If profile has no default_category, set the shared default (for older users)
        if not profile.default_category:
            profile.default_category = Category.get_default_category()
            profile.save(update_fields=['default_category'])

        serializer = ProfileSerializer(profile, context={'request': request})
        data = serializer.data
        data['email'] = request.user.email
        return Response(data)

    def put(self, request):
        profile, created = Profile.objects.get_or_create(user=request.user)
        serializer = ProfileSerializer(profile, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Profile updated successfully"})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
@swagger_auto_schema(
    request_body=TodoTaskSerializer,
    responses={201: openapi.Response('Success', TodoTaskSerializer)}
)
def todoTaskApi(request):
    if request.method == 'GET':
        tasks = TodoTask.objects.filter(user=request.user)
        serializer = TodoTaskSerializer(tasks, many=True, context={'request': request})
        return Response(serializer.data)
    elif request.method == 'POST':
        serializer = TodoTaskSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Task added successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
@swagger_auto_schema(
    request_body=TodoTaskSerializer,
    manual_parameters=[openapi.Parameter('Authorization', openapi.IN_HEADER, type=openapi.TYPE_STRING, description='Bearer token')]
)
def todoTaskDetail(request, pk):
    try:
        task = TodoTask.objects.get(pk=pk, user=request.user)
    except TodoTask.DoesNotExist:
        return Response({"error": "Task not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = TodoTaskSerializer(task, context={'request': request})
        return Response(serializer.data)
    elif request.method == 'PUT':
        serializer = TodoTaskSerializer(task, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Task updated successfully"})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        task.delete()
        return Response({"message": "Task deleted successfully"}, status=status.HTTP_204_NO_CONTENT)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
@swagger_auto_schema(
    request_body=CategorySerializer,
    responses={201: openapi.Response('Success', CategorySerializer)}
)
def categoryListCreateApi(request):
    if request.method == 'GET':
        # Return both general categories and user's personal categories
        categories = Category.objects.filter(
            Q(is_general=True) | Q(creator=request.user)
        ).distinct()
        serializer = CategorySerializer(categories, many=True, context={'request': request})
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = CategorySerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            # Always create as personal category (not general)
            serializer.save(creator=request.user, is_general=False)
            return Response({
                "message": "Personal category added successfully",
                "category": serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
@swagger_auto_schema(
    request_body=CategorySerializer,
    manual_parameters=[openapi.Parameter('Authorization', openapi.IN_HEADER, type=openapi.TYPE_STRING, description='Bearer token')]
)
def categoryDetailApi(request, pk):
    try:
        # Allow access to general categories and user's personal categories
        category = Category.objects.get(
            Q(pk=pk) & (Q(is_general=True) | Q(creator=request.user))
        )
    except Category.DoesNotExist:
        return Response({"error": "Category not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = CategorySerializer(category, context={'request': request})
        return Response(serializer.data)

    elif request.method == 'PUT':
        # Check if user can edit this category
        if not category.is_editable_by(request.user):
            return Response(
                {"error": "You cannot edit general categories"},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = CategorySerializer(category, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Category updated successfully"})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        # Check if user can delete this category
        if not category.is_editable_by(request.user):
            return Response(
                {"error": "You cannot delete general categories"},
                status=status.HTTP_403_FORBIDDEN
            )

        # Check if category is being used as default
        if Profile.objects.filter(default_category=category).exists():
            return Response(
                {"error": "Cannot delete category that is set as default for some users"},
                status=status.HTTP_400_BAD_REQUEST
            )

        category.delete()
        return Response({"message": "Category deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
