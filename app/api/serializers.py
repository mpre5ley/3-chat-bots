# Define how data moves between Python objects and JSON, how to validate API requests

from rest_framework import serializers
from .models import ModelResponse, PromptSession

# Converts model instances to JSON
class ModelResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = ModelResponse
        fields = ['id', 'prompt', 'model_name', 'model_id', 'response', 'created_at']

# Represents a session including all model responses
class PromptSessionSerializer(serializers.ModelSerializer):
    responses = ModelResponseSerializer(many=True, read_only=True)
    
    class Meta:
        model = PromptSession
        fields = ['id', 'prompt', 'created_at', 'responses']

# Validates POST requests
class PromptRequestSerializer(serializers.Serializer):
    prompt = serializers.CharField(max_length=2000)
    model_ids = serializers.ListField(
        child=serializers.CharField(max_length=100),
        min_length=1,
        max_length=6
    )
# Creates metadata for frontend config
class ModelInfoSerializer(serializers.Serializer):
    id = serializers.CharField()
    name = serializers.CharField()
    description = serializers.CharField()
    max_length = serializers.IntegerField(required=False)