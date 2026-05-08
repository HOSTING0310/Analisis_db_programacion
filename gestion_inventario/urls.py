"""
URLs principales del proyecto gestion_inventario.

Incluye:
- Panel de administración de Django
- URLs de autenticación (login, logout)
- Registro de usuario
- URLs de la app inventario
"""

from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from inventario import views

urlpatterns = [
    # Panel de administración
    path('admin/', admin.site.urls),

    # Autenticación
    path('login/', auth_views.LoginView.as_view(
        template_name='registration/login.html',
        redirect_authenticated_user=True,
    ), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('registro/', views.registro_usuario, name='registro'),

    # App inventario
    path('', include('inventario.urls')),
]
