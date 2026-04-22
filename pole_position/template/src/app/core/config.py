from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "app"
    app_env: str = "dev"
    debug: bool = True


settings = Settings()