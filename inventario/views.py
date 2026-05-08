"""
Vistas del sistema de inventario.

Todas las vistas de gestión de productos están protegidas con @login_required.
Los usuarios normales solo pueden ver y gestionar sus propios productos.
Los administradores (is_staff) pueden ver todos los productos.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Sum, Count, Q, F
from django.conf import settings

from .models import Producto, Categoria
from .forms import ProductoForm, RegistroForm, CategoriaForm


# =============================================================================
# AUTENTICACIÓN
# =============================================================================

def registro_usuario(request):
    """
    Vista de registro de nuevos usuarios.
    Después de registrarse exitosamente, el usuario inicia sesión automáticamente
    y es redirigido al dashboard.
    """
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'¡Bienvenido {user.username}! Tu cuenta ha sido creada exitosamente.')
            return redirect('dashboard')
        else:
            messages.error(request, 'Por favor corrige los errores del formulario.')
    else:
        form = RegistroForm()

    return render(request, 'registration/register.html', {'form': form})


# =============================================================================
# DASHBOARD
# =============================================================================

@login_required
def dashboard(request):
    """
    Dashboard principal del sistema.
    Muestra estadísticas generales: total de productos, productos con bajo stock,
    valor total del inventario, y los últimos productos agregados.
    Los admins ven las estadísticas de todos los usuarios.
    """
    umbral = getattr(settings, 'STOCK_BAJO_UMBRAL', 5)

    if request.user.is_staff:
        productos = Producto.objects.all()
    else:
        productos = Producto.objects.filter(usuario=request.user)

    total_productos = productos.count()
    productos_bajo_stock = productos.filter(cantidad__lt=umbral).count()

    # Calcular valor total del inventario
    valor_total = productos.aggregate(
        total=Sum(F('cantidad') * F('precio'))
    )['total'] or 0

    # Últimos 5 productos
    ultimos_productos = productos[:5]

    # Productos con bajo stock para la alerta
    alertas_stock = productos.filter(cantidad__lt=umbral)[:10]

    context = {
        'total_productos': total_productos,
        'productos_bajo_stock': productos_bajo_stock,
        'valor_total': valor_total,
        'ultimos_productos': ultimos_productos,
        'alertas_stock': alertas_stock,
        'umbral': umbral,
    }
    return render(request, 'inventario/dashboard.html', context)


# =============================================================================
# CRUD DE PRODUCTOS
# =============================================================================

@login_required
def producto_lista(request):
    """
    Lista de productos con búsqueda y paginación.
    Los admins ven todos los productos; los usuarios normales solo los suyos.
    Soporta búsqueda por nombre o descripción mediante el parámetro GET 'q'.
    Paginación de 10 productos por página.
    """
    if request.user.is_staff:
        productos = Producto.objects.all()
    else:
        productos = Producto.objects.filter(usuario=request.user)

    # Búsqueda
    query = request.GET.get('q', '').strip()
    if query:
        productos = productos.filter(
            Q(nombre__icontains=query) | Q(descripcion__icontains=query)
        )
    
    # Filtrado por categoría
    categoria_id = request.GET.get('categoria')
    if categoria_id:
        productos = productos.filter(categoria_id=categoria_id)

    # Paginación
    paginator = Paginator(productos, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'query': query,
        'total_resultados': paginator.count,
        'categorias': Categoria.objects.all(),
        'categoria_actual': int(categoria_id) if categoria_id and categoria_id.isdigit() else None,
    }
    return render(request, 'inventario/producto_list.html', context)


@login_required
def producto_crear(request):
    """
    Crear un nuevo producto.
    El campo 'usuario' se asigna automáticamente al usuario logueado.
    """
    if request.method == 'POST':
        form = ProductoForm(request.POST)
        if form.is_valid():
            producto = form.save(commit=False)
            producto.usuario = request.user
            producto.save()
            messages.success(request, f'Producto "{producto.nombre}" creado exitosamente.')
            return redirect('producto_lista')
        else:
            messages.error(request, 'Por favor corrige los errores del formulario.')
    else:
        form = ProductoForm()

    return render(request, 'inventario/producto_form.html', {
        'form': form,
        'titulo': 'Nuevo Producto',
        'boton': 'Crear Producto',
    })


@login_required
def producto_editar(request, pk):
    """
    Editar un producto existente.
    Solo el creador del producto o un administrador pueden editarlo.
    """
    producto = get_object_or_404(Producto, pk=pk)

    # Verificar permisos
    if not request.user.is_staff and producto.usuario != request.user:
        messages.error(request, 'No tienes permiso para editar este producto.')
        return redirect('producto_lista')

    if request.method == 'POST':
        form = ProductoForm(request.POST, instance=producto)
        if form.is_valid():
            form.save()
            messages.success(request, f'Producto "{producto.nombre}" actualizado exitosamente.')
            return redirect('producto_lista')
        else:
            messages.error(request, 'Por favor corrige los errores del formulario.')
    else:
        form = ProductoForm(instance=producto)

    return render(request, 'inventario/producto_form.html', {
        'form': form,
        'titulo': f'Editar: {producto.nombre}',
        'boton': 'Guardar Cambios',
        'producto': producto,
    })


@login_required
def producto_eliminar(request, pk):
    """
    Eliminar un producto con confirmación.
    Solo el creador del producto o un administrador pueden eliminarlo.
    Requiere confirmación via POST para evitar eliminaciones accidentales.
    """
    producto = get_object_or_404(Producto, pk=pk)

    # Verificar permisos
    if not request.user.is_staff and producto.usuario != request.user:
        messages.error(request, 'No tienes permiso para eliminar este producto.')
        return redirect('producto_lista')

    if request.method == 'POST':
        nombre = producto.nombre
        producto.delete()
        messages.success(request, f'Producto "{nombre}" eliminado exitosamente.')
        return redirect('producto_lista')

    return render(request, 'inventario/producto_confirm_delete.html', {
        'producto': producto,
    })


@login_required
def producto_detalle(request, pk):
    """
    Ver detalle de un producto.
    Los admins pueden ver cualquier producto; los usuarios normales solo los suyos.
    """
    producto = get_object_or_404(Producto, pk=pk)

    # Verificar permisos
    if not request.user.is_staff and producto.usuario != request.user:
        messages.error(request, 'No tienes permiso para ver este producto.')
        return redirect('producto_lista')

    return render(request, 'inventario/producto_detail.html', {
        'producto': producto,
    })


# =============================================================================
# CRUD DE CATEGORÍAS
# =============================================================================

@login_required
def categoria_lista(request):
    """Listado de categorías."""
    categorias = Categoria.objects.annotate(total_productos=Count('productos'))
    return render(request, 'inventario/categoria_list.html', {
        'categorias': categorias,
    })


@login_required
def categoria_crear(request):
    """Crear una nueva categoría."""
    if request.method == 'POST':
        form = CategoriaForm(request.POST)
        if form.is_valid():
            categoria = form.save()
            messages.success(request, f'Categoría "{categoria.nombre}" creada exitosamente.')
            return redirect('categoria_lista')
    else:
        form = CategoriaForm()
    
    return render(request, 'inventario/categoria_form.html', {
        'form': form,
        'titulo': 'Nueva Categoría',
        'boton': 'Crear Categoría',
    })


@login_required
def categoria_editar(request, pk):
    """Editar una categoría existente."""
    categoria = get_object_or_404(Categoria, pk=pk)
    if request.method == 'POST':
        form = CategoriaForm(request.POST, instance=categoria)
        if form.is_valid():
            form.save()
            messages.success(request, f'Categoría "{categoria.nombre}" actualizada exitosamente.')
            return redirect('categoria_lista')
    else:
        form = CategoriaForm(instance=categoria)
    
    return render(request, 'inventario/categoria_form.html', {
        'form': form,
        'titulo': f'Editar: {categoria.nombre}',
        'boton': 'Guardar Cambios',
        'categoria': categoria,
    })


@login_required
def categoria_eliminar(request, pk):
    """Eliminar una categoría."""
    categoria = get_object_or_404(Categoria, pk=pk)
    if request.method == 'POST':
        nombre = categoria.nombre
        categoria.delete()
        messages.success(request, f'Categoría "{nombre}" eliminada exitosamente.')
        return redirect('categoria_lista')
    
    return render(request, 'inventario/categoria_confirm_delete.html', {
        'categoria': categoria,
    })
