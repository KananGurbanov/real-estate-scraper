from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class ListingDTO(BaseModel):
    id: int
    url: Optional[str] = None
    data_item_id: Optional[int] = None
    price: Optional[int] = None
    location: Optional[str] = None
    og_title: Optional[str] = None
    og_description: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    owner_name: Optional[str] = None
    owner_type: Optional[str] = None
    category: Optional[str] = None
    area: Optional[float] = None
    land_area: Optional[str] = None
    room_count: Optional[int] = None
    deed_status: Optional[bool] = None
    renovation_status: Optional[bool] = None
    image_urls: Optional[List[str]] = None
    created_at: datetime

    class Config:
        from_attributes = True


class PaginatedListingsResponse(BaseModel):
    total_count: int
    page: int
    page_size: int
    listings: List[ListingDTO]
