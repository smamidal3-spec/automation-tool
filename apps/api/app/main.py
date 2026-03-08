from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import init_db
from app.routers.automation import router as automation_router
from app.settings import get_settings

settings = get_settings()

app = FastAPI(title="DevOps YAML Automation API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.parse_allowed_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(automation_router, prefix="/api/v1/automation", tags=["automation"])


@app.on_event("startup")
def startup_event() -> None:
    init_db()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
