# core/urls.py
from rest_framework import routers
from django.urls import path, include
from .views import (
    RubroViewSet, ProductoViewSet, ProveedorViewSet, ProductoProveedorViewSet,
    ClienteViewSet, VendedorViewSet, CompraViewSet, CompraProductoViewSet,
    VentaViewSet, FacturaViewSet, EnvioViewSet, EmailTokenObtainPairView, 
    RegistroUsuarioView, UsuarioViewSet, ClienteLocalViewSet, VentaLocalViewSet, ClienteMovilLocalViewSet
)
from .views import crear_admin, usuario_actual, productos_en_promocion
from . import views



router = routers.DefaultRouter()
router.register(r'rubros', RubroViewSet)
router.register(r'productos', ProductoViewSet)
router.register(r'proveedores', ProveedorViewSet)
router.register(r'producto_proveedor', ProductoProveedorViewSet)
router.register(r'clientes', ClienteViewSet)
router.register(r'vendedores', VendedorViewSet)
router.register(r'compras', CompraViewSet)
router.register(r'compra_productos', CompraProductoViewSet)
router.register(r'ventas', VentaViewSet)
router.register(r'facturas', FacturaViewSet)
router.register(r'envios', EnvioViewSet)
router.register(r'usuarios', UsuarioViewSet) # Despues lo borramos
router.register(r'clientes_locales', ClienteLocalViewSet) 
router.register(r'ventas_locales', VentaLocalViewSet)
router.register(r'clientes_moviles_locales', ClienteMovilLocalViewSet)



urlpatterns = [
    
    # Productos en promocíon
    path('productos/promocion/', productos_en_promocion, name='productos_en_promocion'),
    # Estado de la compra
    path('compras/estado/', views.estado_compra, name='estado_compra'),


    path('', include(router.urls)),

    # Autenticación y administración
    path('token/', EmailTokenObtainPairView.as_view(), name='token_obtain_pair_email'),
    path('crear-admin/', crear_admin, name='crear_admin'),

    # registro de usuarios
    path("usuarios/register/", RegistroUsuarioView.as_view(), name="registro-usuario"),# Sistema de escritorio
    path("register/", views.register_user, name="register"), # Web y sistema de escritorio

    path("usuario_actual/", usuario_actual, name="usuario_actual"),

    # Solicitudes contacto
    path('solicitud/crear/', views.crear_solicitud, name=""),
    path('solicitud/cancelar/', views.cancelar_solicitud, name=""),
    path('solicitudes/pendientes/', views.solicitudes_pendientes, name=""),

    path('solicitud/<int:solicitud_id>/aceptar/', views.aceptar_solicitud),

] 