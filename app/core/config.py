from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Multi-Modal AI Engine"
    VERSION: str = "1.0.0"
    
    SECRET_KEY: str = "your-super-secret-key-change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Database Settings (XAMPP / MySQL)
    DB_HOST: str = "localhost"
    DB_PORT: str = "3306"
    DB_USER: str = "root"
    DB_PASSWORD: str = "secretrootpass"  # Updated password
    DB_NAME: str = "ai_project_db"

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()