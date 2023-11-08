from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer
from sqlalchemy.orm import relationship

from solarpark.persistence.database import Base, utcnow
from solarpark.persistence.models.members import Member


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True, autoincrement="auto")
    member_id = Column(Integer, ForeignKey("members.id"), nullable=False)
    year = Column(Integer, nullable=True)
    amount = Column(Float, nullable=True)
    paid_out = Column(Boolean, nullable=True)
    created_at = Column(DateTime, server_default=utcnow())
    updated_at = Column(DateTime, onupdate=utcnow())

    # Relationships
    members = relationship(Member)
