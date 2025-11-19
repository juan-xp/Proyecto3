from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from models import Ingrediente
from typing import List, Optional
import csv

class IngredienteCRUD:
    @staticmethod
    def crear_ingrediente(db: Session, nombre: str, stock: float, unidad: str) -> Ingrediente:
        try:
            # Validar que el nombre no esté vacío
            if not nombre or not nombre.strip():
                raise ValueError("El nombre del ingrediente no puede estar vacío")
            
            # Validar que el stock sea positivo y mayor que cero
            if stock <= 0:
                raise ValueError("El stock debe ser un número positivo mayor que cero")
            
            # Validar que la unidad no esté vacía
            if not unidad or not unidad.strip():
                raise ValueError("La unidad no puede estar vacía")
            
            # Verificar que el ingrediente no esté duplicado
            ingrediente_existente = db.query(Ingrediente).filter(
                Ingrediente.nombre == nombre.strip()
            ).first()
            if ingrediente_existente:
                raise ValueError(f"El ingrediente '{nombre}' ya existe")
            
            ingrediente = Ingrediente(
                nombre=nombre.strip(),
                stock=stock,
                unidad=unidad.strip()
            )
            db.add(ingrediente)
            db.commit()
            db.refresh(ingrediente)
            return ingrediente
        except (SQLAlchemyError, ValueError) as e:
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
                if not nombre.strip():
                    raise ValueError("El nombre del ingrediente no puede estar vacío")
                # Verificar que no exista otro ingrediente con el mismo nombre
                nombre_existente = db.query(Ingrediente).filter(
                    Ingrediente.nombre == nombre.strip(),
                    Ingrediente.id != ingrediente_id
                ).first()
                if nombre_existente:
                    raise ValueError(f"Ya existe un ingrediente con el nombre '{nombre}'")
                ingrediente.nombre = nombre.strip()
            
            if stock is not None:
                if stock < 0:
                    raise ValueError("El stock no puede ser negativo")
                ingrediente.stock = stock
            
            if unidad is not None:
                if not unidad.strip():
                    raise ValueError("La unidad no puede estar vacía")
                ingrediente.unidad = unidad.strip()
            
            db.commit()
            db.refresh(ingrediente)
            return ingrediente
        except (SQLAlchemyError, ValueError) as e:
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
    
    @staticmethod
    def cargar_desde_csv(db: Session, archivo_csv: str) -> dict:
        """
        Carga ingredientes desde un archivo CSV.
        Retorna un diccionario con estadísticas de la carga.
        """
        resultados = {
            'exitosos': 0,
            'errores': 0,
            'mensajes': []
        }
        
        try:
            with open(archivo_csv, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                
                # Validar que el CSV tenga las columnas necesarias
                columnas_requeridas = {'nombre', 'stock', 'unidad'}
                if not columnas_requeridas.issubset(reader.fieldnames):
                    raise ValueError(f"El CSV debe contener las columnas: {', '.join(columnas_requeridas)}")
                
                for fila_num, fila in enumerate(reader, start=2):
                    try:
                        nombre = fila['nombre'].strip()
                        stock_str = fila['stock'].strip()
                        unidad = fila['unidad'].strip()
                        
                        # Validar datos
                        if not nombre:
                            raise ValueError("Nombre vacío")
                        
                        try:
                            stock = float(stock_str)
                        except ValueError:
                            raise ValueError(f"Stock inválido: '{stock_str}'")
                        
                        if stock <= 0:
                            raise ValueError(f"Stock debe ser positivo: {stock}")
                        
                        if not unidad:
                            raise ValueError("Unidad vacía")
                        
                        # Verificar si el ingrediente ya existe
                        ingrediente_existente = db.query(Ingrediente).filter(
                            Ingrediente.nombre == nombre
                        ).first()
                        
                        if ingrediente_existente:
                            # Actualizar stock del ingrediente existente
                            ingrediente_existente.stock = stock
                            ingrediente_existente.unidad = unidad
                            resultados['mensajes'].append(f"Fila {fila_num}: Actualizado '{nombre}'")
                        else:
                            # Crear nuevo ingrediente
                            nuevo_ingrediente = Ingrediente(
                                nombre=nombre,
                                stock=stock,
                                unidad=unidad
                            )
                            db.add(nuevo_ingrediente)
                            resultados['mensajes'].append(f"Fila {fila_num}: Creado '{nombre}'")
                        
                        resultados['exitosos'] += 1
                        
                    except Exception as e:
                        resultados['errores'] += 1
                        resultados['mensajes'].append(f"Fila {fila_num}: Error - {str(e)}")
                        continue
                
                # Confirmar todos los cambios al final
                db.commit()
                
        except FileNotFoundError:
            raise Exception(f"Archivo no encontrado: {archivo_csv}")
        except Exception as e:
            db.rollback()
            raise Exception(f"Error al cargar CSV: {str(e)}")
        
        return resultados