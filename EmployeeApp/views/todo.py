from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from ..models import TodoTask
from ..serializers import TodoTaskSerializer
from ..permissions import IsSuperAdmin, IsAdmin, IsOwnerOrAdmin

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
            'user_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='User ID (optional, SuperAdmin only)'),
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
        if request.user.profile.role == 'superadmin':
            tasks = TodoTask.objects.all()
        elif request.user.profile.role == 'admin':
            tasks = TodoTask.objects.all()  # Admin can view all tasks
        else:
            tasks = TodoTask.objects.filter(user=request.user)
        serializer = TodoTaskSerializer(tasks, many=True, context={'request': request})
        return Response(serializer.data)
    elif request.method == 'POST':
        data = request.data.copy()
        if request.user.profile.role != 'superadmin':
            data['user'] = request.user.id
        serializer = TodoTaskSerializer(data=data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Task added successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated, IsOwnerOrAdmin])
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
            'user_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='User ID (optional, SuperAdmin only)'),
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
        task = TodoTask.objects.get(pk=pk)
    except TodoTask.DoesNotExist:
        return Response({"error": "Task not found"}, status=status.HTTP_404_NOT_FOUND)
    
    if not (request.user.profile.role in ['admin', 'superadmin'] or task.user == request.user):
        return Response({"error": "Permission denied"}, status=status.HTTP_403_FORBIDDEN)
    
    if request.method == 'GET':
        serializer = TodoTaskSerializer(task, context={'request': request})
        return Response(serializer.data)
    elif request.method == 'PUT':
        if request.user.profile.role != 'superadmin' and task.user != request.user:
            return Response({"error": "Permission denied"}, status=status.HTTP_403_FORBIDDEN)
        data = request.data.copy()
        if request.user.profile.role != 'superadmin':
            data['user'] = task.user.id
        serializer = TodoTaskSerializer(task, data=data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Task updated successfully"})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        if request.user.profile.role != 'superadmin' and task.user != request.user:
            return Response({"error": "Permission denied"}, status=status.HTTP_403_FORBIDDEN)
        task.delete()
        return Response({"message": "Task deleted successfully"}, status=status.HTTP_204_NO_CONTENT)