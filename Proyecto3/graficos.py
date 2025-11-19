import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from sqlalchemy.orm import Session
from models import Pedido, ItemPedido, Menu, Ingrediente
from datetime import datetime, timedelta
from typing import List, Dict, Tuple
from functools import reduce

class GraficosEstadisticos:
    
    @staticmethod
    def validar_datos_disponibles(datos: list, mensaje_tipo: str = "datos") -> bool:
        """Valida que existan datos suficientes para generar gráficos"""
        if not datos or len(datos) == 0:
            return False
        return True
    
    @staticmethod
    def obtener_ventas_por_fecha(db: Session, periodo: str = "diario") -> Dict[str, float]:
        """
        Obtiene las ventas agrupadas por fecha según el periodo especificado.
        Periodos: 'diario', 'semanal', 'mensual', 'anual'
        """
        try:
            pedidos = db.query(Pedido).all()
            
            if not GraficosEstadisticos.validar_datos_disponibles(pedidos):
                return {}
            
            ventas = {}
            
            for pedido in pedidos:
                if not pedido.fecha:
                    continue
                    
                try:
                    fecha = pedido.fecha
                    total = pedido.total
                    
                    if periodo == "diario":
                        clave = fecha.strftime("%Y-%m-%d")
                    elif periodo == "semanal":
                        # Obtener número de semana
                        clave = f"{fecha.year}-S{fecha.isocalendar()[1]}"
                    elif periodo == "mensual":
                        clave = fecha.strftime("%Y-%m")
                    elif periodo == "anual":
                        clave = str(fecha.year)
                    else:
                        clave = fecha.strftime("%Y-%m-%d")
                    
                    ventas[clave] = ventas.get(clave, 0.0) + total
                    
                except (ValueError, AttributeError) as e:
                    # Manejar errores de formato en fechas
                    continue
            
            return dict(sorted(ventas.items()))
            
        except Exception as e:
            raise Exception(f"Error al obtener ventas por fecha: {str(e)}")
    
    @staticmethod
    def obtener_distribucion_menus(db: Session) -> Dict[str, int]:
        """Obtiene la cantidad de veces que cada menú ha sido comprado"""
        try:
            items = db.query(ItemPedido).all()
            
            if not GraficosEstadisticos.validar_datos_disponibles(items):
                return {}
            
            # Usar reduce para sumar las cantidades
            distribucion = {}
            for item in items:
                if item.menu and item.menu.nombre:
                    nombre = item.menu.nombre
                    distribucion[nombre] = distribucion.get(nombre, 0) + item.cantidad
            
            # Ordenar por cantidad (mayor a menor)
            return dict(sorted(distribucion.items(), key=lambda x: x[1], reverse=True))
            
        except Exception as e:
            raise Exception(f"Error al obtener distribución de menús: {str(e)}")
    
    @staticmethod
    def obtener_uso_ingredientes(db: Session) -> Dict[str, float]:
        """Calcula el uso total de cada ingrediente en todos los pedidos"""
        try:
            pedidos = db.query(Pedido).all()
            
            if not GraficosEstadisticos.validar_datos_disponibles(pedidos):
                return {}
            
            uso_ingredientes = {}
            
            for pedido in pedidos:
                for item in pedido.items:
                    menu = item.menu
                    cantidad_menu = item.cantidad
                    
                    # Si el menú tiene receta, calcular ingredientes
                    if menu and menu.receta:
                        for ingrediente, cantidad_por_menu in menu.receta.items():
                            try:
                                cantidad_total = cantidad_por_menu * cantidad_menu
                                uso_ingredientes[ingrediente] = uso_ingredientes.get(ingrediente, 0.0) + cantidad_total
                            except (ValueError, TypeError):
                                # Manejar errores de formato en cantidades
                                continue
            
            return dict(sorted(uso_ingredientes.items(), key=lambda x: x[1], reverse=True))
            
        except Exception as e:
            raise Exception(f"Error al calcular uso de ingredientes: {str(e)}")
    
    @staticmethod
    def graficar_ventas_por_fecha(db: Session, periodo: str = "diario", frame=None):
        """Genera gráfico de barras de ventas por fecha"""
        try:
            ventas = GraficosEstadisticos.obtener_ventas_por_fecha(db, periodo)
            
            if not ventas:
                return None, "No hay datos disponibles para mostrar ventas por fecha"
            
            fig, ax = plt.subplots(figsize=(10, 6))
            
            fechas = list(ventas.keys())
            valores = list(ventas.values())
            
            ax.bar(fechas, valores, color='steelblue')
            ax.set_xlabel('Fecha')
            ax.set_ylabel('Ventas ($)')
            ax.set_title(f'Ventas por {periodo.capitalize()}')
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            
            return fig, None
            
        except Exception as e:
            return None, f"Error al generar gráfico: {str(e)}"
    
    @staticmethod
    def graficar_distribucion_menus(db: Session):
        """Genera gráfico de barras horizontales de menús más comprados"""
        try:
            distribucion = GraficosEstadisticos.obtener_distribucion_menus(db)
            
            if not distribucion:
                return None, "No hay datos disponibles para mostrar distribución de menús"
            
            # Limitar a los 10 más vendidos
            top_10 = dict(list(distribucion.items())[:10])
            
            fig, ax = plt.subplots(figsize=(10, 6))
            
            menus = list(top_10.keys())
            cantidades = list(top_10.values())
            
            ax.barh(menus, cantidades, color='coral')
            ax.set_xlabel('Cantidad Vendida')
            ax.set_ylabel('Menú')
            ax.set_title('Top 10 Menús Más Vendidos')
            plt.tight_layout()
            
            return fig, None
            
        except Exception as e:
            return None, f"Error al generar gráfico: {str(e)}"
    
    @staticmethod
    def graficar_uso_ingredientes(db: Session):
        """Genera gráfico circular del uso de ingredientes"""
        try:
            uso = GraficosEstadisticos.obtener_uso_ingredientes(db)
            
            if not uso:
                return None, "No hay datos disponibles para mostrar uso de ingredientes"
            
            fig, ax = plt.subplots(figsize=(10, 8))
            
            ingredientes = list(uso.keys())
            cantidades = list(uso.values())
            
            # Si hay muchos ingredientes, agrupar los menores
            if len(ingredientes) > 8:
                top_ingredientes = ingredientes[:7]
                top_cantidades = cantidades[:7]
                otros = sum(cantidades[7:])
                
                top_ingredientes.append('Otros')
                top_cantidades.append(otros)
                
                ingredientes = top_ingredientes
                cantidades = top_cantidades
            
            ax.pie(cantidades, labels=ingredientes, autopct='%1.1f%%', startangle=90)
            ax.set_title('Distribución de Uso de Ingredientes')
            plt.tight_layout()
            
            return fig, None
            
        except Exception as e:
            return None, f"Error al generar gráfico: {str(e)}"
