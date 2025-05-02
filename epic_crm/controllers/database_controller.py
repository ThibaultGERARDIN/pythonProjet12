from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv
import sentry_sdk

load_dotenv()

DATABASE_USER = os.getenv("DATABASE_USER")
DATABASE_PWD = os.getenv("DATABASE_PWD")


engine = create_engine(f"mysql+pymysql://{DATABASE_USER}:{DATABASE_PWD}@localhost:3306/epic_crm")

sentry_sdk.init(dsn=SENTRY_KEY)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
