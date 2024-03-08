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


@app.get("/user", status_code=status.HTTP_200_OK)
async def user(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentification Failed")
    return {"User": user}

