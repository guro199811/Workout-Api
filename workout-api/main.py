from fastapi import FastAPI
from database import engine, Base

import auth
import routes


# Creating FastAPI instance
app = FastAPI()

# Adding Auth Router
app.include_router(auth.auth)
app.include_router(routes.router)

Base.metadata.create_all(bind=engine)
