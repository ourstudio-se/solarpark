from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from solarpark.persistence.database import Base
from solarpark.persistence.models.members import Member


class MemberEconomics(Base):
    __tablename__ = "economics_members"

    id = Column(Integer, primary_key=True, index=True, autoincrement="auto")
    member_id = Column(Integer, ForeignKey("members.id"), nullable=False)
    nr_of_shares = Column(Integer, nullable=True)
    total_investment = Column(Integer, nullable=True)
    current_value = Column(Integer, nullable=True)
    reinvested = Column(Integer, nullable=True)
    account_balance = Column(Integer, nullable=True)
    pay_out = Column(Boolean, default=False)
    disbursed = Column(Integer, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    # Relationships
    members = relationship(Member)


class Dividend(Base):
    __tablename__ = "dividend"

    id = Column(Integer, primary_key=True, index=True, autoincrement="auto")
    dividend_per_share = Column(Integer, nullable=True)
    payment_year = Column(Integer, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())


class Payment(Base):
    __tablename__ = "Payment"

    id = Column(Integer, primary_key=True, index=True, autoincrement="auto")
    member_id = Column(Integer, ForeignKey("members.id"), nullable=False)
    year = Column(Integer, nullable=True)
    amount = Column(Integer, nullable=True)
    paid_out = Column(Boolean, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    # Relationships
    members = relationship(Member)
