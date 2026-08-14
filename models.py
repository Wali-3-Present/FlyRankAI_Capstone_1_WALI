import uuid
import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from app.database import Base

class Tenant(Base):
    __tablename__ = "tenants"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    widgets = relationship("Widget", back_populates="tenant", cascade="all, delete-orphan")

class Widget(Base):
    __tablename__ = "widgets"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String, ForeignKey("tenants.id"), nullable=False, index=True)
    name = Column(String, nullable=False)
    widget_type = Column(String, default="signup") # signup, cta, popover
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    button_text = Column(String, default="Submit")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    tenant = relationship("Tenant", back_populates="widgets")
    submissions = relationship("Submission", back_populates="widget", cascade="all, delete-orphan")

class Submission(Base):
    __tablename__ = "submissions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    widget_id = Column(String, ForeignKey("widgets.id"), nullable=False, index=True)
    tenant_id = Column(String, ForeignKey("tenants.id"), nullable=False, index=True)
    data = Column(JSON, nullable=False)
    ip_address = Column(String, nullable=True)
    country = Column(String, nullable=True, default="Unknown")
    city = Column(String, nullable=True, default="Unknown")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    widget = relationship("Widget", back_populates="submissions")