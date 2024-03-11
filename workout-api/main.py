from fastapi import FastAPI, status, Depends, HTTPException
from database import engine, SessionLocal, Base
from typing import Annotated, Optional, List
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import asc, desc, or_
from models import (
    User, Goal, 
    Goal_Type, Exercise,
    Exercise_Type, Exercise_Unit,
    Schedule, User_History)
import auth
from auth import get_current_user
from sqlalchemy.orm import joinedload
from pydantic import BaseModel
import logging





# Creating FastAPI instance
app = FastAPI()

# Adding Auth Router
app.include_router(auth.router)

Base.metadata.create_all(bind=engine)



def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]

#user_dependency will act as login_required
user_dependency = Annotated[dict, Depends(get_current_user)]



# Request model
class GoalRequestModel(BaseModel):
    goal_name: str = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    range_min: Optional[int] = None
    range_max: Optional[int] = None
    selected_exercises: List[int] = None
    goal_type_id: int = None
    completed: Optional[bool] = None



# For User Menu, Contains User Data
@app.get("/user", status_code=status.HTTP_200_OK)
def user_data(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Authentification Failed")
    return {"User": user}



# For Main Page, Contains Exercises for displaying on main page
@app.get("/", status_code=status.HTTP_200_OK)
def main(db: db_dependency):
    exercises = db.query(Exercise).\
            join(Exercise_Type).\
                options(joinedload(Exercise.exercise_type)).\
                   order_by(asc(Exercise_Type.exercise_type_id)).all()
    if not exercises:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Exercises were not found")
    
    return {"exercises": [dict(
        exercise_id=exercise.exercise_id,
        exercise_name=exercise.exercise_name,
        description=exercise.description,
        instructions=exercise.instructions,
        target_muscles=exercise.target_muscles,
        difficulty=exercise.difficulty,
        exercise_type_id=exercise.exercise_type_id,
        unit_type_id=exercise.unit_type_id,
        goal_type_id=exercise.goal_type_id,
        exercise_type_name=exercise.exercise_type.exercise_type_name) for exercise in exercises]}


# Searches the exercise by exercise_id
@app.get("/exercises/{exercise_id}")
def get_exercise(exercise_id: int, db: db_dependency):
    exercise = db.query(Exercise).filter(Exercise.exercise_id == exercise_id).first()
    if not exercise:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Exercise not found")
    return {"exercises": exercise}


# This 3 routes are designed for developers to understand
@app.get('/api/all_goal_types/')
def all_goal_types(db: db_dependency):
    goal_types = db.query(Goal_Type).all()
    if not goal_types:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Goal Types are not populated...")
    return {"goal_types": goal_types}



@app.get('/api/all_exercise_types')
def all_exercise_types(db: db_dependency):
    exercise_types = db.query(Exercise_Type).all()
    if not exercise_types:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Exercise types are not populated...")
    return {"exercise_types": exercise_types}



@app.get('/api/all_exercise_units')
def all_exercise_units(db: db_dependency):
    exercise_units = db.query(Exercise_Unit).all()
    if not exercise_units:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Exercise units are not populated...")
    return {"exercise_units": exercise_units}



# Goals Routes, For Getting, Posting, Editing and Deleting
@app.get("/user/personal_goals/")
def personal_goals_get(user: user_dependency, db: db_dependency):
    user_goals = db.query(Goal).\
        join(Goal_Type).filter(Goal.user_id == user['id']).\
            order_by(Goal.start_date.asc(), Goal.created_time.asc()).all()
    if not user_goals:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Goals not found on this specific user_id")

    user_goals_dict = []
    for goal in user_goals:
        # Query of the exercises "related" to the goal using in_ operator
        selected_exercises = db.query(Exercise).filter(Exercise.exercise_id.in_(goal.selected_exercises)).all()
        
        # Goal type target relationship to get a goal type name
        goal_type_target = goal.goal_type.goal_target
        
        # Converting the exercises to a list of dictionaries
        selected_exercises_dict = []
        for exercise in selected_exercises:
            # Query the exercise unit related to the exercise
            exercise_unit = db.query(Exercise_Unit).filter(Exercise_Unit.unit_id == exercise.unit_type_id).first()

            selected_exercises_dict.append(dict(
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
                goal_type_id=exercise.goal_type_id
            ))

        user_goals_dict.append(dict(
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
            goal_target=goal_type_target
        ))

    return {"user_goals": user_goals_dict}



# Editability forr personal goals
@app.put("/user/personal_goals/{goal_id}")
def personal_goals_put(user: user_dependency, goal: GoalRequestModel, goal_id: int, db: db_dependency):
    # Querying Goal with user_id and specified goal_id
    db_goal = db.query(Goal).filter(Goal.user_id == user['id'], Goal.goal_id == goal_id).first()
    if not db_goal:
        raise HTTPException(status_code=404, detail="Goal not found")

    # Checking for goal_type
    if goal.goal_type_id is not None:
        goal_type = db.query(Goal_Type).filter(Goal_Type.goal_type_id == goal.goal_type_id).first()
        if not goal_type:
            raise HTTPException(status_code=404, detail="Goal type not found")
        db_goal.goal_type_id = goal_type.goal_type_id

    for key, value in goal.dict().items():
        if value is not None:
            setattr(db_goal, key, value)

    db.commit()
    db.refresh(db_goal)

    return db_goal


# Deleteability for personal goals
@app.delete("/user/personal_goals/{goal_id}")
def personal_goals_delete(user: user_dependency, goal_id: int, db: db_dependency):
    db_goal = db.query(Goal).filter(Goal.user_id == user['id'], Goal.goal_id == goal_id).first()
    if not db_goal:
        raise HTTPException(status_code=404, detail="Goal not found")

    db.delete(db_goal)
    db.commit()

    return {"message": "Goal successfully deleted"}


# Custom exercises, For Getting data, Posting data, Editing data and Deleting data
@app.get("/user/create_goals/")
def create_goals_get(user: user_dependency, db: db_dependency):
    exercises = db.query(Exercise).\
        join(Goal_Type).\
            options(joinedload(Exercise.exercise_type)).\
                order_by(asc(Goal_Type.goal_type_id)).all()
    if not exercises:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Exercises were not found")
    
    return {"exercises": [dict(
        goal_target=exercise.goal_type.goal_target,
        exercise_id=exercise.exercise_id,
        exercise_name=exercise.exercise_name,
        description=exercise.description,
        instructions=exercise.instructions,
        target_muscles=exercise.target_muscles,
        difficulty=exercise.difficulty,
        goal_type_id=exercise.goal_type_id) for exercise in exercises]}



@app.post("/user/personal_workout/")
def create_goals_post(user: user_dependency, db: db_dependency, goal: GoalRequestModel):
    # Getting current user
    user = db.query(User).filter(User.user_id == user['id']).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    # Checking for goaltypes existance
    goal_type = db.query(Goal_Type).filter(Goal_Type.goal_type_id == goal.goal_type_id).first()
    if not goal_type:
        raise HTTPException(status_code=404, detail="Goal type not found")

    new_goal = Goal(
        goal_name=goal.goal_name,
        user_id=user.user_id,
        start_date=goal.start_date,
        end_date=goal.end_date,
        range_min=goal.range_min,
        range_max=goal.range_max,
        selected_exercises=goal.selected_exercises,
        completed=goal.completed,
        goal_type_id=goal.goal_type_id
    )
    try:
        db.add(new_goal)
        db.commit()
        db.refresh(new_goal)
        return {"Request Succesfull":"Goal entry added"}
    except:
        raise HTTPException(status.HTTP_412_PRECONDITION_FAILED)




