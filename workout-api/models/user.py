from database import Base
from sqlalchemy.orm import relationship
from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    DateTime
)

from datetime import datetime


class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    fullname = Column(String)
    hashed_password = Column(String, nullable=False)
    weight = Column(Integer)
    height = Column(Integer)


class User_History(Base):
    __tablename__ = "user_history"

    history_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    created = Column(DateTime, default=datetime.utcnow)
    fullname_change = Column(String, nullable=True)
    weight_change = Column(Integer, nullable=True)
    height_change = Column(Integer, nullable=True)
    bmi_calculation = Column(Integer, nullable=True)
