from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from solarpark.persistence.database import Base, utcnow
from solarpark.persistence.members import Member


class Share(Base):
    __tablename__ = "shares"

    id = Column(Integer, primary_key=True, index=True, autoincrement="auto")
    member_id = Column(Integer, ForeignKey("members.id"), nullable=False)
    comment = Column(String, nullable=True)
    initial_value = Column(Float, nullable=False)
    current_value = Column(Float, nullable=False)
    purchased_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, server_default=utcnow())
    updated_at = Column(DateTime, onupdate=utcnow())

    # Relationships
    members = relationship(Member)
