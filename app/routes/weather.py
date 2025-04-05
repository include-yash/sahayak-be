from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from utils.weather import get_weather
from routes.auth import get_current_user

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

@router.get("/weather")
async def fetch_weather(city: str, current_user: dict = Depends(get_current_user)):
    """
    Fetch weather data for a given city. Requires authentication.
    """
    try:
        weather_data = await get_weather(city)
        return weather_data
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))