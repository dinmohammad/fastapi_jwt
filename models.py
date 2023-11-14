from sqlalchemy import TIMESTAMP, func, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column
from sqlalchemy.types import String, Integer
from config.database import Base


class Customers(Base):
    __tablename__ = "customers_db"

    id = Column(Integer, primary_key=True, index=True)
    user_type = Column(Integer, default=1)
    name = Column(String(50))
    email = Column(String(100))
    password = Column(String(500))
    access_token = Column(String(300), default=None)
    refresh_token = Column(String(300), default=None)
    status = Column(Integer, default=1)
    created_at = Column(TIMESTAMP, default=func.now())


class Trips(Base):
    __tablename__ = "trips"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("customers_db.id"))
    car_name = Column(String(50))
    pick_up_location = Column(String(100))
    destination = Column(String(100))
    status = Column(Integer, default=1)
    created_at = Column(TIMESTAMP, default=func.now())
    customer = relationship('customers_db', backref='trips')