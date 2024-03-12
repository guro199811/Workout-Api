from database import Base
from sqlalchemy.orm import relationship
from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    DateTime,
    ARRAY,
)


class Schedule(Base):
    __tablename__ = "schedules"

    schedule_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    goal_id = Column(Integer, ForeignKey("goals.goal_id"), nullable=True)
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
    selected_exercises = Column(ARRAY(Integer), nullable=True)
    note = Column(String, default="")
    extended_note = Column(String, default="")
    crontab_value = Column(String, default="")
    goal = relationship("Goal", back_populates="schedule")
