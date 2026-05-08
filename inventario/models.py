"""
Modelos del sistema de inventario.

El modelo Producto es el núcleo del sistema. Cada producto está vinculado
al usuario que lo creó mediante una ForeignKey. Incluye una propiedad
para detectar stock bajo basada en el umbral definido en settings.
"""

from django.db import models
from django.conf import settings
from django.contrib.auth.models import User


class Categoria(models.Model):
    """
    Modelo para categorizar los productos.
    """
    nombre = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='Nombre de la categoría'
    )
    descripcion = models.TextField(
        blank=True,
        default='',
        verbose_name='Descripción'
    )

    class Meta:
        verbose_name = 'Categoría'
        verbose_name_plural = 'Categorías'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Producto(models.Model):
    """
    Modelo principal para los productos del inventario.

    Campos:
        nombre: Nombre del producto (máximo 200 caracteres)
        descripcion: Descripción detallada del producto (opcional)
        cantidad: Cantidad disponible en inventario (entero positivo)
        precio: Precio unitario con hasta 10 dígitos y 2 decimales
        fecha_creacion: Fecha y hora de creación (automática)
        fecha_actualizacion: Fecha y hora de última actualización (automática)
        usuario: Usuario que creó el producto (relación ForeignKey)
    """

    nombre = models.CharField(
        max_length=200,
        verbose_name='Nombre del producto'
    )
    descripcion = models.TextField(
        blank=True,
        default='',
        verbose_name='Descripción'
    )
    cantidad = models.PositiveIntegerField(
        default=0,
        verbose_name='Cantidad en stock'
    )
    precio = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Precio unitario'
    )
    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de creación'
    )
    fecha_actualizacion = models.DateTimeField(
        auto_now=True,
        verbose_name='Última actualización'
    )
    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='productos',
        verbose_name='Creado por'
    )
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='productos',
        verbose_name='Categoría'
    )

    class Meta:
        ordering = ['-fecha_creacion']
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'

    def __str__(self):
        return f'{self.nombre} (Stock: {self.cantidad})'

    @property
    def stock_bajo(self):
        """Retorna True si la cantidad está por debajo del umbral definido en settings."""
        umbral = getattr(settings, 'STOCK_BAJO_UMBRAL', 5)
        return self.cantidad < umbral

    @property
    def valor_total(self):
        """Calcula el valor total del inventario de este producto."""
        return self.cantidad * self.precio
