"""
Formularios del sistema de inventario.

Incluye:
- ProductoForm: formulario para crear/editar productos con widgets de Bootstrap
- RegistroForm: formulario de registro extendido con campo de email
"""

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Producto, Categoria


class CategoriaForm(forms.ModelForm):
    """
    Formulario para crear y editar categorías.
    """
    class Meta:
        model = Categoria
        fields = ['nombre', 'descripcion']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre de la categoría',
                'data-bs-theme': 'dark',
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Descripción (opcional)',
                'rows': 3,
                'data-bs-theme': 'dark',
            }),
        }


class ProductoForm(forms.ModelForm):
    """
    Formulario para crear y editar productos.
    Utiliza ModelForm para generar automáticamente los campos
    a partir del modelo Producto, con widgets personalizados de Bootstrap.
    """

    class Meta:
        model = Producto
        fields = ['nombre', 'descripcion', 'categoria', 'cantidad', 'precio']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del producto',
                'autocomplete': 'off',
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Descripción del producto (opcional)',
                'rows': 4,
                'data-bs-theme': 'dark',
            }),
            'categoria': forms.Select(attrs={
                'class': 'form-select',
                'data-bs-theme': 'dark',
            }),
            'cantidad': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0',
                'min': '0',
                'data-bs-theme': 'dark',
            }),
            'precio': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01',
                'min': '0',
                'data-bs-theme': 'dark',
            }),
        }

    def clean_precio(self):
        """Valida que el precio sea mayor a cero."""
        precio = self.cleaned_data.get('precio')
        if precio is not None and precio <= 0:
            raise forms.ValidationError('El precio debe ser mayor a cero.')
        return precio


class RegistroForm(UserCreationForm):
    """
    Formulario de registro extendido.
    Agrega el campo de email como obligatorio al formulario
    estándar de creación de usuario de Django.
    """

    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'correo@ejemplo.com',
        })
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Agregar clases de Bootstrap a todos los campos
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Nombre de usuario',
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Contraseña',
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirmar contraseña',
        })

    def clean_email(self):
        """Valida que el email no esté ya registrado."""
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Este email ya está registrado.')
        return email

    def save(self, commit=True):
        """Guarda el usuario con el email proporcionado."""
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user
