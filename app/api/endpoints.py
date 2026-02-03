from fastapi import APIRouter, HTTPException, Header
from app.models.schemas import GenerateRequest, GenerateResponse, HistoryResponse
from app.services.ai_service import AIService
from app.services.firebase_service import FirebaseService
from typing import Optional
import traceback

router = APIRouter()
ai_service = AIService()
firebase_service = FirebaseService()

@router.post("/generate", response_model=GenerateResponse)
async def generate_content(request: GenerateRequest, x_fb_token: Optional[str] = Header(None)):
    print(f"🚀 DEBUG: Received generation request: {request.prompt[:20]}...")
    try:
        # 1. Verify Token
        if not x_fb_token:
            uid = "dev_user"
        else:
            user_info = await firebase_service.verify_token(x_fb_token)
            if not user_info:
                raise HTTPException(status_code=401, detail="Invalid Firebase token")
            uid = user_info['uid']

        # 2. Generate Content
        print(f"   - Calling AI service for {uid}...")
        result = await ai_service.generate(request.prompt, request.type)
        print(f"   - AI success! Result: {result[:20]}...")
        
        # 3. Save History
        try:
            print(f"   - Saving history for {uid}...")
            firebase_service.save_history(
                uid, 
                request.prompt, 
                result, 
                request.type,
                platform=request.platform,
                tone=request.tone
            )
        except Exception as fire_err:
            print(f"⚠️ History save failed (ignoring): {fire_err}")
        
        return GenerateResponse(content=result)
        
    except Exception as e:
        print(f"❌ ERROR: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history", response_model=HistoryResponse)
async def get_history(x_fb_token: Optional[str] = Header(None)):
    if not x_fb_token:
        uid = "dev_user"
    else:
        user_info = await firebase_service.verify_token(x_fb_token)
        if not user_info:
            raise HTTPException(status_code=401, detail="Invalid Firebase token")
        uid = user_info['uid']

    try:
        history_list = firebase_service.get_history(uid)
        return HistoryResponse(history=history_list)
    except Exception as e:
        print(f"❌ ERROR fetching history: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))
