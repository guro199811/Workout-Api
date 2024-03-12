from fastapi import FastAPI
from database import engine, Base

from routes import (
    auth, exercise, goal,
    history, schedule, user
)
import time



# Creating FastAPI instance
app = FastAPI()

# Adding Auth Router
app.include_router(auth.auth)
app.include_router(user.user_route)
app.include_router(exercise.exercise)
app.include_router(goal.goal)
app.include_router(schedule.schedule)
app.include_router(history.hist)



Base.metadata.create_all(bind=engine)

def populate_db():
    time.sleep(3)
    from seed import populate_database
    populate_database()

populate_db()
