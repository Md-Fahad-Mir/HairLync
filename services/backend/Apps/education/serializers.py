from rest_framework import serializers
from .models import EducationCategory, EducationalContent


class EducationCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = EducationCategory
        fields = '__all__'
        read_only_fields = ['created_at']


class EducationalContentSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    author_name = serializers.CharField(source='author.full_name', read_only=True)

    class Meta:
        model = EducationalContent
        fields = '__all__'
        read_only_fields = ['view_count', 'created_at', 'updated_at']


class EducationalContentListSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = EducationalContent
        fields = [
            'id', 'title', 'slug', 'category_name', 'content_type',
            'difficulty', 'description', 'thumbnail', 'duration_minutes',
            'is_premium', 'view_count', 'created_at',
        ]
