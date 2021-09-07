from .models import Category, Story
from rest_framework import serializers


class StorySerializer(serializers.HyperlinkedModelSerializer):
    category = serializers.CharField(source='category.id')
    class Meta:
        model = Story
        fields = '__all__'