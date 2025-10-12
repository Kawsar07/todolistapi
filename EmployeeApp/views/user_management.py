from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.contrib.auth.models import User
from ..models import Profile
from ..serializers import UserSerializer, RoleUpdateSerializer
from ..permissions import IsSuperAdmin, IsAdmin

class UserListView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    @swagger_auto_schema(
        operation_description="List all users (SuperAdmin and Admin only)",
        responses={200: UserSerializer(many=True)},
        manual_parameters=[
            openapi.Parameter('Authorization', openapi.IN_HEADER, type=openapi.TYPE_STRING, description='Bearer token')
        ]
    )
    def get(self, request):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True, context={'request': request})
        return Response(serializer.data)

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