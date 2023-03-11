import uvicorn
from fastapi import FastAPI, Request

from solarpark.logging import log_config
from solarpark.persistence.database import Base, engine
from solarpark.settings import settings
from solarpark.setup import add_routes

log_config.configure_logging()

Base.metadata.create_all(bind=engine)

app = FastAPI(title="solarpark-service", description="Solar Park", root_path=settings.ROOT_PATH)

add_routes(app)


@app.get("/healthz")
def healthcheck():
    return {"status": "OK"}


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    log_config.clear_thread_logging_state()
    return await call_next(request)


if __name__ == "__main__":
    uvicorn.run(app)
