from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette import status
from database import SessionLocal
import logging

from .auth import get_current_user
from models import User, User_History


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]

# user_dependency will act as login_required
user_dependency = Annotated[dict, Depends(get_current_user)]


# Section for history routes

hist = APIRouter(prefix="/history", tags=["history"])


@hist.get("/", description="This endpoint returns user related histories.")
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


def add_history(
    db,
    user,
    fullname_change=None,
    weight_change=None,
    height_change=None,
    bmi_calculation=None,
):

    new_history = User_History(
        user_id=user.user_id,
        fullname_change=fullname_change,
        weight_change=weight_change,
        height_change=height_change,
        bmi_calculation=bmi_calculation,
    )
    try:
        db.add(new_history)
        db.commit()
        db.refresh(new_history)
        return new_history
    except Exception as e:
        logging.error(f"Exception raised at add_history function: {e}")


@hist.post("/add_bmi_history/{bmi_value}",
           description="Endpoint and adds history of bmi.")
def bmi_history_addition(user: user_dependency,
                         db: db_dependency, bmi_value: int):
    user_db = db.query(User).filter(User.user_id == user["id"]).first()
    add_history(db, user_db, bmi_calculation=bmi_value)
    return {"message": "Bmi History Added"}


@hist.delete("/{history_id}",
             description='This endpoint removes user history by history_id')
def delete_user_history(user: user_dependency,
                        db: db_dependency, history_id: int):
    history = db.query(User_History).filter(
        User_History.user_id == user["id"],
        User_History.history_id == history_id
    ).first()

    if not history:
        raise HTTPException(status_code=404, detail="history not found")

    try:
        db.delete(history)
        db.commit()
    except Exception as e:
        logging.error(f"Exception raised at delete history function: {e}")
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR)

    return {"message": "History Successfully deleted"}
