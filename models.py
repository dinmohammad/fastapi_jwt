from sqlalchemy import TIMESTAMP, func
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