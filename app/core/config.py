import os
from pydantic import BaseSettings, AnyHttpUrl
from typing import List, Optional

class Settings(BaseSettings):
    API_V1_STR: str = "/api"
    PROJECT_NAME: str = "UT Social"
    
    # MongoDB settings
    MONGODB_URL: str = os.getenv("MONGODB_URL", "mongodb+srv://quintanarealjqr:ZzWt8qAgQ8fp6uYX@utaweb.bk93x.mongodb.net/?retryWrites=true&w=majority&appName=utaweb")
    DATABASE_NAME: str = os.getenv("DATABASE_NAME", "ut_social_db")
    
    # JWT settings
    SECRET_KEY: str = os.getenv("SECRET_KEY", "xwQm9KpBTrE8JzC3vMNs6F5LY7qX_VtG2W9yKbZAfzE")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # CORS
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []

    class Config:
        case_sensitive = True

settings = Settings()