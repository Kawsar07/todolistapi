from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.db.models import Q
from ..models import Category, Profile
from ..serializers import CategorySerializer


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