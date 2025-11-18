from sqlalchemy.orm import Session 
from sqlalchemy.exc import SQLAlchemyError
from models import Cliente
from typing import Optional, List

class ClienteCRUD:
    @staticmethod
    def crear_cliente(db: Session, rut: str, nombre: str) -> Optional[Cliente]:
        """Crea un nuevo cliente"""
        try:
            # Verificar si el RUT ya existe
            cliente_existente = db.query(Cliente).filter(Cliente.rut == rut).first()
            if cliente_existente:
                raise ValueError(f"El cliente con RUT '{rut}' ya existe")
            
            nuevo_cliente = Cliente(rut=rut, nombre=nombre)
            db.add(nuevo_cliente)
            db.commit()
            db.refresh(nuevo_cliente)
            return nuevo_cliente
        except (SQLAlchemyError, ValueError) as e:
            db.rollback()
            raise Exception(f"Error al crear cliente: {str(e)}")
    
    @staticmethod
    def obtener_cliente_por_id(db: Session, cliente_id: int) -> Optional[Cliente]:
        """Obtiene un cliente por su ID"""
        try:
            return db.query(Cliente).filter(Cliente.id == cliente_id).first()
        except SQLAlchemyError as e:
            raise Exception(f"Error al obtener cliente: {str(e)}")
    
    @staticmethod
    def obtener_cliente_por_rut(db: Session, rut: str) -> Optional[Cliente]:
        """Obtiene un cliente por su RUT"""
        try:
            return db.query(Cliente).filter(Cliente.rut == rut).first()
        except SQLAlchemyError as e:
            raise Exception(f"Error al buscar cliente: {str(e)}")
    
    @staticmethod
    def obtener_todos_clientes(db: Session) -> List[Cliente]:
        """Obtiene todos los clientes"""
        try:
            return db.query(Cliente).all()
        except SQLAlchemyError as e:
            raise Exception(f"Error al obtener clientes: {str(e)}")
    
    @staticmethod
    def actualizar_cliente(db: Session, cliente_id: int, rut: str = None, 
                          nombre: str = None) -> Optional[Cliente]:
        """Actualiza los datos de un cliente"""
        try:
            cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
            if not cliente:
                return None
            
            if rut is not None:
                # Verificar que el nuevo RUT no esté en uso
                rut_existente = db.query(Cliente).filter(
                    Cliente.rut == rut,
                    Cliente.id != cliente_id
                ).first()
                if rut_existente:
                    raise ValueError(f"El RUT '{rut}' ya está en uso")
                cliente.rut = rut
            
            if nombre is not None:
                cliente.nombre = nombre
            
            db.commit()
            db.refresh(cliente)
            return cliente
        except (SQLAlchemyError, ValueError) as e:
            db.rollback()
            raise Exception(f"Error al actualizar cliente: {str(e)}")
    
    @staticmethod
    def eliminar_cliente(db: Session, cliente_id: int) -> bool:
        """Elimina un cliente por su ID"""
        try:
            cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
            if not cliente:
                return False
            
            db.delete(cliente)
            db.commit()
            return True
        except SQLAlchemyError as e:
            db.rollback()
            raise Exception(f"Error al eliminar cliente: {str(e)}")
