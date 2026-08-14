from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import JWTError, jwt
import datetime

from app.database import get_db
from app.models import Tenant
from app.schemas import TenantCreate, TenantResponse, Token
from app.config import settings

router = APIRouter(prefix="/api/auth", tags=["Auth"])
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

def create_access_token(data: dict):
    to_encode = data.copy()
    to_encode.update({"exp": datetime.datetime.utcnow() + datetime.timedelta(hours=24)})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")

def get_current_tenant(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> Tenant:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        tenant_id: str = payload.get("sub")
        if tenant_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
        
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if tenant is None:
        raise credentials_exception
    return tenant

@router.post("/register", response_model=TenantResponse)
def register(tenant_in: TenantCreate, db: Session = Depends(get_db)):
    db_tenant = db.query(Tenant).filter(Tenant.email == tenant_in.email).first()
    if db_tenant:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_pwd = pwd_context.hash(tenant_in.password)
    tenant = Tenant(email=tenant_in.email, hashed_password=hashed_pwd)
    db.add(tenant)
    db.commit()
    db.refresh(tenant)
    return tenant

@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    tenant = db.query(Tenant).filter(Tenant.email == form_data.username).first()
    if not tenant or not pwd_context.verify(form_data.password, tenant.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    
    access_token = create_access_token(data={"sub": tenant.id})
    return {"access_token": access_token, "token_type": "bearer"}