import hashlib
from datetime import timedelta

from fastapi import Form, APIRouter, Request, Response
from sqlalchemy import null
from starlette import status
from starlette.responses import RedirectResponse, JSONResponse

import models
from config.database import db_dependency, engine
from core.auth_utils import ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_MINUTES, create_access_token, \
    create_refresh_token, decode_token

router = APIRouter()


@router.post("/customer-login", status_code=status.HTTP_200_OK, tags=["Authentication"])
async def customer_login(
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

            # Create a dictionary with serializable values
            response_content = {
                "token": {
                    "access_token": access_token,
                    "refresh_token": refresh_token
                },
                "token_type": "bearer",
                "token_expires": {
                    "access_token_expires": access_token_expires.total_seconds(),
                    "refresh_token_expires": refresh_token_expires.total_seconds()
                }
            }

            # Create a JSONResponse with the serializable dictionary
            response = JSONResponse(content=response_content)

            response.set_cookie(key="access_token", value=access_token, expires=access_token_expires)
            response.set_cookie(key="refresh_token", value=refresh_token, expires=refresh_token_expires)
            return response

        return "/?error=Account+is+banned"
    return "/?error=Invalid+email+or+password"


@router.post("/logout", tags=["Authentication"])
async def logout(db: db_dependency, request: Request, response: Response):
    response = JSONResponse(
        content={
            "data": {
                "success": "successfully Logout"
            }
        }
    )
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")

    token = request.cookies.get("access_token")
    customer_data = await decode_token(token, db)
    customer_data.access_token = "null"
    db.commit()

    return response
