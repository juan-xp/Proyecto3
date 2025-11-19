import customtkinter as ctk
from tkinter import messagebox, ttk, filedialog
import json
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from database import get_session, engine, Base
from crud.cliente_crud import ClienteCRUD
from crud.ingrediente_crud import IngredienteCRUD
from crud.menu_crud import MenuCRUD
from crud.pedido_crud import PedidoCRUD
from graficos import GraficosEstadisticos

# Configuración de la ventana principal
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

# Crear las tablas en la base de datos
Base.metadata.create_all(bind=engine)
class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Sistema de Gestión - Restaurante")
        self.geometry("900x700")

        # Crear el Tabview (pestañas)
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(pady=20, padx=20, fill="both", expand=True)

        # Pestañas
        self.tab_clientes = self.tabview.add("Clientes")
        self.crear_formulario_cliente(self.tab_clientes)

        self.tab_ingredientes = self.tabview.add("Ingredientes")
        self.crear_formulario_ingrediente(self.tab_ingredientes)

        self.tab_menus = self.tabview.add("Menús")
        self.crear_formulario_menu(self.tab_menus)

        self.tab_pedidos = self.tabview.add("Pedidos")
        self.crear_formulario_pedido(self.tab_pedidos)
        
        self.tab_graficos = self.tabview.add("Gráficos")
        self.crear_formulario_graficos(self.tab_graficos)
# Clientes
    def crear_formulario_cliente(self, parent):
        frame_superior = ctk.CTkFrame(parent)
        frame_superior.pack(pady=10, padx=10, fill="x")

        ctk.CTkLabel(frame_superior, text="RUT").grid(row=0, column=0, pady=10, padx=10)
        self.entry_rut = ctk.CTkEntry(frame_superior, width=150)
        self.entry_rut.grid(row=0, column=1, pady=10, padx=10)

        ctk.CTkLabel(frame_superior, text="Nombre").grid(row=0, column=2, pady=10, padx=10)
        self.entry_nombre_cliente = ctk.CTkEntry(frame_superior, width=200)
        self.entry_nombre_cliente.grid(row=0, column=3, pady=10, padx=10)
        
        ctk.CTkLabel(frame_superior, text="Correo").grid(row=0, column=4, pady=10, padx=10)
        self.entry_correo_cliente = ctk.CTkEntry(frame_superior, width=200)
        self.entry_correo_cliente.grid(row=0, column=5, pady=10, padx=10)

        ctk.CTkButton(frame_superior, text="Crear", command=self.crear_cliente).grid(row=1, column=0, pady=10, padx=5)
        ctk.CTkButton(frame_superior, text="Actualizar", command=self.actualizar_cliente).grid(row=1, column=1, pady=10, padx=5)
        ctk.CTkButton(frame_superior, text="Eliminar", command=self.eliminar_cliente).grid(row=1, column=2, pady=10, padx=5)
        ctk.CTkButton(frame_superior, text="Refrescar", command=self.cargar_clientes).grid(row=1, column=3, pady=10, padx=5)

        frame_inferior = ctk.CTkFrame(parent)
        frame_inferior.pack(pady=10, padx=10, fill="both", expand=True)

        self.treeview_clientes = ttk.Treeview(frame_inferior, columns=("ID", "RUT", "Nombre", "Correo"), show="headings")
        self.treeview_clientes.heading("ID", text="ID")
        self.treeview_clientes.heading("RUT", text="RUT")
        self.treeview_clientes.heading("Nombre", text="Nombre")
        self.treeview_clientes.heading("Correo", text="Correo")
        self.treeview_clientes.column("ID", width=50)
        self.treeview_clientes.column("Correo", width=200)
        self.treeview_clientes.pack(pady=10, padx=10, fill="both", expand=True)

        self.cargar_clientes()

        self.cargar_clientes()

    def cargar_clientes(self):
        db = next(get_session())
        self.treeview_clientes.delete(*self.treeview_clientes.get_children())
        try:
            clientes = ClienteCRUD.obtener_todos_clientes(db)
            for cliente in clientes:
                self.treeview_clientes.insert("", "end", values=(cliente.id, cliente.rut, cliente.nombre, cliente.correo or ""))
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar clientes: {e}")
        finally:
            db.close()

    def crear_cliente(self):
        rut = self.entry_rut.get().strip()
        nombre = self.entry_nombre_cliente.get().strip()
        correo = self.entry_correo_cliente.get().strip()
        if rut and nombre:
            db = next(get_session())
            try:
                ClienteCRUD.crear_cliente(db, rut, nombre, correo if correo else None)
                messagebox.showinfo("Éxito", "Cliente creado correctamente.")
                self.cargar_clientes()
                self.entry_rut.delete(0, 'end')
                self.entry_nombre_cliente.delete(0, 'end')
                self.entry_correo_cliente.delete(0, 'end')
            except Exception as e:
                messagebox.showerror("Error", str(e))
            finally:
                db.close()
        else:
            messagebox.showwarning("Campos Vacíos", "Por favor, ingrese RUT y nombre.")

    def actualizar_cliente(self):
        selected = self.treeview_clientes.selection()
        if not selected:
            messagebox.showwarning("Selección", "Seleccione un cliente.")
            return
        cliente_id = self.treeview_clientes.item(selected)["values"][0]
        rut = self.entry_rut.get().strip()
        nombre = self.entry_nombre_cliente.get().strip()
        correo = self.entry_correo_cliente.get().strip()
        
        db = next(get_session())
        try:
            ClienteCRUD.actualizar_cliente(
                db, cliente_id, 
                rut if rut else None, 
                nombre if nombre else None,
                correo if correo else None
            )
            messagebox.showinfo("Éxito", "Cliente actualizado.")
            self.cargar_clientes()
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            db.close()

    def eliminar_cliente(self):
        selected = self.treeview_clientes.selection()
        if not selected:
            messagebox.showwarning("Selección", "Seleccione un cliente.")
            return
        cliente_id = self.treeview_clientes.item(selected)["values"][0]
        db = next(get_session())
        try:
            ClienteCRUD.eliminar_cliente(db, cliente_id)
            messagebox.showinfo("Éxito", "Cliente eliminado.")
            self.cargar_clientes()
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            db.close()
# Ingredientes
    def crear_formulario_ingrediente(self, parent):
        frame_superior = ctk.CTkFrame(parent)
        frame_superior.pack(pady=10, padx=10, fill="x")

        ctk.CTkLabel(frame_superior, text="Nombre").grid(row=0, column=0, pady=10, padx=10)
        self.entry_nombre_ingrediente = ctk.CTkEntry(frame_superior, width=150)
        self.entry_nombre_ingrediente.grid(row=0, column=1, pady=10, padx=10)

        ctk.CTkLabel(frame_superior, text="Stock").grid(row=0, column=2, pady=10, padx=10)
        self.entry_stock = ctk.CTkEntry(frame_superior, width=100)
        self.entry_stock.grid(row=0, column=3, pady=10, padx=10)

        ctk.CTkLabel(frame_superior, text="Unidad").grid(row=0, column=4, pady=10, padx=10)
        self.entry_unidad = ctk.CTkEntry(frame_superior, width=80)
        self.entry_unidad.grid(row=0, column=5, pady=10, padx=10)

        ctk.CTkButton(frame_superior, text="Crear", command=self.crear_ingrediente).grid(row=1, column=0, pady=10, padx=5)
        ctk.CTkButton(frame_superior, text="Actualizar", command=self.actualizar_ingrediente).grid(row=1, column=1, pady=10, padx=5)
        ctk.CTkButton(frame_superior, text="Eliminar", command=self.eliminar_ingrediente).grid(row=1, column=2, pady=10, padx=5)
        ctk.CTkButton(frame_superior, text="Refrescar", command=self.cargar_ingredientes).grid(row=1, column=3, pady=10, padx=5)
        ctk.CTkButton(frame_superior, text="Cargar CSV", command=self.cargar_csv_ingredientes).grid(row=1, column=4, pady=10, padx=5)

        frame_inferior = ctk.CTkFrame(parent)
        frame_inferior.pack(pady=10, padx=10, fill="both", expand=True)

        self.treeview_ingredientes = ttk.Treeview(frame_inferior, columns=("ID", "Nombre", "Stock", "Unidad"), show="headings")
        self.treeview_ingredientes.heading("ID", text="ID")
        self.treeview_ingredientes.heading("Nombre", text="Nombre")
        self.treeview_ingredientes.heading("Stock", text="Stock")
        self.treeview_ingredientes.heading("Unidad", text="Unidad")
        self.treeview_ingredientes.column("ID", width=50)
        self.treeview_ingredientes.pack(pady=10, padx=10, fill="both", expand=True)

        self.cargar_ingredientes()

    def cargar_ingredientes(self):
        db = next(get_session())
        self.treeview_ingredientes.delete(*self.treeview_ingredientes.get_children())
        try:
            ingredientes = IngredienteCRUD.obtener_todos_ingredientes(db)
            for ing in ingredientes:
                self.treeview_ingredientes.insert("", "end", values=(ing.id, ing.nombre, ing.stock, ing.unidad))
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar ingredientes: {e}")
        finally:
            db.close()

    def crear_ingrediente(self):
        nombre = self.entry_nombre_ingrediente.get().strip()
        stock = self.entry_stock.get().strip()
        unidad = self.entry_unidad.get().strip()
        if nombre and stock and unidad:
            db = next(get_session())
            try:
                IngredienteCRUD.crear_ingrediente(db, nombre, float(stock), unidad)
                messagebox.showinfo("Éxito", "Ingrediente creado.")
                self.cargar_ingredientes()
                self.entry_nombre_ingrediente.delete(0, 'end')
                self.entry_stock.delete(0, 'end')
                self.entry_unidad.delete(0, 'end')
            except Exception as e:
                messagebox.showerror("Error", str(e))
            finally:
                db.close()
        else:
            messagebox.showwarning("Campos Vacíos", "Complete todos los campos.")

    def actualizar_ingrediente(self):
        selected = self.treeview_ingredientes.selection()
        if not selected:
            messagebox.showwarning("Selección", "Seleccione un ingrediente.")
            return
        ing_id = self.treeview_ingredientes.item(selected)["values"][0]
        nombre = self.entry_nombre_ingrediente.get().strip()
        stock = self.entry_stock.get().strip()
        unidad = self.entry_unidad.get().strip()
        
        db = next(get_session())
        try:
            IngredienteCRUD.actualizar_ingrediente(
                db, ing_id, 
                nombre if nombre else None, 
                float(stock) if stock else None, 
                unidad if unidad else None
            )
            messagebox.showinfo("Éxito", "Ingrediente actualizado.")
            self.cargar_ingredientes()
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            db.close()

    def eliminar_ingrediente(self):
        selected = self.treeview_ingredientes.selection()
        if not selected:
            messagebox.showwarning("Selección", "Seleccione un ingrediente.")
            return
        ing_id = self.treeview_ingredientes.item(selected)["values"][0]
        db = next(get_session())
        try:
            IngredienteCRUD.eliminar_ingrediente(db, ing_id)
            messagebox.showinfo("Éxito", "Ingrediente eliminado.")
            self.cargar_ingredientes()
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            db.close()

    # Menús
    def crear_formulario_menu(self, parent):
        frame_superior = ctk.CTkFrame(parent)
        frame_superior.pack(pady=10, padx=10, fill="x")

        ctk.CTkLabel(frame_superior, text="Nombre").grid(row=0, column=0, pady=5, padx=5)
        self.entry_nombre_menu = ctk.CTkEntry(frame_superior, width=150)
        self.entry_nombre_menu.grid(row=0, column=1, pady=5, padx=5)

        ctk.CTkLabel(frame_superior, text="Precio").grid(row=0, column=2, pady=5, padx=5)
        self.entry_precio = ctk.CTkEntry(frame_superior, width=100)
        self.entry_precio.grid(row=0, column=3, pady=5, padx=5)

        ctk.CTkLabel(frame_superior, text="Categoría").grid(row=1, column=0, pady=5, padx=5)
        self.entry_categoria = ctk.CTkEntry(frame_superior, width=150)
        self.entry_categoria.grid(row=1, column=1, pady=5, padx=5)

        ctk.CTkLabel(frame_superior, text="Descripción").grid(row=1, column=2, pady=5, padx=5)
        self.entry_descripcion_menu = ctk.CTkEntry(frame_superior, width=200)
        self.entry_descripcion_menu.grid(row=1, column=3, pady=5, padx=5)

        ctk.CTkLabel(frame_superior, text="Receta (JSON)").grid(row=2, column=0, pady=5, padx=5)
        self.entry_receta = ctk.CTkEntry(frame_superior, width=400)
        self.entry_receta.grid(row=2, column=1, columnspan=3, pady=5, padx=5)

        ctk.CTkButton(frame_superior, text="Crear", command=self.crear_menu).grid(row=3, column=0, pady=10, padx=5)
        ctk.CTkButton(frame_superior, text="Eliminar", command=self.eliminar_menu).grid(row=3, column=1, pady=10, padx=5)
        ctk.CTkButton(frame_superior, text="Refrescar", command=self.cargar_menus).grid(row=3, column=2, pady=10, padx=5)

        frame_inferior = ctk.CTkFrame(parent)
        frame_inferior.pack(pady=10, padx=10, fill="both", expand=True)

        self.treeview_menus = ttk.Treeview(frame_inferior, columns=("ID", "Nombre", "Precio", "Categoría", "Disponible"), show="headings")
        self.treeview_menus.heading("ID", text="ID")
        self.treeview_menus.heading("Nombre", text="Nombre")
        self.treeview_menus.heading("Precio", text="Precio")
        self.treeview_menus.heading("Categoría", text="Categoría")
        self.treeview_menus.heading("Disponible", text="Disponible")
        self.treeview_menus.column("ID", width=50)
        self.treeview_menus.pack(pady=10, padx=10, fill="both", expand=True)

        self.cargar_menus()

    def cargar_menus(self):
        db = next(get_session())
        self.treeview_menus.delete(*self.treeview_menus.get_children())
        try:
            menus = MenuCRUD.obtener_todos_menus(db)
            for menu in menus:
                disp = "Sí" if menu.disponible else "No"
                self.treeview_menus.insert("", "end", values=(menu.id, menu.nombre, menu.precio, menu.categoria, disp))
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar menús: {e}")
        finally:
            db.close()

    def crear_menu(self):
        nombre = self.entry_nombre_menu.get().strip()
        precio = self.entry_precio.get().strip()
        categoria = self.entry_categoria.get().strip()
        descripcion = self.entry_descripcion_menu.get().strip()
        receta_str = self.entry_receta.get().strip()
        
        if nombre and precio:
            db = next(get_session())
            try:
                receta = None
                if receta_str:
                    receta = json.loads(receta_str)  # Convierte string JSON a dict
                
                MenuCRUD.crear_menu(db, nombre, descripcion, float(precio), categoria, True, receta)
                messagebox.showinfo("Éxito", "Menú creado.")
                self.cargar_menus()
                self.entry_nombre_menu.delete(0, 'end')
                self.entry_precio.delete(0, 'end')
                self.entry_categoria.delete(0, 'end')
                self.entry_descripcion_menu.delete(0, 'end')
                self.entry_receta.delete(0, 'end')
            except json.JSONDecodeError:
                messagebox.showerror("Error", "Formato de receta inválido. Use JSON: {\"ingrediente\": cantidad}")
            except Exception as e:
                messagebox.showerror("Error", str(e))
            finally:
                db.close()
        else:
            messagebox.showwarning("Campos Vacíos", "Ingrese nombre y precio.")

    def eliminar_menu(self):
        selected = self.treeview_menus.selection()
        if not selected:
            messagebox.showwarning("Selección", "Seleccione un menú.")
            return
        menu_id = self.treeview_menus.item(selected)["values"][0]
        db = next(get_session())
        try:
            MenuCRUD.eliminar_menu(db, menu_id)
            messagebox.showinfo("Éxito", "Menú eliminado.")
            self.cargar_menus()
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            db.close()

    # Pedidos
    def crear_formulario_pedido(self, parent):
        frame_superior = ctk.CTkFrame(parent)
        frame_superior.pack(pady=10, padx=10, fill="x")

        ctk.CTkLabel(frame_superior, text="Cliente ID").grid(row=0, column=0, pady=5, padx=5)
        self.entry_cliente_id = ctk.CTkEntry(frame_superior, width=80)
        self.entry_cliente_id.grid(row=0, column=1, pady=5, padx=5)

        ctk.CTkLabel(frame_superior, text="Items (JSON)").grid(row=0, column=2, pady=5, padx=5)
        self.entry_items = ctk.CTkEntry(frame_superior, width=300)
        self.entry_items.grid(row=0, column=3, pady=5, padx=5)
        
        ctk.CTkLabel(frame_superior, text='Ejemplo: [{"menu_id": 1, "cantidad": 2}]', font=("Arial", 9)).grid(row=1, column=2, columnspan=2, pady=0)

        ctk.CTkButton(frame_superior, text="Crear Pedido", command=self.crear_pedido).grid(row=2, column=0, pady=10, padx=5)
        ctk.CTkButton(frame_superior, text="Eliminar", command=self.eliminar_pedido).grid(row=2, column=1, pady=10, padx=5)
        ctk.CTkButton(frame_superior, text="Refrescar", command=self.cargar_pedidos).grid(row=2, column=2, pady=10, padx=5)

        frame_inferior = ctk.CTkFrame(parent)
        frame_inferior.pack(pady=10, padx=10, fill="both", expand=True)

        self.treeview_pedidos = ttk.Treeview(frame_inferior, columns=("ID", "Cliente", "Fecha", "Total", "Items"), show="headings")
        self.treeview_pedidos.heading("ID", text="ID")
        self.treeview_pedidos.heading("Cliente", text="Cliente")
        self.treeview_pedidos.heading("Fecha", text="Fecha")
        self.treeview_pedidos.heading("Total", text="Total")
        self.treeview_pedidos.heading("Items", text="Items")
        self.treeview_pedidos.column("ID", width=50)
        self.treeview_pedidos.pack(pady=10, padx=10, fill="both", expand=True)

        self.cargar_pedidos()

    def cargar_pedidos(self):
        db = next(get_session())
        self.treeview_pedidos.delete(*self.treeview_pedidos.get_children())
        try:
            pedidos = PedidoCRUD.obtener_todos_pedidos(db)
            for pedido in pedidos:
                items_text = f"{len(pedido.items)} items"
                self.treeview_pedidos.insert("", "end", values=(
                    pedido.id, 
                    pedido.cliente.nombre, 
                    pedido.fecha.strftime("%Y-%m-%d %H:%M"), 
                    f"${pedido.total}",
                    items_text
                ))
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar pedidos: {e}")
        finally:
            db.close()

    def crear_pedido(self):
        cliente_id = self.entry_cliente_id.get().strip()
        items_str = self.entry_items.get().strip()
        
        if cliente_id and items_str:
            db = next(get_session())
            try:
                items = json.loads(items_str)
                PedidoCRUD.crear_pedido(db, int(cliente_id), items)
                messagebox.showinfo("Éxito", "Pedido creado.")
                self.cargar_pedidos()
                self.entry_cliente_id.delete(0, 'end')
                self.entry_items.delete(0, 'end')
            except json.JSONDecodeError:
                messagebox.showerror("Error", "Formato de items inválido.")
            except Exception as e:
                messagebox.showerror("Error", str(e))
            finally:
                db.close()
        else:
            messagebox.showwarning("Campos Vacíos", "Complete los campos.")

    def eliminar_pedido(self):
        selected = self.treeview_pedidos.selection()
        if not selected:
            messagebox.showwarning("Selección", "Seleccione un pedido.")
            return
        pedido_id = self.treeview_pedidos.item(selected)["values"][0]
        db = next(get_session())
        try:
            PedidoCRUD.eliminar_pedido(db, pedido_id)
            messagebox.showinfo("Éxito", "Pedido eliminado.")
            self.cargar_pedidos()
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            db.close()
    
    # Cargar CSV de ingredientes
    def cargar_csv_ingredientes(self):
        """Carga ingredientes desde un archivo CSV"""
        archivo = filedialog.askopenfilename(
            title="Seleccionar archivo CSV",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if not archivo:
            return
        
        db = next(get_session())
        try:
            resultados = IngredienteCRUD.cargar_desde_csv(db, archivo)
            
            # Mostrar resumen de la carga
            mensaje = f"Carga completada:\n"
            mensaje += f"✓ Exitosos: {resultados['exitosos']}\n"
            mensaje += f"✗ Errores: {resultados['errores']}\n\n"
            
            if resultados['mensajes']:
                mensaje += "Detalles:\n"
                # Mostrar solo los primeros 10 mensajes
                for msg in resultados['mensajes'][:10]:
                    mensaje += f"• {msg}\n"
                if len(resultados['mensajes']) > 10:
                    mensaje += f"... y {len(resultados['mensajes']) - 10} más"
            
            messagebox.showinfo("Carga CSV", mensaje)
            self.cargar_ingredientes()
            
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            db.close()

    # Gráficos
    def crear_formulario_graficos(self, parent):
        """Crea la interfaz para mostrar gráficos estadísticos"""
        # Frame superior con controles
        frame_controles = ctk.CTkFrame(parent)
        frame_controles.pack(pady=10, padx=10, fill="x")
        
        ctk.CTkLabel(frame_controles, text="Seleccionar Gráfico:", font=("Arial", 14, "bold")).grid(row=0, column=0, pady=10, padx=10)
        
        self.combo_graficos = ctk.CTkComboBox(
            frame_controles,
            values=["Ventas por Fecha", "Menús Más Vendidos", "Uso de Ingredientes"],
            width=200
        )
        self.combo_graficos.set("Ventas por Fecha")
        self.combo_graficos.grid(row=0, column=1, pady=10, padx=10)
        
        # ComboBox para periodo (solo visible para ventas)
        ctk.CTkLabel(frame_controles, text="Periodo:").grid(row=0, column=2, pady=10, padx=10)
        self.combo_periodo = ctk.CTkComboBox(
            frame_controles,
            values=["diario", "semanal", "mensual", "anual"],
            width=120
        )
        self.combo_periodo.set("diario")
        self.combo_periodo.grid(row=0, column=3, pady=10, padx=10)
        
        ctk.CTkButton(
            frame_controles,
            text="Generar Gráfico",
            command=self.generar_grafico
        ).grid(row=0, column=4, pady=10, padx=10)
        
        # Frame para el gráfico
        self.frame_grafico = ctk.CTkFrame(parent)
        self.frame_grafico.pack(pady=10, padx=10, fill="both", expand=True)
        
        # Label de información
        self.label_info_grafico = ctk.CTkLabel(
            self.frame_grafico,
            text="Seleccione un tipo de gráfico y presione 'Generar Gráfico'",
            font=("Arial", 12)
        )
        self.label_info_grafico.pack(pady=50)
    
    def generar_grafico(self):
        """Genera el gráfico seleccionado"""
        # Limpiar frame de gráfico
        for widget in self.frame_grafico.winfo_children():
            widget.destroy()
        
        tipo_grafico = self.combo_graficos.get()
        db = next(get_session())
        
        try:
            fig = None
            error = None
            
            if tipo_grafico == "Ventas por Fecha":
                periodo = self.combo_periodo.get()
                fig, error = GraficosEstadisticos.graficar_ventas_por_fecha(db, periodo)
            elif tipo_grafico == "Menús Más Vendidos":
                fig, error = GraficosEstadisticos.graficar_distribucion_menus(db)
            elif tipo_grafico == "Uso de Ingredientes":
                fig, error = GraficosEstadisticos.graficar_uso_ingredientes(db)
            
            if error:
                # Mostrar mensaje de error
                label_error = ctk.CTkLabel(
                    self.frame_grafico,
                    text=error,
                    font=("Arial", 12),
                    text_color="red"
                )
                label_error.pack(pady=50)
            elif fig:
                # Mostrar gráfico
                canvas = FigureCanvasTkAgg(fig, master=self.frame_grafico)
                canvas.draw()
                canvas.get_tk_widget().pack(fill="both", expand=True)
            else:
                label_error = ctk.CTkLabel(
                    self.frame_grafico,
                    text="No se pudo generar el gráfico",
                    font=("Arial", 12)
                )
                label_error.pack(pady=50)
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al generar gráfico: {str(e)}")
        finally:
            db.close()

if __name__ == "__main__":
    app = App()
    app.mainloop()