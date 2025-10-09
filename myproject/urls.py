# myproject/urls.py (updated for media serving)
from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
from django.conf import settings  # ✅ Added for media
from django.conf.urls.static import static  # ✅ Added for media

# Custom serializer for login to match your custom LoginSerializer (email instead of username)
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = 'email'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields[self.username_field] = serializers.EmailField()

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        user = self.UserClass.objects.filter(email=email).first()
        if user and user.check_password(password):
            refresh = self.get_token(user)
            return {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        raise serializers.ValidationError('Invalid credentials')

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

# ✅ Swagger schema setup
schema_view = get_schema_view(
   openapi.Info(
      title="Employee API",
      default_version='v1',
      description="API for managing employees, tasks, and categories with JWT auth",
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),

    # ✅ Your app routes
    path('api/', include('EmployeeApp.urls')),

    # ✅ JWT Token endpoints (for Swagger login)
    path('api/token/login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),  # Login with email/password
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # ✅ Swagger and ReDoc documentation
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]

# ✅ Serve media files in development (add this)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)