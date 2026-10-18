from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 jours

    # Bunny (JAMAIS exposé côté client)
    BUNNY_KEY: str
    BUNNY_LIB: str

    # Admin initial
    ADMIN_EMAIL: str = "admin@dilitafi.com"
    ADMIN_PASSWORD: str = "ChangeMe123!"

    # IAP (plus tard)
    GOOGLE_SERVICE_ACCOUNT_JSON: str = ""
    APPLE_SHARED_SECRET: str = ""

    class Config:
        env_file = ".env"

settings = Settings()