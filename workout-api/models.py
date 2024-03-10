from database import Base
from sqlalchemy import (
    Column, 
    Integer, 
    String,
    Boolean,
    ForeignKey,
    DateTime,
    ARRAY
)

from datetime import datetime



class User(Base):
    __tablename__ = 'users'

    user_id= Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    fullname = Column(String)
    hashed_password = Column(String, nullable=False)
    weight = Column(Integer)
    weight_unit = Column(String)
    height = Column(Integer)
    height_unit = Column(Integer)


# Being Populated From Seed
class Exercise_Type(Base):
    __tablename__ = 'exercise_types'
    
    exercise_type_id = Column(Integer, primary_key=True, index=True)
    exercise_type_name = Column(String, unique=True)
    exercises_array = Column(ARRAY)


# Being Populated From Seed
class Exercise(Base):
    __tablename__ = 'exercises'

    exercise_id = Column(Integer, primary_key=True, index=True)
    exercise_name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    instructions = Column(String)
    target_muscles = Column(String)
    difficulty = Column(String)
    


class Exercise_Unit_Type(Base):
    __tablename__ = 'exercise_unit_types'

    unit_type_id = Column(Integer, primary_key=True, index=True)
    exercises_array = Column(ARRAY)
    unit_1 = Column(String, nullable=False, unique=True)
    unit_2 = Column(String, nullable=True, unique=False)


class Goal(Base):
    __tablename__ = 'goals'
    
    goal_id = Column(Integer, primary_key=True, index=True)
    goal_name = Column(String)
    user_id = Column(Integer, ForeignKey('users.id'))
    created_time = Column(DateTime, default=datetime.utcnow)
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
    range_min = Column(Integer)
    range_max = Column(Integer)
    selected_exercises = Column(ARRAY)


# Predefined
class Goal_Type(Base):
    __tablename__ = 'goal_types'

    goal_type_id = Column(Integer, primary_key=True, index=True)
    goal_target = Column(String, unique=True)
    target_specific_exercises = Column(ARRAY)
    

class Schedule(Base):
    __tablename__ = "schedules"

    schedule_id = Column(Integer, primary_key=True, index=True)
    goal_id = Column(Integer, ForeignKey('goals.goal_id') ,nullable=True)
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
    selected_exercises = Column(ARRAY, nullable=True)
    note = Column(String, default= "")
    extended_note = Column(String, default="")
    crontab_value = Column(String, default="")


class User_History(Base):
    __tablename__ = "user_history"

    user_id = Column(Integer, ForeignKey('users.user_id'))
    created = Column(DateTime, default=datetime.utcnow)
    weight_change = Column(Integer, nullable=True)
    height_change = Column(Integer, nullable=True)
    bmi_calculation = Column(Integer, nullable=True)
    goal_id = Column(Integer, ForeignKey('goals.goal_id'), nullable=True)
    schedule_id = Column(Integer, ForeignKey('schedules.schedule_id'), nullable=True)
