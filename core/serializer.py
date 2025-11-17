# core/serializers.py
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
from django.contrib.auth import authenticate

from .models import Usuario, Rubro, Producto, Proveedor, ProductoProveedor, Cliente, Vendedor, Compra, CompraProducto, Venta, Factura, Envio, ClienteLocal, VentaLocal, ClienteMovilLocal, SolicitudContacto


# JWT con email
class EmailTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = 'email'

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if not email or not password:
            raise serializers.ValidationError('Debe ingresar email y contraseña.')

        user = authenticate(email=email, password=password)

        if user is None:
            raise serializers.ValidationError('Credenciales inválidas.')

        if not user.is_active:
            raise serializers.ValidationError('El usuario está inactivo.')

        attrs['username'] = email
        data = super().validate(attrs)
        return data


# Registro de usuario con creación de Cliente o Vendedor
class RegistroUsuarioSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    nombre = serializers.CharField(required=False)
    apellido = serializers.CharField(required=False)
    telefono = serializers.CharField(required=False)
    direccion = serializers.CharField(required=False)
    zona = serializers.CharField(required=False)

    class Meta:
        model = Usuario
        fields = ["email", "password", "rol", "nombre", "apellido", "telefono", "direccion", "zona"]

    def create(self, validated_data):
        password = validated_data.pop("password")
        rol = validated_data.get("rol")

        user = Usuario(**validated_data)
        user.set_password(password)
        user.save()

        if rol == "cliente":
            Cliente.objects.create(
                id_usuario=user,
                nombre_cliente=validated_data.get("nombre", ""),
                apellido_cliente=validated_data.get("apellido", ""),
                telefono_cliente=validated_data.get("telefono", ""),
                email_cliente=user.email,
                direccion=validated_data.get("direccion", "")
            )
        elif rol == "vendedor":
            Vendedor.objects.create(
                id_usuario=user,
                nombre_vendedor=validated_data.get("nombre", ""),
                apellido_vendedor=validated_data.get("apellido", ""),
                telefono=validated_data.get("telefono", ""),
                email_vendedor=user.email,
                zona=validated_data.get("zona", "")
            )

        return user


# Serializers de otros modelos
class RubroSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rubro
        fields = ['id', 'nombre_rubro']


class ProductoSerializer(serializers.ModelSerializer):
    id_rubro = RubroSerializer(read_only=True)
    id_rubro_id = serializers.PrimaryKeyRelatedField(
        queryset=Rubro.objects.all(), source='id_rubro', write_only=True
    )

    class Meta:
        model = Producto
        fields = ['id', 'id_rubro', 'id_rubro_id', 'nombre_producto', 'descripcion', 'precio', 'stock_actual', 'en_promocion']


class ProveedorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Proveedor
        fields = '__all__'


class ProductoProveedorSerializer(serializers.ModelSerializer):
    id_proveedor = ProveedorSerializer(read_only=True)

    class Meta:
        model = ProductoProveedor
        fields = '__all__'


class ClienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cliente
        fields = '__all__'


class VendedorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vendedor
        fields = '__all__'






class CompraProductoSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompraProducto
        fields = '__all__'


class VentaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Venta
        fields = '__all__'


class FacturaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Factura
        fields = '__all__'


class EnvioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Envio
        fields = '__all__'


class ClienteLocalSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClienteLocal
        fields = '__all__'


class VentaLocalSerializer(serializers.ModelSerializer):
    class Meta:
        model = VentaLocal
        fields = '__all__'


class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = '__all__'

class ClienteMovilLocalSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClienteMovilLocal
        fields = ['id', 'dni_cliente_movil_local', 'nombre_cliente_movil_local', 'apellido_cliente_movil_local']


class CompraSerializer(serializers.ModelSerializer):
    id_cliente_movil_local = ClienteMovilLocalSerializer(read_only=True)

    class Meta:
        model = Compra
        fields = ['id', 'fecha', 'estado', 'id_vendedor', 'id_cliente_movil_local']


class SolicitudContactoSerializer(serializers.ModelSerializer):
    class Meta:
        model = SolicitudContacto
        fields = "__all__"
        read_only_fields = ("usuario", "fecha_creacion", "estado")
