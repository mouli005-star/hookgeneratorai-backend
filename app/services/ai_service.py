import os
import asyncio
import aiohttp
from dotenv import load_dotenv

load_dotenv()

class AIService:
    def __init__(self):
        self.api_key = os.getenv("HF_TOKEN")
        # Detect if it's a placeholder
        if self.api_key and ("your_" in self.api_key or "hf_" not in self.api_key.lower()):
            if self.api_key != "":
                 self.api_key = None
        
        # Use HuggingFace Inference API endpoint
        # Option 1: FLAN-T5 (faster, smaller) - uncomment to use
        # self.api_url = "https://api-inference.huggingface.co/models/google/flan-t5-large"
        
        # Option 2: Mistral-7B (better quality, slower) - currently active
        self.api_url = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2"
        
        print(f"✅ AIService initialized. Token available: {bool(self.api_key)}")

    async def generate(self, prompt: str, task_type: str) -> str:
        # 1. Handle Mock Mode (No API Key)
        if not self.api_key:
            print("⚠️ No HF_TOKEN found, using mock mode")
            await asyncio.sleep(0.5)
            if task_type == "hooks":
                return f"🚀 VIRAL HOOKS FOR: '{prompt}'\n\n1. This is the secret nobody tells you about content creation...\n2. Stop scrolling if you want to double your reach in 24 hours.\n3. I tried this one trick and it changed everything."
            else:
                return f"✨ REWRITTEN CONTENT:\n\nOptimize your '{prompt}' by focusing on the 'Hook-Story-Offer' framework."

        # 2. Build the prompt (optimized for Mistral instruction model)
        if task_type == "hooks":
            full_prompt = f"""Generate 15 engaging viral hooks for social media about: {prompt}

Format each hook on a new line, numbered 1-15. Make them attention-grabbing, curiosity-driven, and optimized for maximum engagement."""
        elif task_type == "hashtags":
            full_prompt = f"""Generate 20 trending hashtags for: {prompt}

Format as a comma-separated list. Mix popular trending tags with niche-specific ones."""
        else:
            full_prompt = f"""Rewrite the following content to be viral and engaging: {prompt}

Make it more compelling, add hooks, and optimize for social media engagement."""

        # 3. Make HTTP request directly
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "inputs": full_prompt,
            "parameters": {
                "max_new_tokens": 800,
                "temperature": 0.7,
                "top_p": 0.95,
                "return_full_text": False
            }
        }

        try:
            print(f"   → Calling HuggingFace API for '{prompt[:30]}...'")
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.api_url,
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    
                    if response.status == 200:
                        data = await response.json()
                        
                        # HF Inference API can return different formats:
                        # Format 1: List with dict containing "generated_text"
                        if isinstance(data, list) and len(data) > 0:
                            if isinstance(data[0], dict):
                                result = data[0].get("generated_text", "").strip()
                            else:
                                result = str(data[0]).strip()
                        # Format 2: Direct dict with "generated_text"
                        elif isinstance(data, dict):
                            result = data.get("generated_text", "").strip()
                        # Format 3: Direct string
                        else:
                            result = str(data).strip()
                        
                        if result:
                            print(f"   ✅ AI Success! Got {len(result)} chars")
                            return result
                        else:
                            print(f"   ⚠️ Empty response: {data}")
                            return "AI returned empty. Please try again."
                    
                    elif response.status == 503:
                        error_text = await response.text()
                        print(f"   ⚠️ Model loading (503): {error_text}")
                        return f"🔄 AI model is warming up. This takes ~20 seconds on first use. Please try again in a moment."
                    
                    else:
                        error_text = await response.text()
                        print(f"   ❌ API Error {response.status}: {error_text}")
                        return f"⚠️ API Error ({response.status}). Using backup hook:\n\n'Why most people fail at this and how you can win.'"
                        
        except asyncio.TimeoutError:
            print("   ❌ Request timeout")
            return "⚠️ Request timeout. The AI is busy. Please try again."
        except Exception as e:
            print(f"   ❌ Generation Error: {type(e).__name__}: {e}")
            return f"⚠️ Service busy. Here is a backup viral hook for: '{prompt}'\n\n'Why most people fail at this and how you can win.'"
