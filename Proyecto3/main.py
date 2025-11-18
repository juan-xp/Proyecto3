from database import get_session, engine, Base
from crud.cliente_crud import ClienteCRUD
from crud.ingrediente_crud import IngredienteCRUD
from crud.menu_crud import MenuCRUD
from crud.pedido_crud import PedidoCRUD

# Crear las tablas en la base de datos
Base.metadata.create_all(bind=engine)

# Función principal para el uso del CRUD
def main():
    # Crear una sesión
    db = next(get_session())

    try:
        # 1. Crear clientes
        print("=== CREANDO CLIENTES ===")
        cliente1 = ClienteCRUD.crear_cliente(db, rut="12345678-9", nombre="Carlos Pérez")
        print(f"Cliente creado: {cliente1.nombre} - RUT: {cliente1.rut}")
        
        # 2. Crear ingredientes
        print("\n=== CREANDO INGREDIENTES ===")
        harina = IngredienteCRUD.crear_ingrediente(db, nombre="Harina", stock=50.0, unidad="kg")
        tomate = IngredienteCRUD.crear_ingrediente(db, nombre="Tomate", stock=30.0, unidad="kg")
        queso = IngredienteCRUD.crear_ingrediente(db, nombre="Queso", stock=20.0, unidad="kg")
        print(f"Ingredientes creados: {harina.nombre}, {tomate.nombre}, {queso.nombre}")
        
        # 3. Crear menús con recetas
        print("\n=== CREANDO MENÚS ===")
        receta_pizza = {
            "Harina": 0.3,
            "Tomate": 0.15,
            "Queso": 0.2
        }
        pizza = MenuCRUD.crear_menu(
            db, 
            nombre="Pizza Napolitana",
            descripcion="Pizza con tomate y queso",
            precio=12000.0,
            categoria="Pizzas",
            disponible=True,
            receta=receta_pizza
        )
        print(f"Menú creado: {pizza.nombre} - ${pizza.precio}")
        
        bebida = MenuCRUD.crear_menu(
            db,
            nombre="Coca Cola",
            descripcion="500ml",
            precio=2000.0,
            categoria="Bebidas",
            disponible=True,
            receta=None
        )
        print(f"Menú creado: {bebida.nombre} - ${bebida.precio}")
        
        # 4. Crear un pedido con múltiples items
        print("\n=== CREANDO PEDIDO ===")
        pedido = PedidoCRUD.crear_pedido(
            db, 
            cliente_id=cliente1.id,
            items=[
                {"menu_id": pizza.id, "cantidad": 2},
                {"menu_id": bebida.id, "cantidad": 1}
            ]
        )
        print(f"Pedido creado: ID {pedido.id}")
        print(f"Items en el pedido:")
        for item in pedido.items:
            print(f"  - {item.cantidad}x {item.menu.nombre} (${item.subtotal})")
        print(f"Total del pedido: ${pedido.total}")
        
        # 5. Listar todos los clientes
        print("\n=== TODOS LOS CLIENTES ===")
        clientes = ClienteCRUD.obtener_todos_clientes(db)
        for c in clientes:
            print(f"- {c.nombre} (RUT: {c.rut})")
        
        # 6. Listar todos los menús disponibles
        print("\n=== MENÚS DISPONIBLES ===")
        menus = MenuCRUD.obtener_menus_disponibles(db)
        for m in menus:
            print(f"- {m.nombre} - ${m.precio} ({m.categoria})")
        
        print("\n¡Operaciones completadas exitosamente!")
        
    except Exception as e:
        print(f"\nError: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    main()