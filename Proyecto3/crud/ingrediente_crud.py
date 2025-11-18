from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from models import Ingrediente
from typing import List, Optional

class IngredienteCRUD:
    @staticmethod
    def crear_ingrediente(db: Session, nombre: str, stock: float, unidad: str) -> Ingrediente:
        try:
            ingrediente = Ingrediente(
                nombre=nombre,
                stock=stock,
                unidad=unidad
            )
            db.add(ingrediente)
            db.commit()
            db.refresh(ingrediente)
            return ingrediente
        except SQLAlchemyError as e:
            db.rollback()
            raise Exception(f"Error al crear ingrediente: {str(e)}")
    
    @staticmethod
    def obtener_ingrediente_por_id(db: Session, ingrediente_id: int) -> Optional[Ingrediente]:
        try:
            return db.query(Ingrediente).filter(Ingrediente.id == ingrediente_id).first()
        except SQLAlchemyError as e:
            raise Exception(f"Error al obtener ingrediente: {str(e)}")
    
    @staticmethod
    def obtener_ingrediente_por_nombre(db: Session, nombre: str) -> Optional[Ingrediente]:
        try:
            return db.query(Ingrediente).filter(Ingrediente.nombre == nombre).first()
        except SQLAlchemyError as e:
            raise Exception(f"Error al buscar ingrediente: {str(e)}")
    
    @staticmethod
    def obtener_todos_ingredientes(db: Session) -> List[Ingrediente]:
        try:
            return db.query(Ingrediente).all()
        except SQLAlchemyError as e:
            raise Exception(f"Error al obtener ingredientes: {str(e)}")
    
    @staticmethod
    def actualizar_ingrediente(db: Session, ingrediente_id: int, nombre: str = None, 
                              stock: float = None, unidad: str = None) -> Optional[Ingrediente]:
        try:
            ingrediente = db.query(Ingrediente).filter(Ingrediente.id == ingrediente_id).first()
            if not ingrediente:
                return None
            
            if nombre is not None:
                ingrediente.nombre = nombre
            if stock is not None:
                ingrediente.stock = stock
            if unidad is not None:
                ingrediente.unidad = unidad
            
            db.commit()
            db.refresh(ingrediente)
            return ingrediente
        except SQLAlchemyError as e:
            db.rollback()
            raise Exception(f"Error al actualizar ingrediente: {str(e)}")
    
    @staticmethod
    def actualizar_stock(db: Session, ingrediente_id: int, cantidad: float) -> Optional[Ingrediente]:
        try:
            ingrediente = db.query(Ingrediente).filter(Ingrediente.id == ingrediente_id).first()
            if not ingrediente:
                return None
            
            ingrediente.stock += cantidad
            
            # Validar que el stock no sea negativo
            if ingrediente.stock < 0:
                db.rollback()
                raise ValueError(f"Stock insuficiente. Stock actual: {ingrediente.stock - cantidad}")
            
            db.commit()
            db.refresh(ingrediente)
            return ingrediente
        except SQLAlchemyError as e:
            db.rollback()
            raise Exception(f"Error al actualizar stock: {str(e)}")
    
    @staticmethod
    def eliminar_ingrediente(db: Session, ingrediente_id: int) -> bool:
        try:
            ingrediente = db.query(Ingrediente).filter(Ingrediente.id == ingrediente_id).first()
            if not ingrediente:
                return False
            
            db.delete(ingrediente)
            db.commit()
            return True
        except SQLAlchemyError as e:
            db.rollback()
            raise Exception(f"Error al eliminar ingrediente: {str(e)}")
    
    @staticmethod
    def verificar_stock_disponible(db: Session, ingrediente_id: int, cantidad_requerida: float) -> bool:
        try:
            ingrediente = db.query(Ingrediente).filter(Ingrediente.id == ingrediente_id).first()
            if not ingrediente:
                return False
            
            return ingrediente.stock >= cantidad_requerida
        except SQLAlchemyError as e:
            raise Exception(f"Error al verificar stock: {str(e)}")