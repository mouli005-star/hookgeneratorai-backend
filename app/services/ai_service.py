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
        
        self.model = "meta-llama/Llama-3.2-1B-Instruct"
        # Use Async client for non-blocking calls
        self.client = AsyncInferenceClient(token=self.api_key) if self.api_key else None

    async def generate(self, prompt: str, task_type: str) -> str:
        # 1. Handle Mock Mode (No API Key)
        if not self.api_key:
            await asyncio.sleep(0.5)
            if task_type == "hook":
                return f"🚀 VIRAL HOOKS FOR: '{prompt}'\n\n1. This is the secret nobody tells you about content creation...\n2. Stop scrolling if you want to double your reach in 24 hours.\n3. I tried this one trick and it changed everything."
            else:
                return f"✨ REWRITTEN CONTENT:\n\nOptimize your '{prompt}' by focusing on the 'Hook-Story-Offer' framework."

        # 2. Handle Real Mode
        system_msg = (
            "You are a world-class, creative social media strategist and viral copywriter. "
            "Your goal is to be helpful and imaginative. If the user provides short or nonsense text like 'dfjdf', "
            "treat it as a creative placeholder and generate content based on what a viral creator would post today. "
            "DO NOT refuse to generate content. Always provide 15-20 hooks or hashtags regardless of the input."
        )
        
        if task_type == "hook":
            user_msg = f"Generate 15-20 distinct, viral hooks for this content/topic: '{prompt}'. Vary styles: curiosity, controversial, story, and listicles."
        elif task_type == "hashtags":
            user_msg = f"Provide 20 optimized, trending hashtags for: '{prompt}'."
        else:
            user_msg = f"Rewrite this content to be 10x more engaging: '{prompt}'. Make it punchy and bold."

        messages = [
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_msg}
        ]

        try:
            # TRUE ASYNC CHAT COMPLETION
            response = await self.client.chat_completion(
                messages,
                max_tokens=1000, 
                model=self.model,
                temperature=0.8 # More creative
            )
            
            if response and hasattr(response, 'choices') and len(response.choices) > 0:
                return response.choices[0].message.content
            
            print(f"⚠️ AI returned empty response: {response}")
            return "AI returned an empty response. Please try again."
        except Exception as e:
            print(f"AI Generation Error: {e}")
            return f"⚠️ Service busy. Here is a backup viral hook for: '{prompt}'\n\n'Why most people fail at this and how you can win.'"
