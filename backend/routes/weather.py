from typing import List
from fastapi import APIRouter, HTTPException, status
from database import get_db_cursor
from schemas.weather import WeatherCreate, WeatherResponse

router = APIRouter(prefix="/weather", tags=["Weather"])


@router.get("", response_model=List[WeatherResponse])
def get_weather():
    """Retrieve weather observations."""
    try:
        with get_db_cursor() as cursor:
            cursor.execute("""
                SELECT
                    weather_id,
                    location,
                    temperature,
                    humidity,
                    rainfall,
                    weather_date
                FROM weather_data
                ORDER BY weather_date DESC
            """)
            rows = cursor.fetchall()
            return [
                {
                    "weather_id": r[0],
                    "location": r[1],
                    "temperature": float(r[2]) if r[2] is not None else 0.0,
                    "humidity": float(r[3]) if r[3] is not None else 0.0,
                    "rainfall": float(r[4]) if r[4] is not None else 0.0,
                    "weather_date": str(r[5])
                }
                for r in rows
            ]
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unable to load weather data: {str(error)}"
        )


@router.post("", response_model=WeatherResponse, status_code=status.HTTP_201_CREATED)
def record_weather(weather: WeatherCreate):
    """Record an environmental/weather observation."""
    try:
        with get_db_cursor(commit=True) as cursor:
            cursor.execute("""
                INSERT INTO weather_data (
                    location,
                    temperature,
                    humidity,
                    rainfall,
                    weather_date
                )
                VALUES (
                    %s,
                    %s,
                    %s,
                    %s,
                    COALESCE(%s, CURRENT_DATE)
                )
                RETURNING
                    weather_id,
                    location,
                    temperature,
                    humidity,
                    rainfall,
                    weather_date
            """, (
                weather.location,
                weather.temperature,
                weather.humidity,
                weather.rainfall,
                weather.weather_date
            ))
            row = cursor.fetchone()
            return {
                "weather_id": row[0],
                "location": row[1],
                "temperature": float(row[2]),
                "humidity": float(row[3]),
                "rainfall": float(row[4]),
                "weather_date": str(row[5])
            }
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unable to record weather data: {str(error)}"
        )
