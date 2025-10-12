from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.contrib.auth.models import User
from ..models import PendingRegistration, Profile, Category
from ..serializers import PendingRegistrationSerializer
from ..permissions import IsAdmin
from rest_framework_simplejwt.tokens import RefreshToken

class PendingRegistrationListView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    @swagger_auto_schema(
        operation_description="List pending registrations (Admin and SuperAdmin only)",
        responses={200: PendingRegistrationSerializer(many=True)},
        manual_parameters=[
            openapi.Parameter('Authorization', openapi.IN_HEADER, type=openapi.TYPE_STRING, description='Bearer token')
        ]
    )
    def get(self, request):
        pending_requests = PendingRegistration.objects.filter(status='pending')
        serializer = PendingRegistrationSerializer(pending_requests, many=True)
        return Response(serializer.data)

class PendingRegistrationDetailView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    @swagger_auto_schema(
        operation_description="Approve or reject a pending registration (Admin and SuperAdmin only)",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'status': openapi.Schema(type=openapi.TYPE_STRING, enum=['approved', 'rejected'], description='Status of the registration'),
                'role': openapi.Schema(type=openapi.TYPE_STRING, enum=['user', 'admin', 'superadmin'], description='Role for approved user (SuperAdmin only, optional)'),
            },
            required=['status']
        ),
        responses={200: 'Success', 400: 'Invalid input', 404: 'Pending registration not found'},
        manual_parameters=[
            openapi.Parameter('Authorization', openapi.IN_HEADER, type=openapi.TYPE_STRING, description='Bearer token')
        ]
    )
    def put(self, request, pk):
        try:
            pending = PendingRegistration.objects.get(pk=pk)
        except PendingRegistration.DoesNotExist:
            return Response({"error": "Pending registration not found"}, status=status.HTTP_404_NOT_FOUND)
        
        status_choice = request.data.get('status')
        if status_choice not in ['approved', 'rejected']:
            return Response({"error": "Invalid status"}, status=status.HTTP_400_BAD_REQUEST)
        
        pending.status = status_choice
        pending.save()
        
        if status_choice == 'approved':
            user = User.objects.create_user(
                username=pending.email,
                email=pending.email,
                password=pending.password
            )
            profile_data = {
                'name': pending.name,
                'location': pending.location,
                'default_category': Category.get_default_category(),
                'role': 'user' if request.user.profile.role != 'superadmin' else request.data.get('role', 'user'),
                'status': 'approved'
            }
            profile = Profile.objects.create(user=user, **profile_data)
            if pending.image:
                profile.image = pending.image
                profile.save()
            
            refresh = RefreshToken.for_user(user)
            return Response({
                'message': 'Registration approved',
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            })
        else:
            return Response({"message": "Registration rejected"})