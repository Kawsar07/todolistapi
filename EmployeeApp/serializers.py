# from rest_framework import serializers
# from .models import Department, Employee

# class DepartmentSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Department
#         fields = ['DepartmentId', 'DepartmentName']

# class EmployeeSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Employee
#         fields = ['EmployeeId', 'EmployeeName', 'Department', 'DateOfJoining', 'PhotoFileName']
from rest_framework import serializers
from .models import TodoTask

class TodoTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = TodoTask
        fields = ['id', 'name', 'description', 'due_date', 'is_completed']
