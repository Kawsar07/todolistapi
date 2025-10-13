from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from ..models import TodoTask
from ..serializers import TodoTaskSerializer
from ..permissions import IsSuperAdmin, IsAdmin, IsOwnerOrAdmin
from ..filters import TodoTaskFilter
from datetime import datetime, timedelta
from django.utils import timezone  # Add for make_aware

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
@swagger_auto_schema(
    operation_description="List or create tasks. GET: Query params for ISO dates. POST: Body with DD-MM-YYYY dates for filter (search mode) or task data for create.",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'name': openapi.Schema(type=openapi.TYPE_STRING, description='Task name (required for create)'),
            'description': openapi.Schema(type=openapi.TYPE_STRING, description='Task description (optional)'),
            'due_date': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME, description='Due date (optional for create)'),
            'is_completed': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='Task completion status (optional)'),
            'category_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='Category ID (optional)'),
            'user_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='User ID (optional, SuperAdmin only)'),
            'start_date': openapi.Schema(type=openapi.TYPE_STRING, description='Filter due_date >= (DD-MM-YYYY, e.g., 01-09-2025) - triggers search mode'),
            'end_date': openapi.Schema(type=openapi.TYPE_STRING, description='Filter due_date <= (DD-MM-YYYY, e.g., 13-09-2025) - triggers search mode'),
        },
        required=['name']  # Only for create; optional for search
    ),
    consumes=['application/json'],
    responses={200: TodoTaskSerializer(many=True), 201: TodoTaskSerializer, 400: 'Invalid input/date format'},
    manual_parameters=[
        openapi.Parameter('Authorization', openapi.IN_HEADER, type=openapi.TYPE_STRING, description='Bearer token'),
        openapi.Parameter('start_date', openapi.IN_QUERY, type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME, description='Filter due_date >= (ISO for GET, e.g., 2025-09-01T00:00:00Z)'),
        openapi.Parameter('end_date', openapi.IN_QUERY, type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME, description='Filter due_date <= (ISO for GET, e.g., 2025-09-13T23:59:59Z)'),
    ]
)
def todoTaskApi(request):
    if request.method == 'GET':
        # Unchanged
        if request.user.profile.role == 'superadmin':
            tasks = TodoTask.objects.all()
        elif request.user.profile.role == 'admin':
            tasks = TodoTask.objects.all()
        else:
            tasks = TodoTask.objects.filter(user=request.user)
        
        filterset = TodoTaskFilter(request.GET, queryset=tasks)
        if not filterset.is_valid():
            return Response(filterset.errors, status=status.HTTP_400_BAD_REQUEST)
        tasks = filterset.qs
        
        serializer = TodoTaskSerializer(tasks, many=True, context={'request': request})
        return Response(serializer.data)
    
    elif request.method == 'POST':
        data = request.data.copy()
        
        # Check if filter fields present → Search mode
        if 'start_date' in data or 'end_date' in data:
            # Role-based queryset (same as GET)
            if request.user.profile.role == 'superadmin':
                tasks = TodoTask.objects.all()
            elif request.user.profile.role == 'admin':
                tasks = TodoTask.objects.all()
            else:
                tasks = TodoTask.objects.filter(user=request.user)
            
            # Optional: Exclude null due_date if you want only dated tasks
            # tasks = tasks.exclude(due_date__isnull=True)
            
            # Parse DD-MM-YYYY dates and make timezone-aware
            filter_data = {}
            try:
                if 'start_date' in data:
                    start_str = data['start_date']
                    start_naive = datetime.strptime(start_str, '%d-%m-%Y')
                    start_aware = timezone.make_aware(start_naive)  # Makes it aware (UTC by default)
                    filter_data['start_date'] = start_aware
                    print(f"Parsed start_date: {start_aware}")  # Debug: Check console
                
                if 'end_date' in data:
                    end_str = data['end_date']
                    end_naive = datetime.strptime(end_str, '%d-%m-%Y') + timedelta(days=1) - timedelta(microseconds=1)
                    end_aware = timezone.make_aware(end_naive)
                    filter_data['end_date'] = end_aware
                    print(f"Parsed end_date: {end_aware}")  # Debug: Check console
            except ValueError as e:
                return Response({"error": f"Invalid date format. Use DD-MM-YYYY (e.g., 01-09-2025). Error: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
            
            # Apply filter
            print(f"Before filter: {tasks.count()} tasks")  # Debug
            filterset = TodoTaskFilter(data=filter_data, queryset=tasks)
            if not filterset.is_valid():
                return Response(filterset.errors, status=status.HTTP_400_BAD_REQUEST)
            tasks = filterset.qs
            print(f"After filter: {tasks.count()} tasks")  # Debug
            
            if tasks.count() == 0:
                return Response({"message": "No tasks found in date range.", "data": []}, status=status.HTTP_200_OK)
            
            serializer = TodoTaskSerializer(tasks, many=True, context={'request': request})
            return Response(serializer.data)  # 200: Filtered list
        
        else:
            # Create mode (unchanged)
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