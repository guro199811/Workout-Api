from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime



# Data Validation
class CreateUserRequest(BaseModel):
    username: str
    fullname: Optional[str]
    password: str
    weight: Optional[int]
    height: Optional[int]


class Token(BaseModel):
    access_token: str
    token_type: str


class GoalRequestModel(BaseModel):
    goal_name: str = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    range_min: Optional[int] = None
    range_max: Optional[int] = None
    selected_exercises: List[int] = None
    goal_type_id: int = None
    completed: Optional[bool] = None


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
