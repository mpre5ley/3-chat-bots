# Interface with Hugging Face API and handles demo mode 

import os
from huggingface_hub import InferenceClient
from django.conf import settings
from dotenv import load_dotenv
from pathlib import Path
from .models import ModelResponse, PromptSession

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
            print('Define HUGGING_FACE_API_TOKEN in .\backend\.env')
            print('-----------------------------------------------------')
            self.client = None
        else:
            self.client = InferenceClient(provider='cerebras', 
                                          api_key=self.api_token)
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
                'default': "Thank you for your prompt! I'm currently running in demo mode with preset responses. To get AI-generated content from Llama 3.1 8B, please define HUGGING_FACE_API_TOKEN to the .\backend\.env file."
            },
            'Qwen/Qwen3-235B-A22B-Instruct-2507': {
                'greeting': "Hello! I'm Qwen 3, developed by Alibaba Cloud. I specialize in multilingual understanding and can assist with diverse tasks across languages and domains.",
                'question': "Excellent question! As Qwen 3, I would typically provide comprehensive, well-researched answers. This is a demo response - define an API token in .\backend\.env to unlock my full capabilities.",
                'code': "Here's a code snippet:\n\n```javascript\nconst qwenDemo = () => {\n  console.log('Qwen 3 demo mode');\n  return 'Add API token for real responses';\n};\n```\n\nWith proper authentication, I can assist with advanced programming tasks.",
                'meaning': "42",
                'default': "This is a demonstration response from Qwen 3. I'm running in demo mode because no Hugging Face API token was detected in .env. For actual AI responses, please define HUGGING_FACE_API_TOKEN in .\backend\.env."
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
            reponse_type = 'greeting'
        elif any(word in prompt_lower for word in ['code', 'program', 'function', 'class', 'def']):
            reponse_type = 'code'
        elif '?' in prompt:
            reponse_type = 'question'
        elif all(word in prompt_lower for word in ['meaning', 'life']):
            response_type = 'meaning'
        else:
            response_type = 'default'

        # Get model demo response
        model_responses = mock_responses.get(model_id)
        reponse = model_responses.get(response_type)

        return "DEMO MODE" + reponse
    
    # Generate reponse in demo or production mode
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
        
    # Loop through each model, generate reponse, save to db
    def process_prompt_with_models(self, prompt, model_ids):
        responses = []
        for model_id in model_ids:
            try:
                model_info = self.get_model_info(model_id)
                # if model id not found, skip model
                if not model_info:
                    continue
                max_length = model_info.get('max_length')
                response_text = self.generate_text(model_id,
                                                   prompt,
                                                   max_length=max_length)
                # Save to db
                ModelResponse.objects.create(prompt=prompt,
                                             model_name=model_info['name'],
                                             model_id=model_id,
                                             response=response_text)
                responses.append({
                    'model_id' : model_id,
                    'model_name' : model_info['name'],
                    'response' : response_text,
                    'success' : True,
                    'demo_mode' : self.demo_mode
                })
            except Exception as e:
                model_name = model_info['name'] if model_info else 'unknown'
                responses.append({
                    'model_id' : model_id,
                    'model_name' : model_name,
                    'response' : f'Error: {str(e)}',
                    'success' : False,
                    'demo_mode' : self.demo_mode
                })
        return responses