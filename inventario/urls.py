"""
URLs de la aplicación inventario.

Define las rutas para:
- Dashboard
- CRUD de productos (listar, crear, detalle, editar, eliminar)
"""

from django.urls import path
from . import views

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),

    # CRUD de productos
    path('productos/', views.producto_lista, name='producto_lista'),
    path('productos/nuevo/', views.producto_crear, name='producto_crear'),
    path('productos/<int:pk>/', views.producto_detalle, name='producto_detalle'),
    path('productos/<int:pk>/editar/', views.producto_editar, name='producto_editar'),
    path('productos/<int:pk>/eliminar/', views.producto_eliminar, name='producto_eliminar'),

    # CRUD de categorías
    path('categorias/', views.categoria_lista, name='categoria_lista'),
    path('categorias/nueva/', views.categoria_crear, name='categoria_crear'),
    path('categorias/<int:pk>/editar/', views.categoria_editar, name='categoria_editar'),
    path('categorias/<int:pk>/eliminar/', views.categoria_eliminar, name='categoria_eliminar'),
]
