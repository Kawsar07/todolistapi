from rest_framework import serializers
from .models import TodoTask, Category, Profile
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from django.db.models import Q

class CategorySerializer(serializers.ModelSerializer):
    is_editable = serializers.SerializerMethodField()
    type = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'is_general', 'is_editable', 'type']
        read_only_fields = ['is_general']

    def get_is_editable(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.is_editable_by(request.user)
        return False

    def get_type(self, obj):
        return 'general' if obj.is_general else 'personal'


class TodoTaskSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), source='category', write_only=True, required=False
    )
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = TodoTask
        fields = ['id', 'name', 'description', 'due_date', 'is_completed', 'category', 'category_id', 'user']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            # Users can assign both general and their personal categories
            self.fields['category_id'].queryset = Category.objects.filter(
                Q(is_general=True) | Q(creator=request.user)
            )

    def validate(self, attrs):
        """
        If no category is provided, assign profile.default_category if set,
        otherwise assign the shared Default Category.
        """
        request = self.context.get('request')
        if not attrs.get('category') and request:
            profile, _ = Profile.objects.get_or_create(user=request.user)
            if profile.default_category:
                attrs['category'] = profile.default_category
            else:
                default_cat = Category.get_default_category()
                profile.default_category = default_cat
                profile.save(update_fields=['default_category'])
                attrs['category'] = default_cat
        return attrs


class ProfileSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    image = serializers.ImageField(write_only=True, required=False, allow_null=True)
    default_category = CategorySerializer(read_only=True)
    default_category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), source='default_category', write_only=True, required=False
    )

    class Meta:
        model = Profile
        fields = ['name', 'location', 'image_url', 'image', 'default_category', 'default_category_id']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            self.fields['default_category_id'].queryset = Category.objects.filter(
                Q(is_general=True) | Q(creator=request.user)
            )

    def get_image_url(self, obj):
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
        return None


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        user = User.objects.filter(email=email).first()
        if user and user.check_password(password):
            refresh = RefreshToken.for_user(user)
            return {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        raise serializers.ValidationError('Invalid credentials')


class RegistrationSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(min_length=6)
    name = serializers.CharField(max_length=100)
    location = serializers.CharField(max_length=100, required=False, allow_blank=True)
    image = serializers.ImageField(required=False, allow_null=True)

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already registered")
        return value

    def validate_image(self, value):
        if value is not None:
            if not value.name.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
                raise serializers.ValidationError("Invalid image format. Use JPG, PNG, or GIF.")
        return value

    def create(self, validated_data):
        image = validated_data.pop('image', None)
        password = validated_data.pop('password')
        email = validated_data.pop('email')

        user = User.objects.create_user(
            username=email,
            email=email,
            password=password,
        )

        profile_data = {k: v for k, v in validated_data.items() if k in ['name', 'location']}
        profile = Profile.objects.create(user=user, **profile_data)

        # Assign the shared default category to new users
        default_category = Category.get_default_category()
        profile.default_category = default_category
        profile.save()

        if image:
            profile.image = image
            profile.save()

        return user
