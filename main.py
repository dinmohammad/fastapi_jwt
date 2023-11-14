import hashlib
from fastapi import FastAPI, Form
from starlette.responses import RedirectResponse
import models

from core.helper import get_user_by_email
from config.database import engine, db_dependency

import routes.auth
import  routes.customer

app = FastAPI()
models.Base.metadata.create_all(bind=engine)


@app.post("/customer/register/submit", tags=["Registration"])
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

    existing_user = await get_user_by_email(email, db, models.Customers)
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

# Auth route
app.include_router(routes.auth.router)


# Customer Booking post
app.include_router(routes.customer.customer)

