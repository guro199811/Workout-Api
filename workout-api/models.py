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

    id= Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    fullname = Column(String)
    mail = Column(String, unique=True, nullable=False)
    phone = Column(String) # String- it allows for Prefixes
    hashed_password = Column(String, nullable=False)


# Being Populated From Seed
class Exercise_Unit(Base):
    __tablename__ = 'exercise_units'

    unit_id = Column(Integer, primary_key=True, index=True)
    unit_type = Column(String, unique=True)


# Being Populated From Seed
class Exercise_Type(Base):
    __tablename__ = 'exercise_types'
    
    type_id = Column(Integer, primary_key=True, index=True)
    workout_type = Column(String, unique=True)


# Being Populated From Seed
class Exercise(Base):
    __tablename__ = 'exercises'

    exercise_id = Column(Integer, primary_key=True, index=True)
    exercise_name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    instructions = Column(String)
    target_muscles = Column(String)
    calories_per_minute = Column(Integer)
    difficulty = Column(String)
    type_id = Column(Integer, ForeignKey('exercise_types.type_id'), nullable=False)
    unit_id = Column(Integer, ForeignKey('exercise_units.unit_id'), nullable=False)


class Weight_Tracker(Base):
    __tablename__ = 'weight_tracker'

    tracker_id = Column(Integer, primary_key=True, index=True)
    person_id = Column(Integer, ForeignKey('users.id'))
    weight = Column(Integer)
    weight_recorded = Column(DateTime, default=datetime.utcnow)


class Workout_Tracker(Base):
    __tablename__ = 'workout_tracker'

    workout_id = Column(Integer, primary_key=True, index=True)
    person_id = Column(Integer, ForeignKey('users.id'))
    exercises = Column(String) # This Needs To Be array, if i forget to change it back
    comment = Column(String)
    due_time = Column(DateTime, nullable=True)


class Goal_Tracker(Base):
    __tablename__ = 'goal_tracker'
    
    goal_id = Column(Integer, primary_key=True, index=True)
    person_id = Column(Integer, ForeignKey('users.id'))
    created_time = Column(DateTime, default=datetime.utcnow)
    goal_description = Column(String)
    due_time = Column(DateTime, nullable=True)