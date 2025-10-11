from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from ..models import TodoTask
from ..serializers import TodoTaskSerializer


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