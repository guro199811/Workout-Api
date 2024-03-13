from database import Base
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, ForeignKey


# Being Populated From Seed
class Exercise_Type(Base):
    __tablename__ = "exercise_types"

    exercise_type_id = Column(Integer, primary_key=True, index=True)
    exercise_type_name = Column(String, unique=True)
    exercises = relationship("Exercise", back_populates="exercise_type")


# Being Populated From Seed
class Exercise_Unit(Base):
    __tablename__ = "exercise_units"

    unit_id = Column(Integer, primary_key=True, index=True)
    unit_1 = Column(String, nullable=False, unique=True)
    unit_2 = Column(String, nullable=True, unique=False)


# Being Populated From Seed
class Exercise(Base):
    __tablename__ = "exercises"

    exercise_id = Column(Integer, primary_key=True, index=True)
    exercise_name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    instructions = Column(String)
    target_muscles = Column(String)
    difficulty = Column(String)
    exercise_type_id = Column(Integer, ForeignKey(
        "exercise_types.exercise_type_id"))
    exercise_type = relationship("Exercise_Type", back_populates="exercises")
    unit_type_id = Column(Integer, ForeignKey("exercise_units.unit_id"))
    goal_type_id = Column(Integer, ForeignKey("goal_types.goal_type_id"))
    goal_type = relationship("Goal_Type", back_populates="exercises")
