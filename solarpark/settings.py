from pydantic import BaseSettings


class Settings(BaseSettings):
    ROOT_PATH: str = ""
    CONNECTIONSTRING_DB: str
    API_KEY: str
    DOMAIN: str = "solarpark.eu.auth0.com"
    API_AUDIENCE: str = "https://solarpark.authentication.com"
    ISSUER: str = "https://solarpark.eu.auth0.com/"
    ALGORITHMS: str = "RS256"
    MAIL_USERNAME: str = "simonhamberg93"
    MAIL_PASSWORD: str = "unkuwcrotytvhfbr"
    MAIL_FROM: str = "simonhamberg93@gmail.com"
    MAIL_PORT: int = 587
    MAIL_SERVER: str = "smtp.gmail.com"
    MAIL_FROM_NAME: str = "Solarpark"


settings = Settings()
