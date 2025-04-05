from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from utils.schemes import get_senior_citizen_schemes
from routes.auth import get_current_user

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

@router.get("/schemes")
async def fetch_schemes(current_user: dict = Depends(get_current_user)):
    """
    Fetch government schemes for senior citizens with summaries. Requires authentication.
    """
    try:
        schemes = await get_senior_citizen_schemes()
        return {"schemes": schemes}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))