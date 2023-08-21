import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from solarpark.authentication import api_security
from solarpark.logging import log_config
from solarpark.persistence.database import Base, engine
from solarpark.settings import settings
from solarpark.setup import add_routes

log_config.configure_logging()

Base.metadata.create_all(bind=engine)

app = FastAPI(title="solarpark-service", description="Solar Park", root_path=settings.ROOT_PATH)

add_routes(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOW_ORIGINS.split(";"),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/healthz")
def healthcheck():
    return {"status": "OK"}


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    log_config.clear_thread_logging_state()
    return await call_next(request)


if __name__ == "__main__":
    # Override security when run locally, this will not run when deployed.
    def fake_auth():
        pass

    app.dependency_overrides[api_security] = fake_auth

    uvicorn.run(app)
