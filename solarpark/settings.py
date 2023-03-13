from pydantic import BaseSettings


class Settings(BaseSettings):
    ROOT_PATH: str = ""
    CONNECTIONSTRING_DB: str
    API_KEY: str


settings = Settings()
