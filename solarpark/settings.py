from pydantic import BaseSettings


class Settings(BaseSettings):
    ROOT_PATH: str = ""
    CONNECTIONSTRING_DB: str


settings = Settings()
