from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from app import models, schemas, crud, auth
from app.database import engine, SessionLocal
from app.config import settings


# Veritabanındaki tabloları oluştur
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "API is running!"}

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/register", response_model=schemas.UserOut)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db, user)

@app.post("/token", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = crud.get_user_by_email(db, form_data.username)
    if not user:
        raise HTTPException(status_code=400, detail="Invalid credentials")
    if not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    
    access_token = auth.create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

# Giriş yapan kullanıcıyı JWT token'dan çekmek için
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(status_code=401, detail="Could not validate credentials")
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = crud.get_user_by_email(db, email=email)
    if user is None:
        raise credentials_exception
    return user


# Araç ekleme endpoint'i (giriş yapmış kullanıcıya özel) Burayi daha sonraki asamada kullanacagiz...
    # @app.post("/vehicles", response_model=schemas.VehicleOut)
    # def create_vehicle(
    #     vehicle: schemas.VehicleCreate,
    #     db: Session = Depends(get_db),    
    # ):
    #     return crud.create_vehicle(db=db, vehicle=vehicle, user_id=current_user.id)

#gecici cozum
    # @app.post("/vehicles", response_model=schemas.VehicleOut)
    # def create_vehicle(vehicle: schemas.VehicleCreate, db: Session = Depends(get_db)):
    #     db_vehicle = crud.create_vehicle(db=db, vehicle=vehicle, user_id=1)  # user_id geçici olarak sabit
    #     return db_vehicle

@app.post("/vehicles", response_model=schemas.VehicleOut)
def create_vehicle(vehicle: schemas.VehicleCreate, db: Session = Depends(get_db)):
    # Geçici kullanıcı varsayımı (örneğin ID=1)
    fake_user = db.query(models.User).filter(models.User.id == 1).first()
    if not fake_user:
        raise HTTPException(status_code=404, detail="Kullanıcı bulunamadı")

    db_vehicle = models.Vehicle(**vehicle.dict(), owner_id=fake_user.id)
    db.add(db_vehicle)
    db.commit()
    db.refresh(db_vehicle)
    return db_vehicle
