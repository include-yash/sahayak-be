from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from utils.gemini import get_gemini_response
from routes.auth import get_current_user

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# Define request model
class GeminiRequest(BaseModel):
    prompt: str

@router.post("/gemini")
async def query_gemini(request: GeminiRequest, current_user: dict = Depends(get_current_user)):
    """
    Send a prompt to Gemini and return the response. Requires authentication.
    """
    try:
        response = await get_gemini_response(request.prompt)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))