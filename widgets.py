from fastapi import APIRouter, Depends, HTTPException, Response, Request
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models import Widget, Tenant
from app.schemas import WidgetCreate, WidgetResponse
from app.routers.auth import get_current_tenant

router = APIRouter(tags=["Widgets"])

@router.post("/api/widgets", response_model=WidgetResponse)
def create_widget(
    widget_in: WidgetCreate,
    current_tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db)
):
    widget = Widget(**widget_in.model_dump(), tenant_id=current_tenant.id)
    db.add(widget)
    db.commit()
    db.refresh(widget)
    widget.embed_code = f'<script src="http://localhost:8000/widget.js?id={widget.id}"></script>'
    return widget

@router.get("/api/widgets", response_model=List[WidgetResponse])
def list_widgets(
    current_tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db)
):
    widgets = db.query(Widget).filter(Widget.tenant_id == current_tenant.id).all()
    for w in widgets:
        w.embed_code = f'<script src="http://localhost:8000/widget.js?id={w.id}"></script>'
    return widgets

# Fast, Cached Public Config Delivery (CDN Simulation)[cite: 1]
@router.get("/api/widgets/{widget_id}/config")
def get_widget_config(widget_id: str, response: Response, db: Session = Depends(get_db)):
    widget = db.query(Widget).filter(Widget.id == widget_id).first()
    if not widget:
        raise HTTPException(status_code=404, detail="Widget not found")
    
    # HTTP Caching Headers[cite: 1]
    response.headers["Cache-Control"] = "public, max-age=60"
    return {
        "id": widget.id,
        "title": widget.title,
        "description": widget.description,
        "widget_type": widget.widget_type,
        "button_text": widget.button_text
    }