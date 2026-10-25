from sqlalchemy import func, select
from app.database import get_db
from app.models import Vendor
from sqlalchemy.orm import Session
from app.routers.vendors import router as vendors_router
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

from app.routers.auth import router as auth_router

app = FastAPI(
    title="VendorBridge API",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(vendors_router)

@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/dashboard/summary", tags=["Dashboard"])
def dashboard_summary(db: Session = Depends(get_db)):
    total = db.scalar(select(func.count()).select_from(Vendor)) or 0
    pending = db.scalar(
        select(func.count()).select_from(Vendor).where(Vendor.status == "pending")
    ) or 0
    approved = db.scalar(
        select(func.count()).select_from(Vendor).where(Vendor.status == "approved")
    ) or 0

    return {
        "total_vendors": total,
        "pending_vendors": pending,
        "approved_vendors": approved,
    }