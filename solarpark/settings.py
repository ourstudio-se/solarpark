from pydantic import BaseSettings


class Settings(BaseSettings):
    ROOT_PATH: str = ""
    CONNECTIONSTRING_DB: str
    API_KEY: str
    DOMAIN: str = "solarpark.eu.auth0.com"
    API_AUDIENCE: str = "https://solarpark.authentication.com"
    ISSUER: str = "https://solarpark.eu.auth0.com/"
    ALGORITHMS: str = "RS256"
    SENDGRID_API_KEY: str


settings = Settings()
