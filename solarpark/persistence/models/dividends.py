from sqlalchemy import Boolean, Column, DateTime, Float, Integer

from solarpark.persistence.database import Base, utcnow


class Dividend(Base):
    __tablename__ = "dividends"

    id = Column(Integer, primary_key=True, index=True, autoincrement="auto")
    dividend_per_share = Column(Float, nullable=False)
    payment_year = Column(Integer, nullable=False)
    completed = Column(Boolean, nullable=False)
    created_at = Column(DateTime, server_default=utcnow())
    updated_at = Column(DateTime, onupdate=utcnow())
