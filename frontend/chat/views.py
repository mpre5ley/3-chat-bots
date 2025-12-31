# Views for application frontend

import requests
from django.shortcuts import render
from django.http import JsonResponse
from django.conf import settings
from django.views.decorators.http import require_http_methods
import json

# Fetches model list from backend
def index(request):
    try:
        response = requests.get(f"{settings.BACKEND_API_URL}/models/", timeout=10)
        models = response.json() if response.status_code == 200 else []
    except requests.RequestException:
        models = []
    return render(request, 'chat/index.html', {'models': models})

# Decorator to accept POST requests
# Handle prompt and model selection, send to backend, listen for response
@require_http_methods(["POST"])
def chat(request):
    try:
        data = json.loads(request.body)
        prompt = data.get('prompt', '')
        model_ids = data.get('model_ids', [])
        if not prompt or not model_ids:
            return JsonResponse({'error': 'Prompt and model selection required'}, status=400)
        
        # Send to backend API
        response = requests.post(
            f"{settings.BACKEND_API_URL}/prompt/",
            json={'prompt': prompt, 'model_ids': model_ids},
            timeout=60
        )
        return JsonResponse(response.json(), status=response.status_code)
    except requests.RequestException as e:
        return JsonResponse({'error': f'Backend connection error: {str(e)}'}, status=503)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
