import datetime
import uuid
from dataclasses import dataclass

from sqlalchemy import Column, UUID, ForeignKey, Float, Date
from sqlalchemy.orm import relationship

from core.db import Base, settings


@dataclass
class transaction(Base):
    __tablename__ = 'transactions'
    __bind_key__ = settings.dw_schema
    __table_args__ = {'schema': settings.dw_schema}

    transaction_id: uuid.UUID = Column(UUID, primary_key=True)
    user_id: uuid.UUID = Column(UUID, ForeignKey(f'{settings.dw_schema}.users.user_id'), nullable=False)
    user = relationship("users", foreign_keys=[user_id])

    amount: float = Column(Float, nullable=False)
    transaction_date: datetime.date = Column(Date, nullable=False)
