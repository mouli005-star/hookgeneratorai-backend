import requests
import json

API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2"
TOKEN = "hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxx" # REPLACE WITH YOUR TOKEN or use os.getenv("HF_TOKEN")

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

payload = {
    "inputs": "Generate a viral hook for Instagram",
    "parameters": {
        "max_new_tokens": 100,
        "temperature": 0.7
    }
}

print("Testing HuggingFace API...")
print(f"URL: {API_URL}")
print(f"Token: {TOKEN[:10]}...")

try:
    response = requests.post(API_URL, headers=headers, json=payload, timeout=30)
    print(f"\nStatus Code: {response.status_code}")
    print(f"Response: {response.text[:500]}")
    
    if response.status_code == 200:
        print("\n✅ SUCCESS! Your token works!")
    elif response.status_code == 503:
        print("\n⏳ Model is loading. Wait 20 seconds and try again.")
    elif response.status_code == 401:
        print("\n❌ Token is invalid or expired.")
    elif response.status_code == 410:
        print("\n❌ Model endpoint has been deprecated or moved.")
    else:
        print(f"\n⚠️ Unexpected status: {response.status_code}")
        
except Exception as e:
    print(f"\n❌ Error: {e}")
