from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    ROOT_PATH: str = ""
    CONNECTIONSTRING_DB: str
    API_KEY: str
    DOMAIN: str = "solarpark.eu.auth0.com"
    API_AUDIENCE: str = "https://solarpark.authentication.com"
    ISSUER: str = "https://solarpark.eu.auth0.com/"
    ALGORITHMS: str = "RS256"
    SENDGRID_API_KEY: str
    SHARE_PRICE: int = 3000
    ALLOW_ORIGINS: str = "http://localhost:5173;https://solarpark-test-env.netlify.app"
    BATCH_SIZE: int = 20


settings = Settings()
