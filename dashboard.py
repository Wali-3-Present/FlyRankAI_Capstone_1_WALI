from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List

from app.database import get_db
from app.models import Tenant, Submission, Widget
from app.schemas import SubmissionResponse
from app.routers.auth import get_current_tenant

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])

@router.get("/stats")
def get_dashboard_stats(
    current_tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db)
):
    total_widgets = db.query(Widget).filter(Widget.tenant_id == current_tenant.id).count()
    total_submissions = db.query(Submission).filter(Submission.tenant_id == current_tenant.id).count()
    
    geo_breakdown = (
        db.query(Submission.country, func.count(Submission.id))
        .filter(Submission.tenant_id == current_tenant.id)
        .group_by(Submission.country)
        .all()
    )

    return {
        "total_widgets": total_widgets,
        "total_submissions": total_submissions,
        "geo_breakdown": {country: count for country, count in geo_breakdown}
    }

@router.get("/submissions", response_model=List[SubmissionResponse])
def get_tenant_submissions(
    current_tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db)
):
    # Multi-tenant isolation verified[cite: 1]
    return db.query(Submission).filter(Submission.tenant_id == current_tenant.id).all()