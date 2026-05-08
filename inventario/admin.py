"""
Configuración del panel de administración para el modelo Producto.

Personaliza la interfaz del admin de Django con:
- Columnas personalizadas (nombre, cantidad, precio, usuario, fecha)
- Indicador visual de stock bajo
- Filtros por usuario y fecha
- Búsqueda por nombre y descripción
"""

from django.contrib import admin
from django.conf import settings
from django.utils.html import format_html
from .models import Producto, Categoria


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'descripcion']
    search_fields = ['nombre']


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    """Panel de administración personalizado para Producto."""

    list_display = [
        'nombre',
        'cantidad_display',
        'precio',
        'usuario',
        'fecha_creacion',
        'estado_stock',
    ]
    list_filter = ['usuario', 'fecha_creacion']
    search_fields = ['nombre', 'descripcion']
    list_per_page = 20
    readonly_fields = ['fecha_creacion', 'fecha_actualizacion']

    fieldsets = (
        ('Información del Producto', {
            'fields': ('nombre', 'descripcion', 'categoria', 'cantidad', 'precio')
        }),
        ('Metadata', {
            'fields': ('usuario', 'fecha_creacion', 'fecha_actualizacion'),
            'classes': ('collapse',),
        }),
    )

    def cantidad_display(self, obj):
        """Muestra la cantidad con color según el nivel de stock."""
        umbral = getattr(settings, 'STOCK_BAJO_UMBRAL', 5)
        if obj.cantidad < umbral:
            color = '#e74c3c'
            icon = '⚠️'
        elif obj.cantidad < umbral * 2:
            color = '#f39c12'
            icon = '⚡'
        else:
            color = '#27ae60'
            icon = '✅'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{} {}</span>',
            color, icon, obj.cantidad
        )
    cantidad_display.short_description = 'Cantidad'
    cantidad_display.admin_order_field = 'cantidad'

    def estado_stock(self, obj):
        """Muestra un badge con el estado del stock."""
        if obj.stock_bajo:
            return format_html(
                '<span style="background-color: #e74c3c; color: white; '
                'padding: 3px 10px; border-radius: 12px; font-size: 11px;">'
                'BAJO</span>'
            )
        return format_html(
            '<span style="background-color: #27ae60; color: white; '
            'padding: 3px 10px; border-radius: 12px; font-size: 11px;">'
            'OK</span>'
        )
    estado_stock.short_description = 'Estado'
