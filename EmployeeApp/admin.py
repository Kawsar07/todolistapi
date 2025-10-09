from django.contrib import admin
from .models import Category, Profile, TodoTask

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_general', 'creator', 'created_at']
    list_filter = ['is_general', 'created_at']
    search_fields = ['name']
    readonly_fields = ['created_at']

    def save_model(self, request, obj, form, change):
        # If creating a general category, set creator to None
        if obj.is_general:
            obj.creator = None
        super().save_model(request, obj, form, change)


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'name', 'location', 'default_category']
    search_fields = ['user__email', 'name']


@admin.register(TodoTask)
class TodoTaskAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'category', 'is_completed', 'due_date']
    list_filter = ['is_completed', 'category', 'created_at']
    search_fields = ['name', 'description', 'user__email']
    readonly_fields = ['created_at', 'updated_at']
