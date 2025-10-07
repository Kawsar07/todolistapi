from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import TodoTask, Category
from .serializers import TodoTaskSerializer, CategorySerializer

# ✅ TodoTask List and Create
@api_view(['GET', 'POST'])
def todoTaskApi(request):
    if request.method == 'GET':
        tasks = TodoTask.objects.all()
        serializer = TodoTaskSerializer(tasks, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        serializer = TodoTaskSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Task added successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# ✅ TodoTask Detail, Update, Delete
@api_view(['GET', 'PUT', 'DELETE'])
def todoTaskDetail(request, pk):
    try:
        task = TodoTask.objects.get(pk=pk)
    except TodoTask.DoesNotExist:
        return Response({"error": "Task not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = TodoTaskSerializer(task)
        return Response(serializer.data)
    elif request.method == 'PUT':
        serializer = TodoTaskSerializer(task, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Task updated successfully"})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        task.delete()
        return Response({"message": "Task deleted successfully"}, status=status.HTTP_204_NO_CONTENT)

# ✅ Category List and Create
@api_view(['GET', 'POST'])
def categoryListCreateApi(request):
    if request.method == 'GET':
        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Category added successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# ✅ Category Detail, Update, Delete
@api_view(['GET', 'PUT', 'DELETE'])
def categoryDetailApi(request, pk):
    try:
        category = Category.objects.get(pk=pk)
    except Category.DoesNotExist:
        return Response({"error": "Category not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = CategorySerializer(category)
        return Response(serializer.data)
    elif request.method == 'PUT':
        serializer = CategorySerializer(category, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Category updated successfully"})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        category.delete()
        return Response({"message": "Category deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
