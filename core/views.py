# core/views.py
from rest_framework import viewsets, status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.contrib.auth.hashers import make_password
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import (
    Rubro, Producto, Proveedor, ProductoProveedor,
    Cliente, Vendedor, Compra, CompraProducto, Usuario,
    Venta, Factura, Envio, ClienteLocal, VentaLocal, ClienteMovilLocal, SolicitudContacto
)
from .serializer import (
    RubroSerializer, ProductoSerializer, ProveedorSerializer, ProductoProveedorSerializer, UsuarioSerializer,
    ClienteSerializer, VendedorSerializer, CompraSerializer, CompraProductoSerializer, VentaLocalSerializer,
    VentaSerializer, FacturaSerializer, EnvioSerializer, EmailTokenObtainPairSerializer, RegistroUsuarioSerializer, ClienteLocalSerializer,
    ClienteMovilLocalSerializer, SolicitudContactoSerializer
)


# --------------------
# ViewSets para cada modelo ##################################################################################################
class RubroViewSet(viewsets.ModelViewSet):
    queryset = Rubro.objects.all()
    serializer_class = RubroSerializer
    permission_classes = [] 
    # permission_classes = [IsAuthenticated]

# --------------------
# ViewSets para cada modelo ####################################################################################################
class ProductoViewSet(viewsets.ModelViewSet):
    queryset = Producto.objects.all()
    serializer_class = ProductoSerializer
    permission_classes = [] 
    # permission_classes = [IsAuthenticated]


class ProveedorViewSet(viewsets.ModelViewSet):
    queryset = Proveedor.objects.all()
    serializer_class = ProveedorSerializer
    permission_classes = []


class ProductoProveedorViewSet(viewsets.ModelViewSet):
    queryset = ProductoProveedor.objects.all()
    serializer_class = ProductoProveedorSerializer
    permission_classes = []


class ClienteViewSet(viewsets.ModelViewSet):
    queryset = Cliente.objects.all()
    serializer_class = ClienteSerializer
    permission_classes = []


class VendedorViewSet(viewsets.ModelViewSet):
    queryset = Vendedor.objects.all()
    serializer_class = VendedorSerializer
    permission_classes = []


class CompraViewSet(viewsets.ModelViewSet):
    queryset = Compra.objects.all()
    serializer_class = CompraSerializer
    permission_classes = []


class CompraProductoViewSet(viewsets.ModelViewSet):
    queryset = CompraProducto.objects.all()
    serializer_class = CompraProductoSerializer
    def get_queryset(self):
        queryset = super().get_queryset()
        producto_id = self.request.query_params.get('producto_id')
        if producto_id:
            queryset = queryset.filter(id_producto_id=producto_id)
        return queryset
    permission_classes = []


class VentaViewSet(viewsets.ModelViewSet):
    queryset = Venta.objects.all()
    serializer_class = VentaSerializer
    permission_classes = []


class FacturaViewSet(viewsets.ModelViewSet):
    queryset = Factura.objects.all()
    serializer_class = FacturaSerializer
    permission_classes = []


class EnvioViewSet(viewsets.ModelViewSet):
    queryset = Envio.objects.all()
    serializer_class = EnvioSerializer
    permission_classes = []


# --------------------
# JWT Login #########################################################################################################
class EmailTokenObtainPairView(TokenObtainPairView):
    serializer_class = EmailTokenObtainPairSerializer
    permission_classes = []



# --------------------
# Endpoint para crear el primer administrador #########################################################################
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def crear_admin(request):
    """
    Crea un usuario administrador si no hay ninguno en la base de datos.
    """
    if Usuario.objects.exists():
        return Response(
            {"detail": "Ya existe un usuario registrado."},
            status=status.HTTP_400_BAD_REQUEST
        )

    email = request.data.get('email')
    password = request.data.get('password')

    if not email or not password:
        return Response(
            {"detail": "Debe proporcionar email y contraseña."},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Guardar contraseña hasheada
    Usuario.objects.create(
        email=email,
        password=make_password(password),
        rol='Administrador'
    )

    return Response(
        {"detail": "Usuario administrador creado correctamente."},
        status=status.HTTP_201_CREATED
    )


class RegistroUsuarioView(generics.CreateAPIView):
    """
    Endpoint para registrar usuarios (administradores, clientes, etc.).
    """
    queryset = Usuario.objects.all()
    serializer_class = RegistroUsuarioSerializer
    permission_classes = [permissions.AllowAny] 


# Despues lo borramos #############################################################################
class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = Usuario.objects.all()
    serializer_class = RegistroUsuarioSerializer
    permission_classes = [permissions.AllowAny]


class ClienteLocalViewSet(viewsets.ModelViewSet):
    queryset = ClienteLocal.objects.all()
    serializer_class = ClienteLocalSerializer
    permission_classes = []

class ClienteMovilLocalViewSet(viewsets.ModelViewSet):
    queryset = ClienteMovilLocal.objects.all()
    serializer_class = ClienteMovilLocalSerializer
    permission_classes = []  # ajustar según necesidad


class CompraViewSet(viewsets.ModelViewSet):
    queryset = Compra.objects.all().order_by('-fecha')
    serializer_class = CompraSerializer

    def perform_create(self, serializer):
        cliente = serializer.validated_data['id_cliente']
        serializer.save(dni_cliente_compra=cliente.dni_cliente)


    @action(detail=False, methods=['get'], url_path='pendientes')
    def pendientes(self, request):
        pendientes = self.queryset.filter(estado='Pendiente')
        serializer = self.get_serializer(pendientes, many=True)
        return Response(serializer.data)
    permission_classes = []

    @action(detail=False, methods=['get'])
    def por_dni(self, request):
        dni = request.query_params.get('dni')
        if not dni:
            return Response({"error": "Falta parámetro dni"}, status=400)
        compras = Compra.objects.filter(id_cliente_movil_local__dni_cliente_movil_local=dni)
        serializer = self.get_serializer(compras, many=True)
        return Response(serializer.data)

class VentaLocalViewSet(viewsets.ModelViewSet):
    queryset = VentaLocal.objects.all()
    serializer_class = VentaLocalSerializer
    permission_classes = []


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def usuario_actual(request):
    user = request.user
    nombre = ""
    apellido = ""
    dni = ""

    if user.rol.lower() == "cliente":
        try:
            cliente = Cliente.objects.get(id_usuario=user)
            nombre = cliente.nombre_cliente
            apellido = cliente.apellido_cliente
            dni = cliente.dni_cliente
        except Cliente.DoesNotExist:
            pass
    elif user.rol.lower() == "vendedor":
        try:
            vendedor = Vendedor.objects.get(id_usuario=user)
            nombre = vendedor.nombre_vendedor
            apellido = vendedor.apellido_vendedor
            dni = vendedor.dni_vendedor
        except Vendedor.DoesNotExist:
            pass

    return Response({
        "id": user.id,
        "email": user.email,
        "rol": user.rol,
        "nombre": nombre,
        "apellido": apellido,
        "dni": dni
    })


# Para registrar usuario
@api_view(["POST"])
@permission_classes([AllowAny])
def register_user(request):
    try:
        email = request.data.get("email")
        password = request.data.get("password")
        rol = request.data.get("rol")  # cliente, vendedor, administrador
        nombre = request.data.get("nombre")
        apellido = request.data.get("apellido")
        telefono = request.data.get("telefono")
        direccion = request.data.get("direccion")
        dni = request.data.get("dni")

        if Usuario.objects.filter(email=email).exists():
            return Response({"error": "El email ya está registrado."}, status=status.HTTP_400_BAD_REQUEST)

        # Crear el usuario
        usuario = Usuario.objects.create_user(email=email, password=password, rol=rol)

        # Crear registros relacionados según rol
        if rol == "cliente":
            Cliente.objects.create(
                id_usuario=usuario,
                nombre_cliente=nombre,
                apellido_cliente=apellido,
                telefono_cliente=telefono,
                email_cliente=email,
                direccion=direccion,
                dni_cliente=dni,
            )
        elif rol == "vendedor":
            Vendedor.objects.create(
                id_usuario=usuario,
                nombre_vendedor=nombre,
                apellido_vendedor=apellido,
                telefono=telefono,
                email_vendedor=email,
                zona=direccion,  # dirección como zona
                dni_vendedor=dni,
            )
        # administrador no necesita tabla adicional

        return Response({"success": f"Usuario {rol} registrado correctamente."}, status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    

# Productos en promoción
@api_view(["GET"])
@permission_classes([AllowAny])
def productos_en_promocion(request):
    productos = Producto.objects.filter(en_promocion=True)
    serializer = ProductoSerializer(productos, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([AllowAny])
def estado_compra(request):
    dni = request.GET.get('dni')
    if not dni:
        return Response({'error': 'Se requiere el DNI'}, status=400)

    clientes_movil = ClienteMovilLocal.objects.filter(dni_cliente_movil_local=dni)
    if not clientes_movil.exists():
        return Response({'error': 'No se encontró el DNI en clientes móviles.'}, status=404)
    
    # Buscar compras asociadas a esos clientes
    compras = Compra.objects.filter(id_cliente_movil_local__in=clientes_movil)
    serializer = CompraSerializer(compras, many=True)
    return Response(serializer.data)


# Crear solicitud - clientes
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def crear_solicitud(request):
    solicitud = SolicitudContacto.objects.create(
        usuario=request.user
    )

    return Response({
        "id": solicitud.id,
        "estado": solicitud.estado,
        "fecha_creacion": solicitud.fecha_creacion
    }, status=status.HTTP_201_CREATED)


# Cancelar Solicitud - Clientes
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def cancelar_solicitud(request):
    user = request.user
    if user.rol.lower() != "cliente":
        return Response({"detail": "Solo clientes."}, status=403)
    try:
        cliente = Cliente.objects.get(id_usuario=user)
    except Cliente.DoesNotExist:
        return Response({"detail": "Perfil de cliente no encontrado."}, status=404)
    if not hasattr(cliente, 'solicitud_contacto'):
        return Response({"detail": "No tenés solicitud activa."}, status=404)
    cliente.solicitud_contacto.delete()
    return Response({"detail": "Solicitud cancelada."}, status=204)


# Ver solicitudes - vendedores
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def solicitudes_pendientes(request):
    rol = request.user.rol.lower()
    if rol == "vendedor":
        solicitudes = SolicitudContacto.objects.filter(estado='pendiente').order_by("-fecha_creacion")
    elif rol == "cliente":
        solicitudes = SolicitudContacto.objects.filter(usuario=request.user).order_by("-fecha_creacion")
    else:
        return Response({"detail": "Rol no autorizado."}, status=403)
    serializer = SolicitudContactoSerializer(solicitudes, many=True)
    return Response(serializer.data)


# Aceptar solicitudes - vendedores
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def aceptar_solicitud(request, solicitud_id):
    if request.user.rol.lower() != "vendedor":
        return Response({"detail": "Solo vendedores."}, status=403)

    try:
        vendedor = Vendedor.objects.get(id_usuario=request.user)
    except Vendedor.DoesNotExist:
        return Response({"detail": "Perfil de vendedor no encontrado."}, status=404)

    try:
        solicitud = SolicitudContacto.objects.get(id=solicitud_id, estado='pendiente')
    except SolicitudContacto.DoesNotExist:
        return Response({"detail": "Solicitud no encontrada o ya procesada."}, status=404)

    usuario = solicitud.usuario
    try:
        cliente = Cliente.objects.get(id_usuario=usuario)
    except Cliente.DoesNotExist:
        return Response({"detail": "Cliente no encontrado."}, status=404)


    # Crear cliente móvil
    ClienteMovilLocal.objects.create(
        nombre_cliente_movil_local = cliente.nombre_cliente,
        apellido_cliente_movil_local = cliente.apellido_cliente,
        telefono_cliente_movil_local = cliente.telefono_cliente,
        email_cliente_movil_local = cliente.email_cliente,
        direccion_cliente_movil_local = cliente.direccion,
        dni_cliente_movil_local = cliente.dni_cliente,
    )

    # Marcar quién aceptó
    solicitud.vendedor_acepta = vendedor
    solicitud.estado = "aceptada"
    solicitud.save()

    # comienza integración Firebase
    from moto_api.firebase.firebase import enviar_notificacion
    enviar_notificacion(usuario.id, "Tu solicitud fue aceptada")

    # Finalmente eliminar la solicitud
    solicitud.delete()

    return Response({"detail": "Solicitud aceptada."}, status=200)

