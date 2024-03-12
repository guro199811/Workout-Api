from fastapi import status, Depends, HTTPException
from database import SessionLocal
from typing import Annotated, Optional, List
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import asc, desc, or_
from models import (
    User,
    Goal,
    Goal_Type,
    Exercise,
    Exercise_Type,
    Exercise_Unit,
    Schedule,
    User_History,
)
import auth
from auth import get_current_user
from sqlalchemy.orm import joinedload
from pydantic import BaseModel
import logging
from fastapi import APIRouter, status, Depends, HTTPException


router = APIRouter(prefix="/api")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]

# user_dependency will act as login_required
user_dependency = Annotated[dict, Depends(get_current_user)]


# Request models
class GoalRequestModel(BaseModel):
    goal_name: str = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    range_min: Optional[int] = None
    range_max: Optional[int] = None
    selected_exercises: List[int] = None
    goal_type_id: int = None
    completed: Optional[bool] = None


# Request models
class ScheduleRequestModel(BaseModel):
    goal_id: Optional[int] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    selected_exercises: List[int] = None
    note: Optional[str] = None
    extended_note: Optional[str] = None
    crontab_value: Optional[str] = None


class ChangeUserDataRequest(BaseModel):
    fullname: str
    weight: Optional[int]
    height: Optional[int]


# For User Menu, Contains User Data
@router.get("/user", status_code=status.HTTP_200_OK)
def user_data(user: user_dependency, db: db_dependency):
    user_db = db.query(User).filter(User.user_id == user["id"]).first()
    if user_db is None:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED, detail="Authentification Failed"
        )
    return {
        "User": user,
        "fullname": user_db.fullname,
        "weight": user_db.weight,
        "height": user_db.height,
    }


@router.put("/user_data_change")
def change_user_data(
    user: user_dependency, db: db_dependency, user_request: ChangeUserDataRequest
):
    user = db.query(User).filter(User.user_id == user["id"]).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    # Map the fields to their corresponding changes
    changes = {
        "fullname": user_request.fullname,
        "weight": user_request.weight,
        "height": user_request.height,
    }

    # Initializing changes to None
    fullname_change = None
    weight_change = None
    height_change = None

    # Iterating over the changes and updating the user data
    for field, value in changes.items():
        if getattr(user, field) != value:
            setattr(user, field, value)
            # Update the change variables
            if field == "fullname":
                fullname_change = value
            elif field == "weight":
                weight_change = value
            elif field == "height":
                height_change = value

    # Add the changes to the User_History table
    add_history(db, user, fullname_change, weight_change, height_change)

    try:
        db.commit()
        return {"Request Successfull": "User Data has been changed"}
    except:
        db.rollback()
        raise HTTPException(status.HTTP_400_BAD_REQUEST)


# For Main Page, Contains Exercises for displaying on main page
@router.get("/exercises", status_code=status.HTTP_200_OK)
def exercises(db: db_dependency):
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


# Searches the exercise by exercise_id
@router.get("/exercises/{exercise_id}")
def get_exercise_by_id(exercise_id: int, db: db_dependency):
    exercise = db.query(Exercise).filter(Exercise.exercise_id == exercise_id).first()
    if not exercise:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Exercise not found")
    return {"exercises": exercise}


# Querries all Goal types
@router.get("/all_goal_types/")
def all_goal_types(db: db_dependency):
    goal_types = db.query(Goal_Type).all()
    if not goal_types:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND, detail="Goal Types are not populated..."
        )
    return {"goal_types": goal_types}


# Querries all Exercise types
@router.get("/all_exercise_types")
def all_exercise_types(db: db_dependency):
    exercise_types = db.query(Exercise_Type).all()
    if not exercise_types:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND, detail="Exercise types are not populated..."
        )
    return {"exercise_types": exercise_types}


# querries all Exercise unit types
@router.get("/all_exercise_units")
def all_exercise_units(db: db_dependency):
    exercise_units = db.query(Exercise_Unit).all()
    if not exercise_units:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND, detail="Exercise units are not populated..."
        )
    return {"exercise_units": exercise_units}


# Section For Goals Routes, For Getting, Posting, Editing and Deleting


@router.get("/user/create_goal/")
def get_goal_data(user: user_dependency, db: db_dependency):
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


@router.post("/user/create_goal/")
def create_goal(user: user_dependency, db: db_dependency, goal: GoalRequestModel):
    # Getting current user
    user = db.query(User).filter(User.user_id == user["id"]).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    # Checking for goaltypes existance
    goal_type = (
        db.query(Goal_Type).filter(Goal_Type.goal_type_id == goal.goal_type_id).first()
    )
    if not goal_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Goal type not found"
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
    except:
        raise HTTPException(status.HTTP_400_BAD_REQUEST)


# get user goals
@router.get("/user/personal_goals/")
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
            status.HTTP_404_NOT_FOUND, detail="Goals not found on this specific user"
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
@router.put("/user/personal_goals/{goal_id}")
def edit_personal_goal(
    user: user_dependency, goal: GoalRequestModel, goal_id: int, db: db_dependency
):
    # Querying Goal with user_id and specified goal_id
    db_goal = (
        db.query(Goal)
        .filter(Goal.user_id == user["id"], Goal.goal_id == goal_id)
        .first()
    )
    if not db_goal:
        raise HTTPException(status_code=404, detail="Goal not found")

    # we need user query for add_history functon
    user_db = db.query(User).filter(User.user_id == user["id"]).first()

    # Checking for goal_type
    if goal.goal_type_id is not None:
        goal_type = (
            db.query(Goal_Type)
            .filter(Goal_Type.goal_type_id == goal.goal_type_id)
            .first()
        )
        if not goal_type:
            raise HTTPException(status_code=404, detail="Specific Goal type not found")
        db_goal.goal_type_id = goal_type.goal_type_id

    changes = goal.dict()  # Request model can be dictionarized


    # Iterate over the changes and update the goal data
    for key, value in changes.items():
        if value is not None and getattr(db_goal, key) != value:
            setattr(db_goal, key, value)



    db.commit()
    db.refresh(db_goal)

    return db_goal


# Deletability for personal goals
@router.delete("/user/personal_goals/{goal_id}")
def delete_personal_goal(user: user_dependency, goal_id: int, db: db_dependency):
    db_goal = (
        db.query(Goal)
        .filter(Goal.user_id == user["id"], Goal.goal_id == goal_id)
        .first()
    )
    if not db_goal:
        raise HTTPException(status_code=404, detail="Goal not found")

    db.delete(db_goal)
    db.commit()

    return {"message": "Goal successfully deleted"}


# Section For Schedule Routes, For Getting, Posting, Editing and Deleting


@router.get("/user/create_schedule")
def get_schedule_data(user: user_dependency, db: db_dependency):
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
                goal_type_id=exercise.goal_type_id,
                exercise_type_name=exercise.exercise_type.exercise_type_name,
            )
            for exercise in exercises
        ]
    }


@router.post("/user/create_schedule")
def create_schedule(
    user: user_dependency, db: db_dependency, schedule: ScheduleRequestModel
):
    # Querring current user
    user = db.query(User).filter(User.user_id == user["id"]).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User Not Found"
        )
    goal = db.query(Goal).filter(Goal.goal_id == schedule.goal_id).first()
    if goal:
        selected_exercises = list(
            set(goal.selected_exercises).union(schedule.selected_exercises)
        )

        new_schedule = Schedule(
            goal_id=schedule.goal_id,
            user_id=user.user_id,
            start_date=schedule.start_date,
            end_date=schedule.end_date,
            selected_exercises=selected_exercises,
            note=schedule.note,
            extended_note=schedule.extended_note,
            crontab_value=schedule.crontab_value,
        )

    else:
        new_schedule = Schedule(
            user_id=user.user_id,
            start_date=schedule.start_date,
            end_date=schedule.end_date,
            selected_exercises=schedule.selected_exercises,
            note=schedule.note,
            extended_note=schedule.extended_note,
            crontab_value=schedule.crontab_value,
        )
    try:
        db.add(new_schedule)
        db.commit()
        db.refresh(new_schedule)
        return {"Request Succesful": "Schedule entry has been added"}

    except:
        raise HTTPException(status.HTTP_400_BAD_REQUEST)


@router.get("/user/schedules/")
def get_personal_schedules(user: user_dependency, db: db_dependency):
    schedules = db.query(Schedule).filter(Schedule.user_id == user["id"]).all()
    if not schedules:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            detail="Schedules not found on this specific user",
        )

    schedules_dict = []
    for schedule in schedules:
        if schedule.goal_id:
            goal = db.query(Goal).filter(Goal.goal_id == schedule.goal_id).first()
            if goal:
                selected_exercises = list(
                    set(goal.selected_exercises).union(schedule.selected_exercises)
                )
            else:
                selected_exercises = schedule.selected_exercises
        else:
            selected_exercises = schedule.selected_exercises

        schedules_dict.append(
            dict(
                schedule_id=schedule.schedule_id,
                user_id=schedule.user_id,
                goal_id=schedule.goal_id,
                start_date=schedule.start_date,
                end_date=schedule.end_date,
                selected_exercises=selected_exercises,
                note=schedule.note,
                extended_note=schedule.extended_note,
                crontab_value=schedule.crontab_value,
            )
        )

    return {"schedules": schedules_dict}


@router.put("/user/schedules/{schedule_id}")
def edit_personal_schedule(
    user: user_dependency,
    schedule: ScheduleRequestModel,
    schedule_id: int,
    db: db_dependency,
):
    # Querying Schedule with user_id and specified schedule_id
    db_schedule = (
        db.query(Schedule)
        .filter(Schedule.user_id == user["id"], Schedule.schedule_id == schedule_id)
        .first()
    )

    if not db_schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")

    # we need user query for add_history function
    user_db = db.query(User).filter(User.user_id == user["id"]).first()

    if schedule.goal_id:
        goal = db.query(Goal).filter(Goal.goal_id == schedule.goal_id).first()
        if goal:
            selected_exercises = list(
                set(goal.selected_exercises).union(schedule.selected_exercises)
            )
            schedule.selected_exercises = selected_exercises


    # Iterating over the changes and update the schedule data
    for attr, value in schedule.dict().items():
        if value is not None:
            setattr(db_schedule, attr, value)


    db.commit()
    db.refresh(db_schedule)

    return db_schedule


@router.delete("/user/schedules/{schedule_id}")
def delete_personal_schedule(
    user: user_dependency, schedule_id: int, db: db_dependency
):
    schedule = (
        db.query(Schedule)
        .filter(Schedule.user_id == user["id"], Schedule.schedule_id == schedule_id)
        .first()
    )

    if not schedule:
        raise HTTPException(status_code=404, detail="schedule not found")

    db.delete(schedule)
    db.commit()

    return {"message": "Goal successfully deleted"}


@router.get("/user/history")
def get_user_history(user: user_dependency, db: db_dependency):
    user_histories = (
        db.query(User_History).filter(User_History.user_id == user["id"]).all()
    )
    if not user_histories:
        raise HTTPException(status_code=404, detail="histories not found")

    result = []
    for history in user_histories:
        history_dict = {}
        history_dict["history_id"] = history.history_id
        history_dict["created"] = history.created
        if history.fullname_change is not None:
            history_dict["fullname_change"] = history.fullname_change
        if history.weight_change is not None:
            history_dict["weight_change"] = history.weight_change
        if history.height_change is not None:
            history_dict["height_change"] = history.height_change
        if history.bmi_calculation is not None:
            history_dict["bmi_calculation"] = history.bmi_calculation
        result.append(history_dict)
    return result


@router.delete("/user/history/{history_id}")
def delete_user_history(user: user_dependency, db: db_dependency, history_id: int):
    history = db.query(User_History).filter(
        User_History.user_id == user["id"], User_History.history_id == history_id
    )

    if not history:
        raise HTTPException(status_code=404, detail="history not found")

    db.delete(history)
    db.commit()

    return {"message": "History Successfully deleted"}


def add_history(
    db,
    user,
    fullname_change=None,
    weight_change=None,
    height_change=None,
    bmi_calculation=None
):

    new_history = User_History(
        user_id=user.user_id,
        fullname_change=fullname_change,
        weight_change=weight_change,
        height_change=height_change,
        bmi_calculation=bmi_calculation
    )
    db.add(new_history)
    db.commit()
    db.refresh(new_history)
    return new_history


@router.post("/add_bmi_history/{bmi_value}")
def bmi_history_addition(user: user_dependency, db: db_dependency, bmi_value: int):
    user_db = db.query(User).filter(User.user_id == user["id"]).first()
    add_history(db, user_db.user_id, bmi_calculation=bmi_value)
