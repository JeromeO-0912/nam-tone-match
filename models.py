import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime
from db import Base


def utcnow():
    return datetime.now(timezone.utc)


class Job(Base):
    __tablename__ = "jobs"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=False, index=True)
    status = Column(String, nullable=False, default="queued")  # queued | processing | done | failed
    di_s3_key = Column(String, nullable=True)
    reference_s3_key = Column(String, nullable=True)
    output_s3_key = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False)