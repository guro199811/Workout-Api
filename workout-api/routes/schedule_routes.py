from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette import status
from database import SessionLocal
import logging

from .auth import get_current_user
from form_models import ScheduleRequestModel
from models import (
    User, Goal, Schedule,
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


# Section For Schedule Routes, For Getting, Posting, Editing and Deleting

schedule = APIRouter(prefix="/schedule", tags=["schedules"])


@schedule.post(
    "/create_schedule",
    description="This endpoint creates a user related schedule"
)
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

    except Exception as e:
        logging.error(
            f"Exception raised at create_schedule(post) function: {e}")
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR)


@schedule.get(
    "/user_schedules/",
    description="This endpoint querries user related schedules"
)
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
            goal = db.query(Goal).filter(
                Goal.goal_id == schedule.goal_id).first()
            if goal:
                selected_exercises = list(
                    set(goal.selected_exercises).union(
                        schedule.selected_exercises)
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


@schedule.put(
    "/user_schedules/{schedule_id}",
    description="This endpoint edits user related schedule by schedule_id",
)
def edit_personal_schedule(
    user: user_dependency,
    schedule: ScheduleRequestModel,
    schedule_id: int,
    db: db_dependency,
):
    # Querying Schedule with user_id and specified schedule_id
    db_schedule = (
        db.query(Schedule)
        .filter(Schedule.user_id == user["id"],
                Schedule.schedule_id == schedule_id)
        .first()
    )

    if not db_schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")

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

    try:
        db.commit()
        db.refresh(db_schedule)
        return db_schedule
    except Exception as e:
        logging.error(
            f"Exception raised at edit_personal_schedule(put) function: {e}")
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR)


@schedule.delete(
    "/user_schedules/{schedule_id}",
    description="This endpoint deletes user related schedule by schedule_id",
)
def delete_personal_schedule(
    user: user_dependency, schedule_id: int, db: db_dependency
):
    schedule = (
        db.query(Schedule)
        .filter(Schedule.user_id == user["id"],
                Schedule.schedule_id == schedule_id)
        .first()
    )

    if not schedule:
        raise HTTPException(status_code=404, detail="schedule not found")

    try:
        db.delete(schedule)
        db.commit()
        return {"message": "Goal successfully deleted"}
    except Exception as e:
        logging.error(
            f"Exception raised at delete schedule(delete) function: {e}"
        )
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR)
