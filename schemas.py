from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any
from datetime import datetime

class TenantCreate(BaseModel):
    email: EmailStr
    password: str

class TenantResponse(BaseModel):
    id: str
    email: EmailStr

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class WidgetCreate(BaseModel):
    name: str
    widget_type: Optional[str] = "signup"
    title: str
    description: Optional[str] = None
    button_text: Optional[str] = "Submit"

class WidgetResponse(WidgetCreate):
    id: str
    tenant_id: str
    created_at: datetime
    embed_code: Optional[str] = None

    class Config:
        from_attributes = True

class SubmissionCreate(BaseModel):
    widget_id: str
    data: Dict[str, Any]
    hp_field: Optional[str] = None # Honeypot field for bot detection

class SubmissionResponse(BaseModel):
    id: str
    widget_id: str
    data: Dict[str, Any]
    country: Optional[str]
    city: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True