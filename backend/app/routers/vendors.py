
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from sqlalchemy import or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User, Vendor
from app.services.session import get_current_user

router = APIRouter(prefix="/vendors", tags=["Vendors"])


def require_roles(*roles: str):
    def check_role(
        current_user: User = Depends(get_current_user),
    ) -> User:
        if current_user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )
        return current_user

    return check_role


class VendorCreate(BaseModel):
    vendor_name: str = Field(min_length=2, max_length=180)
    category: str = Field(min_length=2, max_length=100)
    contact_name: str = Field(min_length=2, max_length=120)
    contact_email: EmailStr
    contact_phone: str = Field(min_length=5, max_length=20)
    gstin: str | None = None
    pan: str | None = None
    address: str | None = None


class VendorUpdate(BaseModel):
    vendor_name: str | None = Field(default=None, min_length=2, max_length=180)
    category: str | None = Field(default=None, min_length=2, max_length=100)
    contact_name: str | None = Field(default=None, min_length=2, max_length=120)
    contact_email: EmailStr | None = None
    contact_phone: str | None = Field(default=None, min_length=5, max_length=20)
    gstin: str | None = None
    pan: str | None = None
    address: str | None = None


class VendorStatusUpdate(BaseModel):
    status: Literal["pending", "approved", "rejected"]


class VendorResponse(BaseModel):
    id: int
    vendor_name: str
    category: str
    gstin: str | None
    pan: str | None
    contact_name: str
    contact_email: EmailStr
    contact_phone: str
    address: str | None
    status: str

    model_config = ConfigDict(from_attributes=True)


@router.get(
    "/",
    response_model=list[VendorResponse],
    dependencies=[Depends(require_roles("admin", "procurement_officer", "manager"))],
)
def list_vendors(
    search: str | None = None,
    vendor_status: str | None = Query(default=None, alias="status"),
    db: Session = Depends(get_db),
):
    stmt = select(Vendor)

    if search and search.strip():
        term = f"%{search.strip()}%"
        stmt = stmt.where(
            or_(
                Vendor.vendor_name.ilike(term),
                Vendor.contact_name.ilike(term),
                Vendor.contact_email.ilike(term),
                Vendor.category.ilike(term),
            )
        )

    if vendor_status:
        if vendor_status not in {"pending", "approved", "rejected"}:
            raise HTTPException(422, detail="Invalid vendor status")
        stmt = stmt.where(Vendor.status == vendor_status)

    return db.scalars(stmt.order_by(Vendor.id.desc())).all()


@router.post(
    "/",
    response_model=VendorResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_roles("admin", "procurement_officer"))],
)
def create_vendor(payload: VendorCreate, db: Session = Depends(get_db)):
    data = payload.model_dump()
    for field in ("gstin", "pan", "address"):
        if isinstance(data[field], str):
            data[field] = data[field].strip() or None

    vendor = Vendor(
        **{
            **data,
            "vendor_name": payload.vendor_name.strip(),
            "category": payload.category.strip(),
            "contact_name": payload.contact_name.strip(),
            "contact_email": str(payload.contact_email).lower(),
            "contact_phone": payload.contact_phone.strip(),
        },
        status="pending",
    )
    db.add(vendor)

    try:
        db.commit()
        db.refresh(vendor)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Could not create vendor; check GSTIN uniqueness and field values",
        ) from None

    return vendor


@router.get(
    "/{vendor_id}",
    response_model=VendorResponse,
    dependencies=[Depends(require_roles("admin", "procurement_officer", "manager"))],
)
def get_vendor(vendor_id: int, db: Session = Depends(get_db)):
    vendor = db.get(Vendor, vendor_id)
    if not vendor:
        raise HTTPException(404, detail="Vendor not found")
    return vendor


@router.put(
    "/{vendor_id}",
    response_model=VendorResponse,
    dependencies=[Depends(require_roles("admin", "procurement_officer"))],
)
def update_vendor(
    vendor_id: int,
    payload: VendorUpdate,
    db: Session = Depends(get_db),
):
    vendor = db.get(Vendor, vendor_id)
    if not vendor:
        raise HTTPException(404, detail="Vendor not found")

    data = payload.model_dump(exclude_unset=True)

    for field, value in data.items():
        if isinstance(value, str):
            value = value.strip()
            if field in {"gstin", "pan", "address"} and not value:
                value = None
        setattr(vendor, field, value)

    try:
        db.commit()
        db.refresh(vendor)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Could not update vendor; check GSTIN uniqueness and field values",
        ) from None

    return vendor


@router.patch(
    "/{vendor_id}/status",
    response_model=VendorResponse,
    dependencies=[Depends(require_roles("admin", "manager"))],
)
def update_vendor_status(
    vendor_id: int,
    payload: VendorStatusUpdate,
    db: Session = Depends(get_db),
):
    vendor = db.get(Vendor, vendor_id)
    if not vendor:
        raise HTTPException(404, detail="Vendor not found")

    vendor.status = payload.status
    db.commit()
    db.refresh(vendor)
    return vendor


@router.delete(
    "/{vendor_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_roles("admin", "procurement_officer"))],
)
def delete_vendor(vendor_id: int, db: Session = Depends(get_db)):
    vendor = db.get(Vendor, vendor_id)
    if not vendor:
        raise HTTPException(404, detail="Vendor not found")

    db.delete(vendor)
    db.commit()
    return None
