from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.contrib.auth.models import User
from django.db.models import Q
from ..models import Profile
from ..serializers import UserSerializer, RoleUpdateSerializer
from ..permissions import IsSuperAdmin, IsAdmin

class CustomPageNumberPagination(PageNumberPagination):
    page_size = 20  
    page_size_query_param = 'page_size'
    max_page_size = 100  

class UserListView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    @swagger_auto_schema(
        operation_description="List all users with pagination (SuperAdmin and Admin only)",
        responses={200: UserSerializer(many=True)},
        manual_parameters=[
            openapi.Parameter('Authorization', openapi.IN_HEADER, type=openapi.TYPE_STRING, description='Bearer token'),
            openapi.Parameter('page', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description='Page number'),
            openapi.Parameter('page_size', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description='Number of items per page (max 100)'),
        ]
    )
    def get(self, request):
        users = User.objects.all()
        paginator = CustomPageNumberPagination()
        page = paginator.paginate_queryset(users, request)
        serializer = UserSerializer(page, many=True, context={'request': request})
        return paginator.get_paginated_response(serializer.data)

class UserSearchView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    @swagger_auto_schema(
        operation_description="Search users by username with pagination (SuperAdmin and Admin only)",
        responses={200: UserSerializer(many=True)},
        manual_parameters=[
            openapi.Parameter('Authorization', openapi.IN_HEADER, type=openapi.TYPE_STRING, description='Bearer token'),
            openapi.Parameter('search', openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Search by username', required=True),
            openapi.Parameter('page', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description='Page number'),
            openapi.Parameter('page_size', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description='Number of items per page (max 100)'),
        ]
    )
    def get(self, request):
        search_query = request.query_params.get('search', '').strip()
        if not search_query:
            return Response({"error": "Search query is required"}, status=status.HTTP_400_BAD_REQUEST)
        users = User.objects.filter(username__icontains=search_query)
        paginator = CustomPageNumberPagination()
        page = paginator.paginate_queryset(users, request)
        serializer = UserSerializer(page, many=True, context={'request': request})
        return paginator.get_paginated_response(serializer.data)

class UserDetailView(APIView):
    permission_classes = [IsAuthenticated, IsSuperAdmin]

    @swagger_auto_schema(
        operation_description="Update user role (SuperAdmin only)",
        request_body=RoleUpdateSerializer,
        responses={200: 'Success', 400: 'Invalid input', 404: 'User not found'},
        manual_parameters=[
            openapi.Parameter('Authorization', openapi.IN_HEADER, type=openapi.TYPE_STRING, description='Bearer token')
        ]
    )
    def put(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = RoleUpdateSerializer(data=request.data)
        if serializer.is_valid():
            profile = user.profile
            profile.role = serializer.validated_data['role']
            profile.save()
            return Response({"message": "Role updated successfully"})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="Delete user account (SuperAdmin only)",
        responses={204: 'User deleted', 404: 'User not found'},
        manual_parameters=[
            openapi.Parameter('Authorization', openapi.IN_HEADER, type=openapi.TYPE_STRING, description='Bearer token')
        ]
    )
    def delete(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        
        if user == request.user:
            return Response({"error": "Cannot delete own account"}, status=status.HTTP_400_BAD_REQUEST)
        
        user.delete()
        return Response({"message": "User deleted successfully"}, status=status.HTTP_204_NO_CONTENT)