from sqlalchemy import Boolean, Column, DateTime, Integer, String

from solarpark.persistence.database import Base, utcnow


class ErrorLog(Base):
    __tablename__ = "errors"

    id = Column(Integer, primary_key=True, index=True, autoincrement="auto")
    member_id = Column(String, nullable=True)
    share_id = Column(String, nullable=True)
    comment = Column(String, nullable=False)
    resolved = Column(Boolean, nullable=False)
    created_at = Column(DateTime, server_default=utcnow())
    updated_at = Column(DateTime, onupdate=utcnow())
