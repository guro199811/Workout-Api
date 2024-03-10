from fastapi import FastAPI, status, Depends, HTTPException
from database import engine, SessionLocal
from typing import Annotated
from sqlalchemy.orm import Session
import models
import auth
from auth import get_current_user






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
async def user(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentification Failed")
    return {"User": user}



# For Main Page, Contains Exercises for displaying on main page
@app.get("/", status_code=status.HTTP_200_OK)
async def main(db: db_dependency):
    exercises = db.query(models.Exercise).all()
    #For Loop Here to extract exercise
    return {"exercises": exercises }



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

