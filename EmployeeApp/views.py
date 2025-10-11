from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
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
import random
import string
from datetime import timedelta
from django.contrib.auth.models import User
from .models import TodoTask, Category, Profile, OTP
from .serializers import (
    TodoTaskSerializer, CategorySerializer, LoginSerializer,
    RegistrationSerializer, ProfileSerializer, ForgotPasswordSerializer,
    OTPVerificationSerializer, ChangePasswordSerializer
)

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

@api_view(['POST'])
@permission_classes([AllowAny])
@swagger_auto_schema(
    operation_description="Log in a user",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'email': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_EMAIL, description='User email'),
            'password': openapi.Schema(type=openapi.TYPE_STRING, description='User password'),
        },
        required=['email', 'password']
    ),
    consumes=['application/json'],
    responses={200: LoginSerializer, 400: 'Invalid credentials'}
)
def login(request):
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        return Response({'message': 'Login successful', **serializer.validated_data}, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
@swagger_auto_schema(
    operation_description="List or create tasks",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'name': openapi.Schema(type=openapi.TYPE_STRING, description='Task name'),
            'description': openapi.Schema(type=openapi.TYPE_STRING, description='Task description (optional)'),
            'due_date': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME, description='Due date (optional)'),
            'is_completed': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='Task completion status (optional)'),
            'category_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='Category ID (optional)'),
        },
        required=['name']
    ),
    consumes=['application/json'],
    responses={200: TodoTaskSerializer(many=True), 201: TodoTaskSerializer, 400: 'Invalid input'},
    manual_parameters=[
        openapi.Parameter('Authorization', openapi.IN_HEADER, type=openapi.TYPE_STRING, description='Bearer token')
    ]
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
    operation_description="Retrieve, update, or delete a task",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'name': openapi.Schema(type=openapi.TYPE_STRING, description='Task name'),
            'description': openapi.Schema(type=openapi.TYPE_STRING, description='Task description (optional)'),
            'due_date': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME, description='Due date (optional)'),
            'is_completed': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='Task completion status (optional)'),
            'category_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='Category ID (optional)'),
        },
        required=['name']
    ),
    consumes=['application/json'],
    responses={200: TodoTaskSerializer, 204: 'Task deleted', 400: 'Invalid input', 404: 'Task not found'},
    manual_parameters=[
        openapi.Parameter('Authorization', openapi.IN_HEADER, type=openapi.TYPE_STRING, description='Bearer token')
    ]
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
    operation_description="List or create categories",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'name': openapi.Schema(type=openapi.TYPE_STRING, description='Category name'),
            'is_general': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='Is general category (optional)'),
        },
        required=['name']
    ),
    consumes=['application/json'],
    responses={200: CategorySerializer(many=True), 201: CategorySerializer, 400: 'Invalid input'},
    manual_parameters=[
        openapi.Parameter('Authorization', openapi.IN_HEADER, type=openapi.TYPE_STRING, description='Bearer token')
    ]
)
def categoryListCreateApi(request):
    if request.method == 'GET':
        categories = Category.objects.filter(Q(is_general=True) | Q(creator=request.user)).distinct()
        serializer = CategorySerializer(categories, many=True, context={'request': request})
        return Response(serializer.data)
    elif request.method == 'POST':
        serializer = CategorySerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save(creator=request.user, is_general=False)
            return Response({"message": "Category added successfully", "category": serializer.data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
@swagger_auto_schema(
    operation_description="Retrieve, update, or delete a category",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'name': openapi.Schema(type=openapi.TYPE_STRING, description='Category name'),
            'is_general': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='Is general category (optional)'),
        },
        required=['name']
    ),
    consumes=['application/json'],
    responses={200: CategorySerializer, 204: 'Category deleted', 400: 'Invalid input', 403: 'Forbidden', 404: 'Category not found'},
    manual_parameters=[
        openapi.Parameter('Authorization', openapi.IN_HEADER, type=openapi.TYPE_STRING, description='Bearer token')
    ]
)
def categoryDetailApi(request, pk):
    try:
        category = Category.objects.get(Q(pk=pk) & (Q(is_general=True) | Q(creator=request.user)))
    except Category.DoesNotExist:
        return Response({"error": "Category not found"}, status=status.HTTP_404_NOT_FOUND)
    if request.method == 'GET':
        serializer = CategorySerializer(category, context={'request': request})
        return Response(serializer.data)
    elif request.method == 'PUT':
        if not category.is_editable_by(request.user):
            return Response({"error": "You cannot edit general categories"}, status=status.HTTP_403_FORBIDDEN)
        serializer = CategorySerializer(category, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Category updated successfully"})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        if not category.is_editable_by(request.user):
            return Response({"error": "You cannot delete general categories"}, status=status.HTTP_403_FORBIDDEN)
        if Profile.objects.filter(default_category=category).exists():
            return Response({"error": "Cannot delete default category"}, status=status.HTTP_400_BAD_REQUEST)
        category.delete()
        return Response({"message": "Category deleted successfully"}, status=status.HTTP_204_NO_CONTENT)

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

class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Change user password",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'old_password': openapi.Schema(type=openapi.TYPE_STRING, description='Current password'),
                'new_password': openapi.Schema(type=openapi.TYPE_STRING, description='New password'),
            },
            required=['old_password', 'new_password']
        ),
        consumes=['application/json'],
        responses={200: 'Password changed', 400: 'Invalid old password'},
        manual_parameters=[
            openapi.Parameter('Authorization', openapi.IN_HEADER, type=openapi.TYPE_STRING, description='Bearer token')
        ]
    )
    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            user = request.user
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            return Response({"message": "Password changed successfully"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)