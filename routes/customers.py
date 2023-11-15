from fastapi import APIRouter, Form, Request
from starlette import status
from starlette.responses import RedirectResponse

import models
from config.database import db_dependency
from core.auth_utils import decode_token

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
    try:
        customerData = await decode_token(token, db)
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
        return {"You are not Authorized! Please Login"}
