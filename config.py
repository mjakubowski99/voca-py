from re import S
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    jwt_secret: str
    database_url: str

    google_android_client_id: str 
    google_ios_client_id: str 
    google_web_client_id: str 

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()