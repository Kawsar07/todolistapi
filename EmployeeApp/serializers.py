from rest_framework import serializers
from .models import TodoTask, Category

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']

class TodoTaskSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), source='category', write_only=True
    )

    class Meta:
        model = TodoTask
        fields = ['id', 'name', 'description', 'due_date', 'is_completed', 'category', 'category_id']
