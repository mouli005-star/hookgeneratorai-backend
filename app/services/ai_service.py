import os
import asyncio
from huggingface_hub import AsyncInferenceClient
from dotenv import load_dotenv

load_dotenv()

class AIService:
    def __init__(self):
        self.api_key = os.getenv("HF_TOKEN")
        # Detect if it's a placeholder
        if self.api_key and ("your_" in self.api_key or "hf_" not in self.api_key.lower()):
            if self.api_key != "": # Only clear if it's actually set to something suspicious
                 self.api_key = None
        
        # Using Llama-3.1-8B which is more powerful and reliable on the free API
        self.model = "meta-llama/Llama-3.1-8B-Instruct"
        # Use Async client with a longer timeout
        self.client = AsyncInferenceClient(token=self.api_key, timeout=30) if self.api_key else None

    async def generate(self, prompt: str, task_type: str) -> str:
        # Detect if it's nonsense or repetitive
        if len(set(prompt.split())) < 2 and len(prompt) > 20:
             return "Please provide more specific details or a clear topic for better results."

        # 1. Handle Mock Mode (No API Key)
        if not self.api_key:
            await asyncio.sleep(0.5)
            return "⚠️ AI Configuration Error: Missing HF_TOKEN in environment variables."

        # 2. Handle Real Mode
        system_msg = (
            "You are a world-class, creative social media strategist and viral copywriter. "
            "Generate high-impact, viral-potential content. "
            "Output formatting: Use clear numbers, bold headings, and emojis. "
            "Style: Psychological hooks, curiosity gaps, and strong calls to action."
        )
        
        if task_type == "hook":
            user_msg = f"Generate 10 viral hooks for: '{prompt}'. Vary styles: curiosity, controversial, story, and listicles."
        elif task_type == "hashtags":
            user_msg = f"Provide 20 high-reach, relevant hashtags for: '{prompt}'."
        else:
            user_msg = f"Rewrite this for maximum engagement: '{prompt}'. Use the AIDA framework."

        messages = [
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_msg}
        ]

        try:
            # TRUE ASYNC CHAT COMPLETION
            response = await self.client.chat_completion(
                messages,
                max_tokens=800, 
                model=self.model,
                temperature=0.7
            )
            
            if response and hasattr(response, 'choices') and len(response.choices) > 0:
                content = response.choices[0].message.content
                if content and len(content.strip()) > 10:
                    return content
            
            return "The AI returned a short or empty response. Please try with a more detailed prompt."

        except Exception as e:
            error_str = str(e).lower()
            print(f"❌ AI Generation Error: {e}")
            
            if "model is overloaded" in error_str or "loading" in error_str:
                return "🚀 The AI model is currently busy. Please wait 10 seconds and click 'Regenerate'—it will work once the model is finished loading!"
            elif "401" in error_str or "authorization" in error_str:
                return "🛑 AI Token Error: Your Hugging Face token is invalid. Please check the HF_TOKEN in your Render settings."
            
            return f"⚠️ The AI generation service is temporarily unavailable. Error: {str(e)[:50]}..."
