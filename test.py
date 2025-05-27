from sqlalchemy.orm import Session
from app import models, database  # projene göre düzenle

db: Session = next(database.get_db())

rentals = db.query(models.Rental).all()
for r in rentals:
    print(f"Rental ID: {r.id}, User ID: {r.user_id}, Start: {r.start_date}, End: {r.end_date}")
