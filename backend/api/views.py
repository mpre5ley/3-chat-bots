# API Endpoints

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.conf import settings
from .serializers import (
    PromptRequestSerializer, 
    ModelInfoSerializer, 
    ModelResponseSerializer,
    PromptSessionSerializer
)
from .services import HuggingFaceAPIService
from .models import ModelResponse, PromptSession

# Decorator to accept POST requests
# Main endpoint for frontend calls
@api_view(['POST'])
def process_prompt(request):
    # Validate input or return error
    serializer = PromptRequestSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    # Get prompt and model ids
    prompt = serializer.validated_data['prompt']
    model_ids = serializer.validated_data['model_ids']

    # Create Hugging Face service instance, process prompt, create session
    try:
        service = HuggingFaceAPIService()
        responses = service.process_prompt_with_models(prompt, model_ids)
        session = PromptSession.objects.create(prompt=prompt)
        
        # Add responses to the db session
        for response_data in responses:
            if response_data['success']:
                model_response = ModelResponse.objects.filter(
                    prompt=prompt,
                    model_id=response_data['model_id']
                ).first()
                if model_response:
                    session.responses.add(model_response)
        
        return Response({
            'session_id': session.id,
            'prompt': prompt,
            'responses': responses,
            'timestamp': session.created_at
        })
        
    except Exception as e:
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

# Decorator to accept GET requests
# Return list of available models
@api_view(['GET'])
def get_models(request):
    models = settings.AVAILABLE_MODELS
    serializer = ModelInfoSerializer(models, many=True)
    return Response(serializer.data)

# Decorator to accept GET requests
# Return last 50 responses
@api_view(['GET'])
def get_responses(request):
    responses = ModelResponse.objects.all()[:50]
    serializer = ModelResponseSerializer(responses, many=True)
    return Response(serializer.data)

# Decorator to accept GET requests
# Return last 20 sessions
@api_view(['GET'])
def get_sessions(request):
    sessions = PromptSession.objects.all()[:20]
    serializer = PromptSessionSerializer(sessions, many=True)
    return Response(serializer.data)

# Decorator to accept GET requests
# Return session by session id
@api_view(['GET'])
def get_session(request, session_id):
    try:
        session = PromptSession.objects.get(id=session_id)
        serializer = PromptSessionSerializer(session)
        return Response(serializer.data)
    except PromptSession.DoesNotExist:
        return Response(
            {'error': 'Session not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )