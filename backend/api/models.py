# Create database tables using Django models for LLM interaction

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

    # Config class for Django to set default ordering
    class Meta:
        ordering = ['-created_at']

    # Defines how db object appears in logs
    def __str__(self):
        return f"{self.model_name} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"
    
class PromptSession(models.Model):
    # The entered prompt
    prompt = models.TextField()

    # Session creation time
    created_at = models.DateTimeField(default=timezone.now)

    # Links the responses to each session
    responses = models.ManyToManyField(ModelResponse, related_name='sessions')

    # Config class for Django to set default ordering
    class Meta:
        ordering = ['-created_at']

    # Defines how db object appears in logs
    def __str__(self):
        return f"Session {self.id} - {self.created_at.strftime('%Y-%m-%d %H:%M')}" 


    
