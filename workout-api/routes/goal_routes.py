from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette import status
from database import SessionLocal
import logging

from .auth import get_current_user
from form_models import GoalRequestModel
from models import (
    User,
    Goal,
    Goal_Type,
    Exercise,
    Exercise_Unit,
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]

# user_dependency will act as login_required
user_dependency = Annotated[dict, Depends(get_current_user)]


# Section For Goals Routes, For Getting, Posting, Editing and Deleting
goal = APIRouter(prefix="/goal", tags=["goals"])


# Querries all Goal types
@goal.get("/all_goal_types/",
          description="This endpoint returns all available goal_types.")
def all_goal_types(db: db_dependency):
    goal_types = db.query(Goal_Type).all()
    if not goal_types:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND, detail="Goal Types are not populated."
        )
    return {"goal_types": goal_types}


@goal.post("/create_goal/", description="This endpoint is for goal creation")
def create_goal(user: user_dependency, db: db_dependency,
                goal: GoalRequestModel):
    # Getting current user
    user = db.query(User).filter(User.user_id == user["id"]).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    # Checking for goaltypes existance
    goal_type = (
        db.query(Goal_Type).filter(
            Goal_Type.goal_type_id == goal.goal_type_id).first()
    )
    if not goal_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Goal type not found in create_goal form",
        )

    new_goal = Goal(
        goal_name=goal.goal_name,
        user_id=user.user_id,
        start_date=goal.start_date,
        end_date=goal.end_date,
        range_min=goal.range_min,
        range_max=goal.range_max,
        selected_exercises=goal.selected_exercises,
        completed=goal.completed,
        goal_type_id=goal.goal_type_id,
    )
    try:
        db.add(new_goal)
        db.commit()
        db.refresh(new_goal)
        return {"Request Succesfull": "Goal entry added"}
    except Exception as e:
        logging.error(f"Exception Raised at create_goal(post) function: {e}")
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR)


# get user goals
@goal.get("/personal_goals/",
          description="This endpoint returns user related goals.")
def get_personal_goals(user: user_dependency, db: db_dependency):
    user_goals = (
        db.query(Goal)
        .join(Goal_Type)
        .filter(Goal.user_id == user["id"])
        .order_by(Goal.start_date.asc(), Goal.created_time.asc())
        .all()
    )
    if not user_goals:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            detail="Goals not found on this specific user"
        )

    user_goals_dict = []
    for goal in user_goals:
        # Query of the exercises "related" to the goal using in_ operator
        selected_exercises = (
            db.query(Exercise)
            .filter(Exercise.exercise_id.in_(goal.selected_exercises))
            .all()
        )

        # Goal type target relationship to get a goal type name
        goal_type_target = goal.goal_type.goal_target

        # Converting the exercises to a list of dictionaries
        selected_exercises_dict = []
        for exercise in selected_exercises:
            # Query the exercise unit related to the exercise
            exercise_unit = (
                db.query(Exercise_Unit)
                .filter(Exercise_Unit.unit_id == exercise.unit_type_id)
                .first()
            )

            selected_exercises_dict.append(
                dict(
                    exercise_id=exercise.exercise_id,
                    exercise_name=exercise.exercise_name,
                    description=exercise.description,
                    instructions=exercise.instructions,
                    target_muscles=exercise.target_muscles,
                    difficulty=exercise.difficulty,
                    exercise_type_id=exercise.exercise_type_id,
                    unit_type_id=exercise.unit_type_id,
                    unit_1=exercise_unit.unit_1,
                    unit_2=exercise_unit.unit_2,
                    goal_type_id=exercise.goal_type_id,
                )
            )

        user_goals_dict.append(
            dict(
                goal_id=goal.goal_id,
                goal_name=goal.goal_name,
                user_id=goal.user_id,
                created_time=goal.created_time,
                start_date=goal.start_date,
                end_date=goal.end_date,
                range_min=goal.range_min,
                range_max=goal.range_max,
                selected_exercises=selected_exercises_dict,
                completed=goal.completed,
                goal_type_id=goal.goal_type_id,
                goal_target=goal_type_target,
            )
        )

    return {"user_goals": user_goals_dict}


# Editability forr personal goals
@goal.put("/personal_goals/{goal_id}",
          description="This endpoint edits user related goal.")
def edit_personal_goal(
    user: user_dependency, goal: GoalRequestModel, goal_id: int,
    db: db_dependency
):
    # Querying Goal with user_id and specified goal_id
    db_goal = (
        db.query(Goal)
        .filter(Goal.user_id == user["id"], Goal.goal_id == goal_id)
        .first()
    )
    if not db_goal:
        raise HTTPException(status_code=404, detail="Goal not found")

    # Checking for goal_type
    if goal.goal_type_id is not None:
        goal_type = (
            db.query(Goal_Type)
            .filter(Goal_Type.goal_type_id == goal.goal_type_id)
            .first()
        )
        if not goal_type:
            raise HTTPException(status_code=404,
                                detail="Specific Goal type not found")
        db_goal.goal_type_id = goal_type.goal_type_id

    changes = goal.dict()  # Request model can be dictionarized

    # Iterate over the changes and update the goal data
    for key, value in changes.items():
        if value is not None and getattr(db_goal, key) != value:
            setattr(db_goal, key, value)

    try:
        db.commit()
        db.refresh(db_goal)
        return db_goal
    except Exception as e:
        logging.error(
            f"Exception Raised at edit_personal_goal(put) function: {e}")
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR)


# Deletability for personal goals
@goal.delete("/personal_goals/{goal_id}",
             description="This endpoint deletes user related goal.")
def delete_personal_goal(user: user_dependency, goal_id: int,
                         db: db_dependency):
    db_goal = (
        db.query(Goal)
        .filter(Goal.user_id == user["id"], Goal.goal_id == goal_id)
        .first()
    )
    if not db_goal:
        raise HTTPException(status_code=404, detail="Goal not found")

    try:
        db.delete(db_goal)
        db.commit()
        return {"message": "Goal successfully deleted"}
    except Exception as e:
        logging.error(f"Exception Raised at delete goal function: {e}")
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR)
