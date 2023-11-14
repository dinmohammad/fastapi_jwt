from fastapi import APIRouter, Form
from starlette.responses import RedirectResponse

from config.database import db_dependency

customer = APIRouter()


@customer.post("customer/booking/request", tags=["Customer"])
async def Booking_request(
    db: db_dependency,
    car_name: str = Form(None),
    pick_up_location: str = Form(None),
    destination: str = Form(None),
):
    if car_name is None:
        return RedirectResponse("/?error=car name is require", 302)
    if pick_up_location is None:
        return RedirectResponse("/?error=pick up location is require", 302)

    print("car_name")
    # return {"Result": "ok"}

