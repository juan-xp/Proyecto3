from sqlalchemy.orm import Session 
from sqlalchemy.exc import SQLAlchemyError
from models import Cliente

class ClienteCRUD:
    @staticmethod
    def crear_cliente(db: Session, nombre: str, email: str, edad: int)