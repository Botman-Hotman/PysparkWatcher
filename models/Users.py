import datetime as dt
import uuid
from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import Column, String, Date, Integer, DateTime, Boolean, UUID

from core.db import Base, settings


@dataclass
class user(Base):
    __tablename__ = 'users'
    __bind_key__ = settings.dw_schema
    __table_args__ = {'schema': settings.dw_schema}

    id: int = Column(Integer, primary_key=True, autoincrement=True)

    user_id: str = Column(String, nullable=False)
    name: str = Column(String, nullable=False)
    email: str = Column(String, nullable=False)
    date_of_birth: dt.date = Column(Date, nullable=False)

    effective_start_date: dt.datetime = Column(DateTime, nullable=False, default=datetime.utcnow)
    effective_end_date: dt.datetime = Column(DateTime, nullable=True)
    is_current: bool = Column(Boolean, nullable=False, default=True)

    version_number: int = Column(Integer, nullable=False, default=1)
