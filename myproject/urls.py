from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# ✅ Swagger schema setup
schema_view = get_schema_view(
   openapi.Info(
      title="Employee API",
      default_version='v1',
      description="API for managing employees, tasks, and categories",
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),

    # ✅ Your app routes
    path('', include('EmployeeApp.urls')),

    # ✅ Swagger and ReDoc documentation
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
