from django.urls import path


from .views import (
    todoTaskApi, todoTaskDetail,
    categoryListCreateApi, categoryDetailApi
)

urlpatterns = [
    path('todo/', todoTaskApi),               # GET all, POST new
    path('todo/<int:pk>/', todoTaskDetail),   # GET one, PUT, DELETE
    path('categories/', categoryListCreateApi),         # GET all, POST new
    path('categories/<int:pk>/', categoryDetailApi),    # GET one, PUT, DELETE
]
