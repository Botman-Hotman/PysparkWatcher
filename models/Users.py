import datetime as dt
from datetime import datetime
import uuid
from dataclasses import dataclass

from sqlalchemy import Column, String, UUID, Date, Integer, DateTime, Boolean

from core.db import Base, settings


@dataclass
class user(Base):
    __tablename__ = 'users'
    __bind_key__ = settings.dw_schema
    __table_args__ = {'schema': settings.dw_schema}

    # Surrogate key
    id: int = Column(Integer, primary_key=True)

    name: str = Column(String, nullable=False)
    email: str = Column(String, nullable=False)
    date_of_birth: dt.date = Column(Date, nullable=False)

    # SCD Type 2 columns
    effective_start_date: dt.datetime = Column(DateTime, nullable=False, default=datetime.utcnow)
    effective_end_date: dt.datetime = Column(DateTime, nullable=True)
    is_current: bool = Column(Boolean, nullable=False, default=True)

    # Optional versioning
    version_number: int = Column(Integer, nullable=False, default=1)
