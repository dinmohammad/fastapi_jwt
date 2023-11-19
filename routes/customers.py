import hashlib
from datetime import timedelta

from fastapi import APIRouter, Form, Request, HTTPException
from starlette import status
from starlette.responses import RedirectResponse, JSONResponse

import models
from config.database import db_dependency
from core.auth_utils import decode_token, ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_MINUTES, \
    create_access_token, create_refresh_token, decode_refresh_token, TokenDecodeError
from core.helper import get_user_by_email

customer = APIRouter()


@customer.post("/customer/booking/request", status_code=status.HTTP_200_OK, tags=["Customer"])
async def Booking_request(
        request: Request,
        db: db_dependency,
        car_name: str = Form(None),
        pick_up_location: str = Form(None),
        destination: str = Form(None)
):
    if car_name is None:
        return RedirectResponse("/?error=car name is require", 302)
    if pick_up_location is None:
        return RedirectResponse("/?error=pick up location is require", 302)
    if destination is None:
        return RedirectResponse("/?error=pick up location is require", 302)
    token = request.cookies.get("access_token")
    existing_refresh_token = request.cookies.get("refresh_token")

    try:
        customerData = await decode_token(token, db)
        print(customerData.id)
        booking_new_data = models.Trips(
            user_id=customerData.id,
            car_name=car_name,
            pick_up_location=pick_up_location,
            destination=destination
        )
        print(car_name, pick_up_location, destination, customerData.id, token)
        db.add(booking_new_data)
        db.commit()
        db.refresh(booking_new_data)
        return {"Booking request send successfully"}
    except:
        db_user = await decode_refresh_token(existing_refresh_token, db)
        print(db_user.email)

        # If the user is authenticated, generate an access token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        refresh_token_expires = timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(db_user.email)
        refresh_token = create_refresh_token(db_user.email)

        # Update the access token in the database
        db_user.access_token = access_token
        db.commit()

        response = RedirectResponse("/?success=create+accessToken", 404)
        response.set_cookie(key="access_token", value=access_token, expires=access_token_expires)
        response.set_cookie(key="refresh_token", value=refresh_token, expires=refresh_token_expires)
        return response


@customer.get("/my_booking_list/", tags=["Customer"], status_code=status.HTTP_201_CREATED)
async def booking_list(request: Request, db: db_dependency):
    token = request.cookies.get("access_token")
    try:
        customer_data =  await decode_token(token, db)
        if customer_data:
            booking_data = db.query(models.Trips).filter(models.Trips.user_id == customer_data.id).all()
            return {"data": booking_data}
        else:
           return JSONResponse(content={"error": "You are not authorized"}, status_code=403)
    except TokenDecodeError as e:
        return JSONResponse(content={"error": "You are not authorized"}, status_code=403)

    # if not booking_data:
    #     booking_data = None
    #     raise HTTPException(status_code=404, detail='No posts found')
    #     # return booking_data
    # return {"data": booking_data}
