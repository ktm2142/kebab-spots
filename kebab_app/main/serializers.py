from rest_framework import serializers
from .models import KebabSpot


class KebabSpotSerializer(serializers.ModelSerializer):
    class Meta:
        model = KebabSpot
        fields = ['id', 'name', 'description', 'latitude', 'longitude', 'created_by', 'created_at', 'updated_at']
        read_only_fields = ['created_by', 'created_at', 'updated_at']
