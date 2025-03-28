import os
from dotenv import load_dotenv

load_dotenv()  # Loads variables from a .env file if available


class Settings:
    DB_USER: str = os.getenv("DB_USER", "your_db_user")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "your_db_password")
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: str = os.getenv("DB_PORT", "5432")
    DB_NAME: str = os.getenv("DB_NAME", "your_db_name")

    @property
    def SQLALCHEMY_DATABASE_URI(self):
        return (
            f"postgresql+psycopg2://{self.DB_USER}:{self.DB_PASSWORD}@"
            f"{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )


settings = Settings()
