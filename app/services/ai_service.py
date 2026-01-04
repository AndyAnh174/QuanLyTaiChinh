"""
AI Service abstraction layer for Gemini and Ollama
"""
import os
import base64
from typing import Optional, Dict, Any, List
from django.conf import settings
from google import genai
from google.genai import types
import requests


class AIService:
    """
    Unified AI service that can switch between Gemini (cloud) and Ollama (local)
    Uses Gemini 3 Flash which supports both text and vision in one model
    """
    
    def __init__(self):
        self.gemini_api_key = settings.GEMINI_API_KEY
        self.gemini_model_name = settings.GEMINI_MODEL_NAME
        self.ollama_url = settings.OLLAMA_URL
        self.use_ollama = os.getenv("USE_OLLAMA", "False").lower() == "true"
        
        # Initialize Gemini 3 Flash client if API key is provided
        if self.gemini_api_key and self.gemini_api_key != "your_gemini_key":
            try:
                # Use v1alpha API version for media_resolution support
                self.gemini_client = genai.Client(
                    api_key=self.gemini_api_key,
                    http_options={'api_version': 'v1alpha'}
                )
            except Exception as e:
                print(f"Warning: Failed to initialize Gemini: {e}")
                self.gemini_client = None
        else:
            self.gemini_client = None
    
    def generate_text(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """
        Generate text using LLM (Gemini 3 Flash or Ollama)
        
        Args:
            prompt: User prompt
            system_prompt: Optional system prompt for context
        
        Returns:
            Generated text response
        """
        if self.use_ollama and self.ollama_url:
            return self._generate_with_ollama(prompt, system_prompt)
        elif self.gemini_client:
            return self._generate_with_gemini(prompt, system_prompt)
        else:
            raise Exception("No AI service available. Configure Gemini API key or Ollama URL.")
    
    def analyze_image(self, image_data: bytes, prompt: str, mime_type: str = "image/jpeg") -> str:
        """
        Analyze image using Gemini 3 Flash (supports both text and vision)
        
        Args:
            image_data: Image bytes
            prompt: Prompt for image analysis
            mime_type: MIME type of image (default: image/jpeg)
        
        Returns:
            Analysis result text
        """
        if self.gemini_client:
            return self._analyze_image_with_gemini(image_data, prompt, mime_type)
        else:
            raise Exception("Vision API not available. Gemini requires API key.")
    
    def generate_with_image(self, text_prompt: str, image_data: bytes, 
                           mime_type: str = "image/jpeg", 
                           system_prompt: Optional[str] = None) -> str:
        """
        Generate response with both text and image using Gemini 3 Flash
        
        Args:
            text_prompt: Text prompt
            image_data: Image bytes
            mime_type: MIME type of image
            system_prompt: Optional system prompt
        
        Returns:
            Generated response text
        """
        if self.gemini_client:
            return self._generate_with_image_gemini(text_prompt, image_data, mime_type, system_prompt)
        else:
            raise Exception("Gemini API not available. Configure API key.")
    
    def _generate_with_gemini(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generate text using Gemini 3 Flash"""
        full_prompt = prompt
        if system_prompt:
            full_prompt = f"{system_prompt}\n\n{prompt}"
        
        try:
            response = self.gemini_client.models.generate_content(
                model=self.gemini_model_name,
                contents=[
                    types.Content(
                        parts=[types.Part(text=full_prompt)]
                    )
                ]
            )
            return response.text
        except Exception as e:
            raise Exception(f"Gemini API error: {e}")
    
    def _analyze_image_with_gemini(self, image_data: bytes, prompt: str, mime_type: str) -> str:
        """Analyze image using Gemini 3 Flash"""
        try:
            response = self.gemini_client.models.generate_content(
                model=self.gemini_model_name,
                contents=[
                    types.Content(
                        parts=[
                            types.Part(text=prompt),
                            types.Part(
                                inline_data=types.Blob(
                                    mime_type=mime_type,
                                    data=image_data,  # image_data is already bytes
                                ),
                                media_resolution={"level": "media_resolution_high"}
                            )
                        ]
                    )
                ]
            )
            return response.text
        except Exception as e:
            raise Exception(f"Gemini Vision API error: {e}")
    
    def _generate_with_image_gemini(self, text_prompt: str, image_data: bytes, 
                                    mime_type: str, system_prompt: Optional[str] = None) -> str:
        """Generate response with both text and image"""
        try:
            # Combine system prompt and user prompt
            full_prompt = text_prompt
            if system_prompt:
                full_prompt = f"{system_prompt}\n\n{text_prompt}"
            
            response = self.gemini_client.models.generate_content(
                model=self.gemini_model_name,
                contents=[
                    types.Content(
                        parts=[
                            types.Part(text=full_prompt),
                            types.Part(
                                inline_data=types.Blob(
                                    mime_type=mime_type,
                                    data=image_data,  # image_data is already bytes
                                ),
                                media_resolution={"level": "media_resolution_high"}
                            )
                        ]
                    )
                ]
            )
            return response.text
        except Exception as e:
            raise Exception(f"Gemini API error: {e}")
    
    def _generate_with_ollama(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generate text using Ollama"""
        full_prompt = prompt
        if system_prompt:
            full_prompt = f"{system_prompt}\n\n{prompt}"
        
        try:
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": "llama2",  # Default model, can be configured
                    "prompt": full_prompt,
                    "stream": False
                },
                timeout=30
            )
            response.raise_for_status()
            result = response.json()
            return result.get("response", "")
        except Exception as e:
            raise Exception(f"Ollama API error: {e}")


# Singleton instance
ai_service = AIService()

