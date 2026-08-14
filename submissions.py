from fastapi import APIRouter, Depends, HTTPException, Request, BackgroundTasks, status
from sqlalchemy.orm import Session
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.database import get_db
from app.models import Widget, Submission
from app.schemas import SubmissionCreate, SubmissionResponse
from app.services import enrich_ip_location, trigger_safe_side_effects

limiter = Limiter(key_func=get_remote_address)
router = APIRouter(prefix="/api/submissions", tags=["Submissions"])

@router.post("", response_model=SubmissionResponse)
@limiter.limit("10/minute") # Rate Limiting Protection[cite: 1]
async def submit_lead(
    request: Request,
    payload: SubmissionCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    # 1. Spam Defense (Honeypot Check)[cite: 1]
    if payload.hp_field:
        # Silently drop spam submission[cite: 1]
        raise HTTPException(status_code= status.HTTP_200_OK, detail={"status": "success", "message": "Processed"})

    # 2. Boundary Validation[cite: 1]
    widget = db.query(Widget).filter(Widget.id == payload.widget_id).first()
    if not widget:
        raise HTTPException(status_code=404, detail="Widget not found")

    client_ip = request.client.host if request.client else "127.0.0.1"

    # 3. Geo Enrichment Fallback Chain[cite: 1]
    geo_data = await enrich_ip_location(client_ip)

    # 4. Storage[cite: 1]
    submission = Submission(
        widget_id=widget.id,
        tenant_id=widget.tenant_id,
        data=payload.data,
        ip_address=client_ip,
        country=geo_data.get("country"),
        city=geo_data.get("city")
    )
    db.add(submission)
    db.commit()
    db.refresh(submission)

    # 5. Non-blocking safe side effect trigger[cite: 1]
    email = payload.data.get("email", "user@example.com")
    background_tasks.add_task(trigger_safe_side_effects, submission.id, email)

    return submission