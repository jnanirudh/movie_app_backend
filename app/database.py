from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings

# The connection pool — like HikariCP in Spring Boot
engine = create_engine(settings.DATABASE_URL)

# Each request gets one session from this factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# All your models will inherit from this — like JPA's @Entity base
Base = declarative_base()