from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Tenant, User
from app.db.session import get_db
from app.schemas import LoginRequest, TokenResponse
from app.security import create_access_token, password_hash

router = APIRouter(prefix="/api/auth", tags=["authentication"])


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    user = db.scalar(select(User).where(User.email == payload.email, User.is_active.is_(True)))
    if user is None or not password_hash.verify(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    tenant = db.get(Tenant, user.tenant_id)
    return TokenResponse(access_token=create_access_token(user), role=user.role, tenant=tenant.slug)
