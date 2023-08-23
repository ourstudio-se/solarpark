from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer
from sqlalchemy.orm import relationship

from solarpark.persistence.database import Base, utcnow
from solarpark.persistence.models.members import Member


class Economics(Base):
    __tablename__ = "economics"

    id = Column(Integer, primary_key=True, index=True, autoincrement="auto")
    member_id = Column(Integer, ForeignKey("members.id"), nullable=False)
    nr_of_shares = Column(Integer, nullable=True)
    total_investment = Column(Float, nullable=True)
    current_value = Column(Float, nullable=True)
    reinvested = Column(Float, nullable=True)
    account_balance = Column(Float, nullable=True)
    pay_out = Column(Boolean, default=False)
    disbursed = Column(Float, nullable=True)
    created_at = Column(DateTime, server_default=utcnow())
    updated_at = Column(DateTime, onupdate=utcnow())

    # Relationships
    members = relationship(Member)
