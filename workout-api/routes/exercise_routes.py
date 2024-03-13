from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import asc
from starlette import status

from database import SessionLocal
from .auth import get_current_user
from models import Exercise, Exercise_Type, Exercise_Unit, Goal_Type


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


# user_dependency will act as login_required
user_dependency = Annotated[dict, Depends(get_current_user)]


exercise = APIRouter(prefix="/exercise", tags=["exercises"])


# For Main Page, Contains Exercises for displaying on main page
@exercise.get(
    "/sorted/exercise_type",
    status_code=status.HTTP_200_OK,
    description="This endpoint returns exercises sorted by exercise type.",
)
def exercises_by_type(db: db_dependency):
    exercises = (
        db.query(Exercise)
        .join(Exercise_Type)
        .options(joinedload(Exercise.exercise_type))
        .order_by(asc(Exercise_Type.exercise_type_id))
        .all()
    )
    if not exercises:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND, detail="Exercises were not found"
        )

    return {
        "exercises": [
            dict(
                exercise_id=exercise.exercise_id,
                exercise_name=exercise.exercise_name,
                description=exercise.description,
                instructions=exercise.instructions,
                target_muscles=exercise.target_muscles,
                difficulty=exercise.difficulty,
                exercise_type_id=exercise.exercise_type_id,
                unit_type_id=exercise.unit_type_id,
                goal_type_id=exercise.goal_type_id,
                exercise_type_name=exercise.exercise_type.exercise_type_name,
            )
            for exercise in exercises
        ]
    }


@exercise.get(
    "/sorted/exercise_goal_type",
    status_code=status.HTTP_200_OK,
    description="This endpoint returns exercises sorted by goal type.",
)
def exercises_by_goal_type(db: db_dependency):
    exercises = (
        db.query(Exercise)
        .join(Goal_Type)
        .options(joinedload(Exercise.exercise_type))
        .order_by(asc(Goal_Type.goal_type_id))
        .all()
    )
    if not exercises:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND, detail="Exercises were not found"
        )

    return {
        "exercises": [
            dict(
                goal_target=exercise.goal_type.goal_target,
                exercise_id=exercise.exercise_id,
                exercise_name=exercise.exercise_name,
                description=exercise.description,
                instructions=exercise.instructions,
                target_muscles=exercise.target_muscles,
                difficulty=exercise.difficulty,
                goal_type_id=exercise.goal_type_id,
            )
            for exercise in exercises
        ]
    }


# Searches the exercise by exercise_id
@exercise.get(
    "/{exercise_id}",
    description="This endpoint returns exercises filtered by exercise_id.",
)
def get_exercise_by_id(exercise_id: int, db: db_dependency):
    exercise = db.query(Exercise).filter(
        Exercise.exercise_id == exercise_id).first()
    if not exercise:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            detail="Exercise not found by exercise_id"
        )
    return {"exercises": exercise}


# Querries all Exercise types, somethings wrong here
@exercise.get(
    "/exercise_types/",
    description="This endpoint returns all available exercise_types.",
)
def all_exercise_types(db: db_dependency):
    exercise_types = db.query(Exercise_Type).all()
    if not exercise_types:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            detail="Exercise types are not populated"
        )
    return {"exercise_types": exercise_types}


# querries all Exercise unit types
@exercise.get(
    "/exercise_units/",
    description="This endpoint returns all available exercise_units.",
)
def all_exercise_units(db: db_dependency):
    exercise_units = db.query(Exercise_Unit).all()
    if not exercise_units:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            detail="Exercise units are not populated"
        )
    return {"exercise_units": exercise_units}
