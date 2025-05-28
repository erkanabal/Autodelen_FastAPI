import unittest
from sqlalchemy import create_engine, Column, Integer, String, Enum, ForeignKey
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from enum import Enum as PyEnum

# Enum tanımı
class UserRoleEnum(str, PyEnum):
    owner = "owner"
    renter = "renter"
    passenger = "passenger"
    admin = "admin"

# Veritabanı ve model kurulumları
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String, unique=True)
    password = Column(String)
    role = Column(Enum(UserRoleEnum), nullable=False)

    rides = relationship("Ride", back_populates="driver")

class Ride(Base):
    __tablename__ = "rides"
    id = Column(Integer, primary_key=True, index=True)
    driver_id = Column(Integer, ForeignKey("users.id"))
    departure_location = Column(String)
    arrival_location = Column(String)
    available_seats = Column(Integer)

    driver = relationship("User", back_populates="rides")
    rentals = relationship("RideRental", back_populates="ride")

class RideRental(Base):
    __tablename__ = "ride_rentals"
    id = Column(Integer, primary_key=True, index=True)
    ride_id = Column(Integer, ForeignKey("rides.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    seats_reserved = Column(Integer)

    ride = relationship("Ride", back_populates="rentals")
    user = relationship("User")

# Test sınıfı
class TestRideRentalPassengerCRUD(unittest.TestCase):
    def setUp(self):
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(bind=engine)
        self.Session = sessionmaker(bind=engine)
        self.db = self.Session()

        # Test kullanıcı
        self.user = User(
            name="Test User",
            email="test@example.com",
            password="hashedpassword",
            role=UserRoleEnum.passenger  # GEÇERLİ Enum değeri
        )
        self.db.add(self.user)
        self.db.commit()
        self.db.refresh(self.user)

    def tearDown(self):
        self.db.close()

    def test_create_ride_success(self):
        ride = Ride(
            driver_id=self.user.id,
            departure_location="Point A",
            arrival_location="Point B",
            available_seats=3
        )
        self.db.add(ride)
        self.db.commit()
        self.db.refresh(ride)

        self.assertIsNotNone(ride.id)
        self.assertEqual(ride.driver_id, self.user.id)

    def test_create_riderental_success(self):
        ride = Ride(
            driver_id=self.user.id,
            departure_location="Point A",
            arrival_location="Point B",
            available_seats=3
        )
        self.db.add(ride)
        self.db.commit()
        self.db.refresh(ride)

        rental = RideRental(
            ride_id=ride.id,
            user_id=self.user.id,
            seats_reserved=2
        )
        self.db.add(rental)
        self.db.commit()
        self.db.refresh(rental)

        self.assertIsNotNone(rental.id)
        self.assertEqual(rental.seats_reserved, 2)

if __name__ == '__main__':
    unittest.main()
