import logging

from repository.database import Session
def save_listing(data):
    session = Session()
    try:
        existing_record = session.query(type(data)).filter_by(data_item_id=data.data_item_id).first()
        if existing_record:
            logging.warning(f"Listing with data_item_id {data.data_item_id} already exists.")
            return

        session.add(data)
        session.commit()
        logging.info(f"Listing saved: {data.og_title}")
    except Exception as e:
        session.rollback()
        logging.error(f"Error saving listing: {e}")
    finally:
        session.close()
