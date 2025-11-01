from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    jwt_secret: str
    database_url: str

    google_android_client_id: str
    google_ios_client_id: str
    google_web_client_id: str
    gemini_api_key: str

    apple_client_id: str
    apple_team_id: str
    apple_key_id: str
    apple_private_key: str
    apple_redirect_url: str

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
