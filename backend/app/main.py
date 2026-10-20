import asyncio
from contextlib import asynccontextmanager, suppress

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.health import router as health_router
from app.api.ingest import router as ingest_router
from app.api.auth import router as auth_router
from app.api.logs import router as logs_router
from app.api.dashboard import router as dashboard_router
from app.api.alerts import router as alerts_router
from app.api.admin import router as admin_router
from app.config import settings
from app.db.session import SessionLocal
from app.services.bootstrap import bootstrap_demo_data
from app.services.retention import delete_expired_logs


@asynccontextmanager
async def lifespan(_: FastAPI):
    db = SessionLocal()
    try:
        bootstrap_demo_data(db)
        delete_expired_logs(db, settings.retention_days)
    finally:
        db.close()
    async def retention_loop():
        while True:
            await asyncio.sleep(settings.retention_check_interval_seconds)
            session = SessionLocal()
            try: delete_expired_logs(session, settings.retention_days)
            finally: session.close()
    task = asyncio.create_task(retention_loop())
    try:
        yield
    finally:
        task.cancel()
        with suppress(asyncio.CancelledError): await task


app = FastAPI(title="LogSight API", version="0.1.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=settings.cors_origins, allow_credentials=False, allow_methods=["*"], allow_headers=["*"])
app.include_router(health_router)
app.include_router(ingest_router)
app.include_router(auth_router)
app.include_router(logs_router)
app.include_router(dashboard_router)
app.include_router(alerts_router)
app.include_router(admin_router)
