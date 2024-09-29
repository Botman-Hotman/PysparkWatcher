import datetime as dt
from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import Column, ForeignKey, Float, Integer, DateTime, String
from sqlalchemy.orm import relationship

from core.db import Base, settings


@dataclass
class transaction(Base):
    __tablename__ = 'transactions'
    __bind_key__ = settings.dw_schema
    __table_args__ = {'schema': settings.dw_schema}

    id: int = Column(Integer, primary_key=True)
    user_id: str = Column(String,  nullable=False)

    amount: float = Column(Float, nullable=False)
    transaction_date: dt.datetime = Column(DateTime, nullable=False)

    # CDC/SCD columns
    created_at: dt.datetime = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: dt.datetime = Column(DateTime, nullable=True)

