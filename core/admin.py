# core/admin.py
from django.contrib import admin
from .models import ClienteLocal, Compra, Producto


@admin.register(ClienteLocal)
class ClienteLocalAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre_cliente', 'apellido_cliente', 'telefono_cliente', 'email_cliente')
    search_fields = ('nombre_cliente', 'apellido_cliente', 'dni', 'email_cliente')


@admin.register(Compra)
class CompraAdmin(admin.ModelAdmin):
    list_display = ('id', 'id_cliente_movil_local', 'id_vendedor', 'fecha', 'estado')
    list_filter = ('estado', 'fecha')
    search_fields = ('id_cliente_movil_local__nombre_cliente_movil_local', 'id_vendedor__nombre_vendedor')



@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):  # nombre de clase distinto al modelo
    list_display = ('id', 'nombre_producto', 'descripcion', 'precio', 'stock_actual')  # campo correcto
    list_filter = ('nombre_producto', 'precio')  # list_filter solo con campos adecuados
