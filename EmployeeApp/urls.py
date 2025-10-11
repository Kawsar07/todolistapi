from django.urls import path
from .views import (
    RegisterView, ProfileView, todoTaskApi, todoTaskDetail,
    categoryListCreateApi, categoryDetailApi, ForgotPasswordView,
    OTPVerificationView, ChangePasswordView, login
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', login, name='login'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('todo/', todoTaskApi, name='todo_list_create'),
    path('todo/<int:pk>/', todoTaskDetail, name='todo_detail'),
    path('categories/', categoryListCreateApi, name='category_list_create'),
    path('categories/<int:pk>/', categoryDetailApi, name='category_detail'),
    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot_password'),
    path('verify-otp/', OTPVerificationView.as_view(), name='verify_otp'),
    path('change-password/', ChangePasswordView.as_view(), name='change_password'),
]