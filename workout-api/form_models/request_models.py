from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime


# Data Validation
class CreateUserRequest(BaseModel):
    username: str = Field(min_length=6, max_length=20,
                          description='Username should be greater than 5,' +
                          " but not higher than 20")
    fullname: Optional[str] = None
    password: str = Field(min_length=6,
                          description='Password should be greater than 5')
    weight: Optional[int] = Field(None, gt=30, lt=300)
    height: Optional[int] = Field(None, ge=50, lt=300)
    active: Optional[bool] = True


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
    goal_type_id: int = Field(None, ge=1)
    completed: Optional[bool] = None

    @validator("range_max")
    def check_range(cls, v, values):
        if "range_min" in values and v < values["range_min"]:
            raise ValueError("range_max must not be lower than range_min")
        return v

    @validator("end_date")
    def check_dates(cls, v, values):
        if "start_date" in values and v < values["start_date"]:
            raise ValueError("end_date must not be earlier than start_date")
        return v


class ScheduleRequestModel(BaseModel):
    goal_id: Optional[int] = Field(None, ge=1)
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    selected_exercises: List[int] = None
    note: Optional[str] = Field(None, max_length=50,
                                description="Note should not exceed 50 chars")
    extended_note: Optional[str] = Field(None, max_length=250,
                                         description="Extended note " +
                                         "should not exceed 250 chars")
    crontab_value: Optional[str] = None

    @validator("end_date")
    def check_dates(cls, v, values):
        if "start_date" in values and v < values["start_date"]:
            raise ValueError("end_date must not be earlier than start_date")
        return v


class ChangeUserDataRequest(BaseModel):
    fullname: Optional[str] = None
    weight: Optional[int] = Field(None, gt=30, lt=300)
    height: Optional[int] = Field(None, ge=50, lt=300)
