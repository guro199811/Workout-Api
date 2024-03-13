from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from starlette import status
from database import SessionLocal


# For Debugging
import logging

from models import User

from form_models import ChangeUserDataRequest, ChangeUserDataRequest


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
from .auth import get_current_user

# user_dependency will act as login_required
user_dependency = Annotated[dict, Depends(get_current_user)]

from .history_routes import add_history


# For user management

user_route = APIRouter(prefix="/user", tags=["user"])


@user_route.get("/", status_code=status.HTTP_200_OK)
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


@user_route.put("/user_data_change")
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
    except Exception as e:
        db.rollback()
        logging.error(f"Exception raised at change_user_data(put) function: {e}")
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR)
