# Create models to handle responses from Hugging Face LLMs

from django.db import models
from django.utils import timezone

class ModelResponse(models.Model):
    # User question
    prompt = models.TextField()

    # Model display name
    model_name = models.CharField(max_length=100)

    # Hugging Face LLM Model ID
    model_id = models.CharField(max_length=100)

    # LLM response
    reponse = models.TextField()

    # Timestamp 
    created_at = models.DateTimeField(default=timezone.now)

    
