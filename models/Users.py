from dataclasses import dataclass
from sqlalchemy import Column, String, UUID, Date

import uuid
import datetime

from core.db import Base, settings


@dataclass
class user(Base):
    __tablename__ = 'users'
    __bind_key__ = settings.dw_schema
    __table_args__ = {'schema': settings.dw_schema}

    user_id: uuid.UUID = Column(UUID, primary_key=True)
    name: str = Column(String, nullable=False)
    email: str = Column(String, nullable=False)
    date_of_birth: datetime.date = Column(Date, nullable=False)
