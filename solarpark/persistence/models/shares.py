from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String, func
from sqlalchemy.orm import relationship

from solarpark.persistence.database import Base
from solarpark.persistence.members import Member


class Share(Base):
    __tablename__ = "shares"

    id = Column(Integer, primary_key=True, index=True, autoincrement="auto")
    member_id = Column(Integer, ForeignKey("members.id"), nullable=False)
    comment = Column(String, nullable=True)
    initial_value = Column(Float, nullable=False)
    current_value = Column(Float, nullable=False)
    purchased_at = Column(DateTime, nullable=False)
    from_internal_account = Column(Boolean, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    members = relationship(Member)
