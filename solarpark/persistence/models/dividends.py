from sqlalchemy import Boolean, Column, DateTime, Float, Integer, func

from solarpark.persistence.database import Base


class Dividend(Base):
    __tablename__ = "dividends"

    id = Column(Integer, primary_key=True, index=True, autoincrement="auto")
    dividend_per_share = Column(Float, nullable=False)
    payment_year = Column(Integer, nullable=False, unique=True)
    completed = Column(Boolean, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
