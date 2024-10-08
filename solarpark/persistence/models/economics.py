from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, func
from sqlalchemy.orm import relationship

from solarpark.persistence.database import Base
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
    last_dividend_year = Column(Integer, nullable=False)
    issued_dividend = Column(DateTime, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    members = relationship(Member)
