from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from solarpark.persistence.database import Base
from solarpark.persistence.members import Member


class Share(Base):
    __tablename__ = "shares"

    id = Column(Integer, primary_key=True, index=True, autoincrement="auto")
    member_id = Column(Integer, ForeignKey("members.id"), nullable=False)
    date = Column(Integer, nullable=False)
    comment = Column(String, nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    # Relationships
    members = relationship(Member)
