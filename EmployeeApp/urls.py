from django.urls import path
from .views import (
    todoTaskApi, todoTaskDetail,
    categoryListCreateApi, categoryDetailApi,
    login,
    RegisterView,
    ProfileView
)

urlpatterns = [
    path('register/', RegisterView.as_view()),
    path('login/', login),
    path('profile/', ProfileView.as_view()),
    path('todo/', todoTaskApi),
    path('todo/<int:pk>/', todoTaskDetail),
    path('categories/', categoryListCreateApi),
    path('categories/<int:pk>/', categoryDetailApi),
]