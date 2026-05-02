# Interface with Hugging Face API and handles demo mode 

import os
from concurrent.futures import ThreadPoolExecutor
from huggingface_hub import InferenceClient
from django.conf import settings
from dotenv import load_dotenv
from pathlib import Path
from .models import ModelResponse

# Load environment variables from env
load_dotenv()

# Load backend path
backend_dir = Path(__file__).resolve().parent.parent

# Hugging Face Inferece API Class
class HuggingFaceAPIService:
    
    def __init__(self):
        # Assign Hugging Face API token or set to demo mode if not found
        self.api_token = os.getenv('HUGGING_FACE_API_TOKEN')
        self.demo_mode = not self.api_token

        # Display instructions for demo mode or define Inference provider
        if self.demo_mode:
            print('-----------------------------------------------------')
            print('Running in DEMO MODE, No Hugging Face API token found')
            print('Define HUGGING_FACE_API_TOKEN in the project root .env file')
            print('-----------------------------------------------------')
            self.client = None
        else:
            # No provider= → HF auto-routes each model to a supported provider.
            # Wider model availability than pinning Cerebras, at the cost of
            # variable per-provider latency (hence the bumped timeout).
            self.client = InferenceClient(api_key=self.api_token, timeout=60)
    # Get model info dictionary
    def get_model_info(self, model_id):
        for model in settings.AVAILABLE_MODELS:
            if model['id'] == model_id:
                return model
        return None
    
    def get_available_models(self):
        return settings.AVAILABLE_MODELS
    
    # Generate demo response
    def generate_mock_response(self, model_id, prompt):

        # Create demo responses for three chosen models
        mock_responses = {
            'meta-llama/Llama-3.1-8B-Instruct': {
                'greeting': "Hello! I'm Llama 3.1 8B, a helpful LLM! I can help you with a wide variety of tasks including writing, analysis, coding, and answering questions. How can I assist you today?",
                'question': "Good question! I am in demo mode, so I'm showing a preset demo response. With a valid Hugging Face API token, I will provide a detailed response to your prompt.",
                'code': "Here's a simple example:\n\n```python\ndef hello_world():\n    print('Hello from Llama 3.1 8B!')\n    return 'Demo mode active'\n```\n\nIn production mode with an API token, I can help with complex coding tasks.",
                'meaning': "42",
                'default': "Thank you for your prompt! I'm currently running in demo mode with preset responses. To get AI-generated content from Llama 3.1 8B, please define HUGGING_FACE_API_TOKEN in the project root .env file."
            },
            'Qwen/Qwen3-235B-A22B-Instruct-2507': {
                'greeting': "Hello! I'm Qwen 3, developed by Alibaba Cloud. I specialize in multilingual understanding and can assist with diverse tasks across languages and domains.",
                'question': "Excellent question! As Qwen 3, I would typically provide comprehensive, well-researched answers. This is a demo response - define an API token in the project root .env to unlock my full capabilities.",
                'code': "Here's a code snippet:\n\n```javascript\nconst qwenDemo = () => {\n  console.log('Qwen 3 demo mode');\n  return 'Add API token for real responses';\n};\n```\n\nWith proper authentication, I can assist with advanced programming tasks.",
                'meaning': "42",
                'default': "This is a demonstration response from Qwen 3. I'm running in demo mode because no Hugging Face API token was detected. For actual AI responses, please define HUGGING_FACE_API_TOKEN in the project root .env file."
            },
            'meta-llama/Llama-3.3-70B-Instruct': {
                'greeting': "Greetings! I'm Llama 3.3 70B, Meta's large language model. With 70 billion parameters, I excel at complex reasoning, creative writing, and technical problem-solving.",
                'question': "That's a thought-provoking inquiry! In full mode, I will provide detailed analysis. Currently showing a demo response - authenticate with a Hugging Face API token to access my complete reasoning capabilities.",
                'code': "Example code:\n\n```java\npublic class Llama33Demo {\n    public static void main(String[] args) {\n        System.out.println(\"Demo: Add API token for real AI\");\n    }\n}\n```\n\nWith API access, I can help with sophisticated software architecture and optimization.",
                'meaning': "42",
                'default': "Hello! I'm Llama 3.3 70B in demo mode. This is a preset response to demonstrate the interface. To experience my full language understanding and generation capabilities, please define HUGGING_FACE_API_TOKEN to your environment configuration."
            }
        }

        # Define demo response based on prompt
        prompt_lower = prompt.lower()
        if any(word in prompt_lower for word in ['hello', 'hi', 'hey', 'greetings']):
            response_type = 'greeting'
        elif any(word in prompt_lower for word in ['code', 'program', 'function', 'class', 'def']):
            response_type = 'code'
        elif '?' in prompt:
            response_type = 'question'
        elif all(word in prompt_lower for word in ['meaning', 'life']):
            response_type = 'meaning'
        else:
            response_type = 'default'

        # Get model demo response, falling back to a default model
        # if model_id has no preset entry (e.g. newly added models).
        model_responses = mock_responses.get(
            model_id, mock_responses['meta-llama/Llama-3.1-8B-Instruct']
        )
        response = model_responses.get(response_type, model_responses['default'])

        return "DEMO MODE " + response
    
    # Generate response in demo or production mode
    def generate_text(self, model_id, prompt, max_length=100):

        # In demo mode
        if self.demo_mode:
            return self.generate_mock_response(model_id, prompt)
        
        # If token is available, use Hugging Face Inference API
        try:
            completion = self.client.chat.completions.create(
                model=model_id,
                messages=[{'role':'user', 'content':prompt}],
                max_tokens=max_length,
            )
            return completion.choices[0].message.content
        except Exception as e:
            return f'Hugging Face API Error: {str(e)}'
        
    # Generate one model's response (used by the thread pool below).
    # DB write happens here so the caller doesn't have to coordinate it.
    def _generate_one(self, model_id, prompt):
        model_info = self.get_model_info(model_id)
        if not model_info:
            return None
        try:
            response_text = self.generate_text(
                model_id, prompt, max_length=model_info.get('max_length')
            )
            ModelResponse.objects.create(
                prompt=prompt,
                model_name=model_info['name'],
                model_id=model_id,
                response=response_text,
            )
            return {
                'model_id': model_id,
                'model_name': model_info['name'],
                'response': response_text,
                'success': True,
                'demo_mode': self.demo_mode,
            }
        except Exception as e:
            return {
                'model_id': model_id,
                'model_name': model_info['name'],
                'response': f'Error: {str(e)}',
                'success': False,
                'demo_mode': self.demo_mode,
            }

    # Run all model calls in parallel so total latency = slowest, not sum.
    def process_prompt_with_models(self, prompt, model_ids):
        if not model_ids:
            return []
        with ThreadPoolExecutor(max_workers=len(model_ids)) as pool:
            results = list(pool.map(lambda mid: self._generate_one(mid, prompt), model_ids))
        return [r for r in results if r is not None]
        return responses