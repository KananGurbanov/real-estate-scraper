from fastapi import FastAPI, Query, Depends
from typing import List
from sqlalchemy.orm import Session
from repository.models import Listing
from sqlalchemy import create_engine, desc, asc
from sqlalchemy.orm import sessionmaker
from dto.dto import ListingDTO, PaginatedListingsResponse

DATABASE_URL = "postgresql://postgres:postgres@localhost:5433/real_estate_db"

app = FastAPI()

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/listings/", response_model=PaginatedListingsResponse)
def search_listings(
    filters: ListingDTO = Depends(),
    db: Session = Depends(get_db)
):
    query = db.query(Listing)

    if filters.min_price is not None:
        query = query.filter(Listing.price >= filters.min_price)
    if filters.max_price is not None:
        query = query.filter(Listing.price <= filters.max_price)
    if filters.min_lat is not None:
        query = query.filter(Listing.latitude >= filters.min_lat)
    if filters.max_lat is not None:
        query = query.filter(Listing.latitude <= filters.max_lat)
    if filters.min_lng is not None:
        query = query.filter(Listing.longitude >= filters.min_lng)
    if filters.max_lng is not None:
        query = query.filter(Listing.longitude <= filters.max_lng)
    if filters.min_area is not None:
        query = query.filter(Listing.area >= filters.min_area)
    if filters.max_area is not None:
        query = query.filter(Listing.area <= filters.max_area)
    if filters.min_rooms is not None:
        query = query.filter(Listing.room_count >= filters.min_rooms)
    if filters.max_rooms is not None:
        query = query.filter(Listing.room_count <= filters.max_rooms)
    if filters.deed_status is not None:
        query = query.filter(Listing.deed_status == filters.deed_status)

    if filters.sort_order == "desc":
        query = query.order_by(desc(Listing.created_at))
    else:
        query = query.order_by(asc(Listing.created_at))

    total_count = query.count()
    listings = query.offset((filters.page - 1) * filters.page_size).limit(filters.page_size).all()

    listing_dtos = [ListingDTO.from_orm(listing) for listing in listings]

    return PaginatedListingsResponse(
        total_count=total_count,
        page=filters.page,
        page_size=filters.page_size,
        listings=listing_dtos
    )
