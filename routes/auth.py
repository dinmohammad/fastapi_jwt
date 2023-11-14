import hashlib
from datetime import timedelta

from fastapi import Form, APIRouter
from starlette import status
from starlette.responses import RedirectResponse

import models
from config.database import db_dependency, engine
from core.auth_utils import ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_MINUTES, create_access_token, \
    create_refresh_token

router = APIRouter()


@router.post("/customer-login", status_code=status.HTTP_200_OK, tags=["Authentication"])
async def drover_login_user(
        db: db_dependency,
        email: str = Form(None),
        password: str = Form(None)
):
    if email is None:
        return RedirectResponse("/?error=Email is required", 302)
    if password is None:
        return RedirectResponse("/?error=Password is required", 302)
    db_user = db.query(models.Customers).filter(models.Customers.email == email).first()
    if db_user and db_user.password == hashlib.md5(password.encode()).hexdigest():
        if db_user.status == 1:
            # If the user is authenticated, generate an access token
            access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            refresh_token_expires = timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)
            access_token = create_access_token(db_user.email)
            refresh_token = create_refresh_token(db_user.email)

            # Update the access token in the database
            db_user.access_token = access_token
            db.commit()
            print(f"db_user:{db_user}")
            response = RedirectResponse("/?success=Login+successfully", 302)
            response.set_cookie(key="access_token", value=access_token, expires=access_token_expires)
            response.set_cookie(key="refresh_token", value=refresh_token, expires=refresh_token_expires)
            return response
            # Return the token in the response
            # return {"access_token": access_token, "token_type": "bearer", "user_type":1}
        return RedirectResponse("/?error=Account+is+banned", 302)
    return RedirectResponse("/?error=Invalid+email+or+password", 302)
