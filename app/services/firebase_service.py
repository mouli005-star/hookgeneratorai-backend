import firebase_admin
from firebase_admin import credentials, auth, firestore
import os
from dotenv import load_dotenv

load_dotenv()

class FirebaseService:
    def __init__(self):
        print("🔍 DEBUG: Starting Firebase Service...")
        
        # In a real production app, we would use a service account JSON file.
        if not firebase_admin._apps:
            # 1. Check for JSON string in .env (Best for Cloud Deployment)
            sa_json = os.getenv("FIREBASE_SERVICE_ACCOUNT_JSON")
            # 2. Check for specific path in .env
            sa_path = os.getenv("FIREBASE_SERVICE_ACCOUNT_PATH")
            # 3. Check for default filename in backend root
            default_sa = os.path.join(os.getcwd(), "firebase-adminsdk.json")
            
            if sa_json:
                print("✅ DEBUG: Found service account JSON string in environment.")
                import json
                cred_dict = json.loads(sa_json)
                cred = credentials.Certificate(cred_dict)
                firebase_admin.initialize_app(cred)
            elif sa_path and os.path.exists(sa_path):
                print(f"✅ DEBUG: Found key path in .env: {sa_path}")
                cred = credentials.Certificate(sa_path)
                firebase_admin.initialize_app(cred)
            elif os.path.exists(default_sa):
                print(f"✅ DEBUG: Found key file: {default_sa}")
                cred = credentials.Certificate(default_sa)
                firebase_admin.initialize_app(cred)
            else:
                print("⚠️ DEBUG: No service account found. Using Project ID only.")
                project_id = os.getenv("FIREBASE_PROJECT_ID", "ai-content-hook-generator")
                firebase_admin.initialize_app(options={'projectId': project_id})
        
        try:
            self.db = firestore.client()
            print("💾 DEBUG: Firestore Client connected successfully.")
        except Exception as e:
            print(f"❌ DEBUG: Firebase Firestore connection failed: {e}")
            self.db = None

    async def verify_token(self, id_token: str):
        if not self.db:
            # Skip token verification if Firestore is down (for local dev)
            return {'uid': 'dev_user', 'email': 'dev@example.com'}
        try:
            decoded_token = auth.verify_id_token(id_token)
            # Sync user profile to Firestore
            self.sync_user_data(decoded_token)
            return decoded_token
        except Exception as e:
            print(f"Error verifying token: {e}")
            return None

    def sync_user_data(self, decoded_token: dict):
        if not self.db:
            return
        uid = decoded_token.get('uid')
        email = decoded_token.get('email')
        name = decoded_token.get('name')
        picture = decoded_token.get('picture')
        
        user_ref = self.db.collection('users').document(uid)
        doc = user_ref.get()
        
        user_data = {
            'email': email,
            'name': name,
            'photoURL': picture,
            'lastLogin': firestore.SERVER_TIMESTAMP
        }
        
        if not doc.exists:
            user_ref.set(user_data)
        else:
            user_ref.update(user_data)

    def save_history(self, uid: str, prompt: str, content: str, task_type: str, platform: str = None, tone: str = None):
        if not self.db:
            return
        self.db.collection('history').add({
            'uid': uid,
            'prompt': prompt,
            'content': content,
            'type': task_type,
            'platform': platform,
            'tone': tone,
            'timestamp': firestore.SERVER_TIMESTAMP
        })

    def get_history(self, uid: str, limit_count: int = 50):
        if not self.db:
            return []
        
        try:
            # We remove .order_by here to avoid 'Missing Index' errors if the user hasn't set them up.
            # We will sort manually in Python instead for maximum reliability.
            docs = self.db.collection('history') \
                .where('uid', '==', uid) \
                .limit(limit_count) \
                .stream()
            
            history = []
            for doc in docs:
                data = doc.to_dict()
                ts = data.get('timestamp')
                ts_str = ts.isoformat() if ts else None
                
                history.append({
                    "id": doc.id,
                    "prompt": data.get("prompt", ""),
                    "content": data.get("content", ""),
                    "type": data.get("type", "hook"),
                    "platform": data.get("platform"),
                    "tone": data.get("tone"),
                    "timestamp": ts_str
                })
            
            # SORT MANUALLY: Newest first
            history.sort(key=lambda x: x['timestamp'] if x['timestamp'] else "", reverse=True)
            
            return history
        except Exception as e:
            print(f"Error fetching history: {e}")
            return []
