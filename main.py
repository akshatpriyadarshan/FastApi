from fastapi import FastAPI, Depends
from pydantic import BaseModel
from typing import Optional, List
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from sqlalchemy import Boolean, Column, Float, String, Integer

app = FastAPI()

# SqlAlchemy Setup
SQLALCHEMY_DATABASE_URL = 'sqlite+pysqlite:///./db.sqlite3:'
engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=True, future=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

#creating local database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# A SQLAlchemny ORM Place defining the table schema
class DBAddress(Base):
    __tablename__ = 'address'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50))
    address = Column(String, nullable=True)
    lat = Column(Float)
    lng = Column(Float)

Base.metadata.create_all(bind=engine)

# A Pydantic class Address for data validation
class Address(BaseModel):
    name: str
    address: Optional[str] = None
    lat: float
    lng: float

    class Config:
        orm_mode = True

# Methods for interacting with the database
def create_address(db: Session, address: Address):
    db_address = DBAddress(**address.dict())
    db.add(db_address)
    db.commit()
    db.refresh(db_address)

    return db_address

def get_addresses(db: Session):
    return db.query(DBAddress).all()

def get_address_btwn(db: Session, lng_from: float, lng_to: float):
    return db.query(DBAddress).filter(DBAddress.lng >= lng_from).filter(DBAddress.lng <=lng_to).all()


# Routes for interacting with the API
@app.post('/address/', response_model=Address)
def create_address_view(address: Address, db: Session = Depends(get_db)):
    db_address = create_address(db, address)
    return db_address

@app.get('/address/', response_model=List[Address])
def get_addresses_view(db: Session = Depends(get_db)):
    return get_addresses(db)


@app.get('/between_address/')
def get_address_between_view(lng_from: float, lng_to: float, db: Session = Depends(get_db)):
     return get_address_btwn(db, lng_from, lng_to)

@app.get('/')
async def root():
    return {'message': 'Hello World!'}