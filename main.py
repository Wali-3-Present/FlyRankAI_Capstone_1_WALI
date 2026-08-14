from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.database import engine, Base
from app.routers import auth, widgets, submissions, dashboard
from app.routers.submissions import limiter

# Initialize Database Schema
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Embeddable Widget & Lead-Capture Platform",
    version="1.0.0"
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS Configuration for Cross-Origin Embeds[cite: 1]
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow any origin site to submit[cite: 1]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static File Server for CDN Bundle Delivery[cite: 1]
app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.get("/widget.js")
def get_widget_js():
    from fastapi.responses import FileResponse
    return FileResponse("app/static/widget.js", media_type="application/javascript")

@app.get("/health")
def health_check():
    return {"status": "ok"}

# Router Inclusions
app.include_router(auth.router)
app.include_router(widgets.router)
app.include_router(submissions.router)
app.include_router(dashboard.router)