from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# SQLite local
DATABASE_URL = 'sqlite:///./proyecto.db'

# Creacion del engine
engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)

# Sesiones
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base declarativa, los modelos heredan de esta base
Base = declarative_base()


def get_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()