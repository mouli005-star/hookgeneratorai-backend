import os
from huggingface_hub import InferenceClient
from dotenv import load_dotenv

# 1. Load your .env
load_dotenv()
api_key = os.getenv("HF_TOKEN")

print(f"--- AI DIAGNOSTIC START ---")
print(f"Configured Key: {api_key[:10]}... (Total length: {len(api_key) if api_key else 0})")

# 2. Test Connection
try:
    if not api_key or "your_" in api_key:
        print("❌ ERROR: No valid API key found in .env")
    else:
        client = InferenceClient(token=api_key)
        model = "meta-llama/Llama-3.2-1B-Instruct"
        
        print(f"Connecting to model: {model}...")
        
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Write 3 viral hooks for a coffee shop"}
        ]

        response = client.chat_completion(
            messages,
            max_tokens=100,
            model=model
        )
        
        print("\n✅ SUCCESS! AI RESPONSE:")
        print("-" * 30)
        print(response.choices[0].message.content.strip())
        print("-" * 30)
    
except Exception as e:
    print(f"\n❌ FAILED: {str(e)}")

print(f"\n--- AI DIAGNOSTIC END ---")
