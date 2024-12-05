from sqlalchemy import ARRAY, Boolean

from sqlalchemy import Column, Integer, String, Float, DateTime, func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Listing(Base):
    __tablename__ = 'listings'

    id = Column(Integer, primary_key=True, autoincrement=True)
    url = Column(String, nullable=True)
    data_item_id = Column(Integer, nullable=True)
    price = Column(Integer, nullable=True)
    location = Column(String, nullable=True)
    og_title = Column(String, nullable=True)
    og_description = Column(String, nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    owner_name = Column(String, nullable=True)
    owner_type = Column(String, nullable=True)
    category = Column(String, nullable=True)
    area = Column(Float, nullable=True)
    land_area = Column(String, nullable=True)
    room_count = Column(Integer, nullable=True)
    deed_status = Column(Boolean, nullable=True)
    renovation_status = Column(Boolean, nullable=True)
    image_urls = Column(ARRAY(String), nullable=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)





