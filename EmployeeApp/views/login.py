from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from ..serializers import LoginSerializer


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