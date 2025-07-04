from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    ROOT_PATH: str = ""
    CONNECTIONSTRING_DB: str
    DOMAIN: str
    API_AUDIENCE: str
    ISSUER: str
    ALGORITHMS: str = "RS256"

    LOOPIA_EMAIL_FROM: str
    LOOPIA_PASSWORD: str
    LOOPIA_SMTP_SERVER: str = "mailcluster.loopia.se"
    LOOPIA_PORT: int = 587

    SHARE_PRICE: int = 3000
    ALLOW_ORIGINS: str
    ECONOMICS_BACKGROUND_BATCH: int = 20


settings = Settings()
