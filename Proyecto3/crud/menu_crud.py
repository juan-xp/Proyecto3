from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from models import Menu
from typing import Optional, List, Dict

class MenuCRUD:
    @staticmethod
    def crear_menu(db: Session, nombre: str, descripcion: str, precio: float, 
                   categoria: str = None, disponible: bool = True, 
                   receta: Dict[str, float] = None) -> Optional[Menu]:
        try:
            nuevo_menu = Menu(
                nombre=nombre,
                descripcion=descripcion,
                precio=precio,
                categoria=categoria,
                disponible=1 if disponible else 0,
                receta=receta  # Se guarda automáticamente como JSON
            )
            db.add(nuevo_menu)
            db.commit()
            db.refresh(nuevo_menu)
            return nuevo_menu
        except SQLAlchemyError as e:
            db.rollback()
            raise Exception(f"Error al crear menú: {str(e)}")
    
    @staticmethod
    def obtener_menu_por_id(db: Session, menu_id: int) -> Optional[Menu]:
        try:
            return db.query(Menu).filter(Menu.id == menu_id).first()
        except SQLAlchemyError as e:
            raise Exception(f"Error al obtener menú: {str(e)}")
    
    @staticmethod
    def obtener_todos_menus(db: Session) -> List[Menu]:
        try:
            return db.query(Menu).all()
        except SQLAlchemyError as e:
            raise Exception(f"Error al obtener menús: {str(e)}")
    
    @staticmethod
    def obtener_menus_disponibles(db: Session) -> List[Menu]:
        try:
            return db.query(Menu).filter(Menu.disponible == 1).all()
        except SQLAlchemyError as e:
            raise Exception(f"Error al obtener menús disponibles: {str(e)}")
    
    @staticmethod
    def obtener_menus_por_categoria(db: Session, categoria: str) -> List[Menu]:
        try:
            return db.query(Menu).filter(Menu.categoria == categoria).all()
        except SQLAlchemyError as e:
            raise Exception(f"Error al obtener menús por categoría: {str(e)}")
    
    @staticmethod
    def actualizar_menu(db: Session, menu_id: int, nombre: str = None, 
                       descripcion: str = None, precio: float = None,
                       categoria: str = None, disponible: bool = None,
                       receta: Dict[str, float] = None) -> Optional[Menu]:
        try:
            menu = db.query(Menu).filter(Menu.id == menu_id).first()
            if not menu:
                return None
            
            if nombre is not None:
                menu.nombre = nombre
            if descripcion is not None:
                menu.descripcion = descripcion
            if precio is not None:
                menu.precio = precio
            if categoria is not None:
                menu.categoria = categoria
            if disponible is not None:
                menu.disponible = 1 if disponible else 0
            if receta is not None:
                menu.receta = receta
            
            db.commit()
            db.refresh(menu)
            return menu
        except SQLAlchemyError as e:
            db.rollback()
            raise Exception(f"Error al actualizar menú: {str(e)}")
    
    @staticmethod
    def cambiar_disponibilidad(db: Session, menu_id: int, disponible: bool) -> Optional[Menu]:
        try:
            menu = db.query(Menu).filter(Menu.id == menu_id).first()
            if not menu:
                return None
            
            menu.disponible = 1 if disponible else 0
            db.commit()
            db.refresh(menu)
            return menu
        except SQLAlchemyError as e:
            db.rollback()
            raise Exception(f"Error al cambiar disponibilidad: {str(e)}")
    
    @staticmethod
    def eliminar_menu(db: Session, menu_id: int) -> bool:
        try:
            menu = db.query(Menu).filter(Menu.id == menu_id).first()
            if not menu:
                return False
            
            db.delete(menu)
            db.commit()
            return True
        except SQLAlchemyError as e:
            db.rollback()
            raise Exception(f"Error al eliminar menú: {str(e)}")