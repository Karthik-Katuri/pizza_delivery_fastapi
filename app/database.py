from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = "postgresql://postgres:abgk1234@localhost/pizza_delivery"

engine = create_engine(DATABASE_URL, echo=True)

Session = sessionmaker(bind=engine, autoflush=False, autocommit=False)

Base = declarative_base()
