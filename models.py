from sqlalchemy import Column, Integer, String, Date, Boolean, create_engine, ForeignKey, Text
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///swasthya.db")
engine = create_engine(DATABASE_URL, echo=False, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    wa_user_id = Column(String, unique=True, index=True)  # WhatsApp phone or wa id
    language = Column(String, default="en")
    consent = Column(Boolean, default=False)
    pincode = Column(String, nullable=True)
    fullname = Column(String, nullable=True)

    children = relationship("Child", back_populates="user")

class Child(Base):
    __tablename__ = "children"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    dob = Column(Date, nullable=False)

    user = relationship("User", back_populates="children")

def init_db():
    Base.metadata.create_all(engine)
