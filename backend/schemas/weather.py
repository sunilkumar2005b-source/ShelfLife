from datetime import date
from typing import Optional
from pydantic import BaseModel, Field


class WeatherCreate(BaseModel):
    location: str = Field(..., min_length=1, max_length=100, description="City or facility location")
    temperature: float = Field(..., description="Temperature in Celsius")
    humidity: float = Field(..., ge=0, le=100, description="Relative humidity percentage")
    rainfall: float = Field(0.0, ge=0, description="Rainfall in mm")
    weather_date: Optional[date] = Field(None, description="Date of observation. Defaults to today.")


class WeatherResponse(BaseModel):
    weather_id: int
    location: str
    temperature: float
    humidity: float
    rainfall: float
    weather_date: str

    class Config:
        from_attributes = True
