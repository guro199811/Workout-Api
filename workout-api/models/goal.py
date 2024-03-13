from database import Base
from sqlalchemy.orm import relationship
from sqlalchemy import (
    Column, Integer, String,
    Boolean, ForeignKey, DateTime, ARRAY)

from datetime import datetime


class Goal(Base):
    __tablename__ = "goals"

    goal_id = Column(Integer, primary_key=True, index=True)
    goal_name = Column(String)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    created_time = Column(DateTime, default=datetime.utcnow)
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
    range_min = Column(Integer)
    range_max = Column(Integer)
    selected_exercises = Column(ARRAY(Integer))
    completed = Column(Boolean, default=False)
    goal_type_id = Column(Integer, ForeignKey("goal_types.goal_type_id"))
    goal_type = relationship("Goal_Type", back_populates="goal")
    schedule = relationship("Schedule", back_populates="goal")


# PBeing Populated From Seed
class Goal_Type(Base):
    __tablename__ = "goal_types"

    goal_type_id = Column(Integer, primary_key=True, index=True)
    goal_target = Column(String, unique=True)
    exercises = relationship("Exercise", back_populates="goal_type")
    goal = relationship("Goal", back_populates="goal_type")
