from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

ROLE_CHOICES = (
    ('superadmin', 'SuperAdmin'),
    ('admin', 'Admin'),
    ('user', 'User'),
)

STATUS_CHOICES = (
    ('approved', 'Approved'),
    ('pending', 'Pending'),
    ('rejected', 'Rejected'),
)

class Category(models.Model):
    name = models.CharField(max_length=100)
    creator = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='categories',
        null=True,
        blank=True
    )
    is_general = models.BooleanField(default=False)
    created_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "todo_category"
        ordering = ['-is_general', 'name']

    def __str__(self):
        return f"{self.name} ({'General' if self.is_general else 'Personal'})"

    @staticmethod
    def get_default_category():
        category, created = Category.objects.get_or_create(
            name="Default Category",
            defaults={"is_general": True, "creator": None}
        )
        if not category.is_general or category.creator is not None:
            category.is_general = True
            category.creator = None
            category.save(update_fields=['is_general', 'creator'])
        return category

    def is_editable_by(self, user):
        return not self.is_general and self.creator == user

    def save(self, *args, **kwargs):
        if not self.pk and not self.created_at:
            self.created_at = timezone.now()
        super().save(*args, **kwargs)

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=100, blank=True)
    image = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    default_category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='default_profiles'
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='user')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='approved')

    class Meta:
        db_table = "todo_profile"

    def __str__(self):
        return f"{self.name} ({self.user.email})"

class TodoTask(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tasks')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    due_date = models.DateTimeField(blank=True, null=True)
    is_completed = models.BooleanField(default=False)
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tasks'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "todo_task"
        ordering = ['-created_at']

    def __str__(self):
        status = "✓" if self.is_completed else "○"
        return f"{status} {self.name}"

class OTP(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='otps')
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)

    class Meta:
        db_table = "todo_otp"

    def __str__(self):
        return f"OTP {self.otp} for {self.user.email}"

class PendingRegistration(models.Model):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=100)
    password = models.CharField(max_length=128)
    location = models.CharField(max_length=100, blank=True)
    image = models.ImageField(upload_to='pending_profile_pics/', blank=True, null=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "todo_pending_registration"

    def __str__(self):
        return f"Pending Registration: {self.email} ({self.status})"