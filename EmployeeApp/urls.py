from django.urls import path
from .views.register import RegisterView
from .views.login import login
from .views.profile import ProfileView
from .views.todo import todoTaskApi, todoTaskDetail
from .views.category import categoryListCreateApi, categoryDetailApi
from .views.forgot_password import ForgotPasswordView
from .views.otp_verification import OTPVerificationView
from .views.change_password import ChangePasswordView

app_name = 'EmployeeApp'

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