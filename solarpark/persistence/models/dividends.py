from sqlalchemy import Column, DateTime, Integer
from sqlalchemy.sql import func

from solarpark.persistence.database import Base


class Dividend(Base):
    __tablename__ = "dividends"

    id = Column(Integer, primary_key=True, index=True, autoincrement="auto")
    dividend_per_share = Column(Integer, nullable=True)
    payment_year = Column(Integer, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
