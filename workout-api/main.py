from fastapi import FastAPI
from database import engine, Base
from seed import populate_database

from routes import (
    auth, exercise_routes, goal_routes,
    history_routes, schedule_routes, user_routes
)


app = FastAPI()

# Adding Auth Router
app.include_router(auth.auth)
app.include_router(user_routes.user_route)
app.include_router(exercise_routes.exercise)
app.include_router(goal_routes.goal)
app.include_router(schedule_routes.schedule)
app.include_router(history_routes.hist)


Base.metadata.create_all(bind=engine)


populate_database()
