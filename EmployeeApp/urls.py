from django.urls import path
from .views import todoTaskApi  # ✅ Correct import

from django.urls import path
from .views import todoTaskApi, todoTaskDetail

urlpatterns = [
    path('todo/', todoTaskApi),              # GET all, POST new
    path('todo/<int:pk>/', todoTaskDetail),  # GET one, PUT, DELETE
]
