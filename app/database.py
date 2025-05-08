from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# .env dosyasını oku
load_dotenv()

# .env içindeki DATABASE_URL değişkenini al
DATABASE_URL = os.getenv("DATABASE_URL")

# SQLite için özel ayar: aynı thread'de çalışmasına izin ver
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# Oturum (session) sınıfı
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Tüm modellerin kalıtım alacağı Base sınıfı
Base = declarative_base()
