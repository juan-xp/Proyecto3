from sqlalchemy import Column, String, Float, Integer, ForeignKey, JSON, DateTime
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

class Cliente(Base):
    __tablename__ = "Clientes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    rut = Column(String, unique=True, index=True, nullable=False)
    nombre = Column(String, nullable=False)
    
    # Relaciones
    pedidos = relationship("Pedido", back_populates="cliente", cascade="all, delete-orphan")


class Ingrediente(Base):
    __tablename__ = "Ingredientes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String, nullable=False, unique=True)
    stock = Column(Float, default=0.0)
    unidad = Column(String, nullable=False)  # Ej: "kg", "litros", "unidades"


class Menu(Base):
    __tablename__ = "Menus"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String, nullable=False)
    descripcion = Column(String, nullable=True)
    precio = Column(Float, nullable=False)
    categoria = Column(String, nullable=True)  # Ej: "Pizzas", "Bebidas", "Postres"
    disponible = Column(Integer, default=1)  # 1=disponible, 0=no disponible
    receta = Column(JSON, nullable=True)  # Ej: {"harina": 0.5, "tomate": 0.2}
    
    # Relaciones
    items = relationship("ItemPedido", back_populates="menu", cascade="all, delete-orphan")


class Pedido(Base):
    __tablename__ = "Pedidos"

    id = Column(Integer, primary_key=True, autoincrement=True)
    fecha = Column(DateTime, default=datetime.now)
    estado = Column(String, default="Pendiente")  # Pendiente, En preparación, Completado
    
    # Claves foráneas
    cliente_id = Column(Integer, ForeignKey("Clientes.id"), nullable=False)
    
    # Relaciones
    cliente = relationship("Cliente", back_populates="pedidos")
    items = relationship("ItemPedido", back_populates="pedido", cascade="all, delete-orphan")
    
    @property
    def total(self) -> float:
        return sum(item.subtotal for item in self.items)


class ItemPedido(Base):
    __tablename__ = "ItemPedidos"

    id = Column(Integer, primary_key=True, autoincrement=True)
    cantidad = Column(Integer, nullable=False)

    # Claves foráneas
    pedido_id = Column(Integer, ForeignKey("Pedidos.id"), nullable=False)
    menu_id = Column(Integer, ForeignKey("Menus.id"), nullable=False)
    
    # Relaciones
    pedido = relationship("Pedido", back_populates="items")
    menu = relationship("Menu", back_populates="items")

    @property
    def subtotal(self) -> float:
        if self.menu:
            return self.menu.precio * self.cantidad
        return 0.0
