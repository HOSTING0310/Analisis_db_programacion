"""
Template tags personalizados para la app inventario.
"""

from django import template

register = template.Library()


@register.filter
def currency(value):
    """Formatea un número como moneda colombiana."""
    try:
        return f"${value:,.2f}"
    except (ValueError, TypeError):
        return value


@register.filter
def stock_class(cantidad):
    """Retorna la clase CSS según el nivel de stock."""
    try:
        cantidad = int(cantidad)
        if cantidad < 5:
            return 'stock-critico'
        elif cantidad < 10:
            return 'stock-bajo'
        else:
            return 'stock-ok'
    except (ValueError, TypeError):
        return ''
