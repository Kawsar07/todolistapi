import django_filters
from .models import TodoTask

class TodoTaskFilter(django_filters.FilterSet):
    start_date = django_filters.DateTimeFilter(field_name='due_date', lookup_expr='gte')  
    end_date = django_filters.DateTimeFilter(field_name='due_date', lookup_expr='lte')    

    class Meta:
        model = TodoTask
        fields = ['start_date', 'end_date']  