# read our environment Variables

from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
)


class Settings(BaseSettings):
    """DataBase Url only loaded as we use extra="ignore" """

    DATABASE_URL: str
    JWT_SECRET: str
    JWT_ALGORITHM: str

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


Config = Settings()
