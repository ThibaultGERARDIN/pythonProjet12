from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_USER = os.getenv("DATABASE_USER")
DATABASE_PWD = os.getenv("DATABASE_PWD")


engine = create_engine(f"mysql+pymysql://{DATABASE_USER}:{DATABASE_PWD}@localhost:3306/epic_crm")

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
