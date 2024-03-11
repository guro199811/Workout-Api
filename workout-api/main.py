from fastapi import FastAPI, status, Depends, HTTPException
from database import engine, SessionLocal
from typing import Annotated
from sqlalchemy.orm import Session
from sqlalchemy import asc, desc
import models
import auth
from auth import get_current_user
from sqlalchemy.orm import joinedload






# Creating FastAPI instance
app = FastAPI()

# Adding Auth Router
app.include_router(auth.router)

models.Base.metadata.create_all(bind=engine)



def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]

#user_dependency will act as login_required
user_dependency = Annotated[dict, Depends(get_current_user)]


# For User Menu, Contains User Data
@app.get("/user", status_code=status.HTTP_200_OK)
def user_data(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentification Failed")
    return {"User": user}



# For Main Page, Contains Exercises for displaying on main page
@app.get("/", status_code=status.HTTP_200_OK)
def main(db: db_dependency):
    exercises = db.query(
        models.Exercise).\
            join(models.Exercise_Type).\
                options(joinedload(models.Exercise.exercise_type)).\
                    order_by(asc(models.Exercise_Type.exercise_type_id)).all()
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



# Workouts Urls, For Getting data, Posting data, Editing data and Deleting data
@app.get("/user/personal_workout/{user_id}")
def workouts_get(user: user_dependency, db: db_dependency):
    pass


@app.post("/user/personal_workout/{user_id}")
def workouts_post(user: user_dependency, db: db_dependency):
    pass


@app.put("/user/personal_workout/{user_id}")
def workouts_put(user: user_dependency, db: db_dependency):
    pass


@app.delete("/user/personal_workout/{user_id}")
def workouts_delete(user: user_dependency, db: db_dependency):
    pass



# Goals Urls, For Getting, Posting, Editing and Deleting
@app.get("/user/personal_goals/{user_id}")
def goals_get(user: user_dependency, db: db_dependency):
    pass


@app.post("/user/personal_goals/{user_id}")
def goals_post(user: user_dependency, db: db_dependency):
    pass


@app.put("/user/personal_goals/{user_id}")
def goals_put(user: user_dependency, db: db_dependency):
    pass


@app.delete("/user/personal_goals/{user_id}")
def goals_delete(user: user_dependency, db: db_dependency):
    pass

