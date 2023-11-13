import hashlib

from fastapi import FastAPI, Depends, Form
from typing import Annotated

from starlette.responses import RedirectResponse

import models
from database import engine, SessionLocal
from sqlalchemy.orm import Session

app = FastAPI()
models.Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


@app.post("/customer/register/submit")
async def register(
        db: db_dependency,
        name: str = Form(None),
        email: str = Form(None),
        password: str = Form(None),
        confirm_password: str = Form(None)
):
    if name is None:
        return RedirectResponse("/?error=Name is require", 302)
    if email is None:
        return RedirectResponse("/?error=Email is required", 302)
    if password is None:
        return RedirectResponse("/?error=Password is required", 302)
    if confirm_password is None:
        return RedirectResponse("/?error=Confirm password is required", 302)
    if password != confirm_password:
        return RedirectResponse("/?error=Passwords+do+not+match", 302)

    existing_user = db.query(models.Customers).filter(models.Customers.email == email).first()
    if existing_user:
        return RedirectResponse("/?error=Email+already+exists", 302)

    hashed_password = hashlib.md5(password.encode()).hexdigest()
    register_db = models.Customers(
        name=name,
        email=email,
        password=hashed_password,
    )
    # print(name,email,password, hashed_password)
    db.add(register_db)
    db.commit()
    db.refresh(register_db)
    return RedirectResponse("/?success=Customer+Registration+successfully", 302)
