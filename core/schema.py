# core/schema.py
import graphene
from graphene_django import DjangoObjectType

from core.models import (
    ClienteMovilLocal, Compra, Vendedor, CompraProducto, Producto, Envio, Venta
)

# Type (Modelos _ Graphql)

class ProductoType(DjangoObjectType):
    class Meta:
        model = Producto
        fields = ("id", "nombre_producto", "precio", "descripcion", "stock_actual")


class CompraProductoType(DjangoObjectType):
    class Meta:
        model = CompraProducto
        fields = ("id", "id_producto", "cantidad", "precio_unitario")

    producto = graphene.Field(ProductoType)

    def resolve_producto(self, info):
        return self.id_producto


class VendedorType(DjangoObjectType):
    class Meta:
        model = Vendedor
        fields = ("id", "nombre_vendedor", "apellido_vendedor", "telefono", "email_vendedor", "zona")


class EnvioType(DjangoObjectType):
    class Meta:
        model = Envio
        fields = ("empresa_flete", "fecha_envio", "fecha_recepcion")


class VentaType(DjangoObjectType):
    class Meta:
        model = Venta
        fields = ("id", "monto_total", "fecha_venta")


class CompraType(DjangoObjectType):
    class Meta:
        model = Compra
        fields = ("id", "fecha", "estado", "id_vendedor", "id_cliente_movil_local")

    vendedor = graphene.Field(VendedorType)
    productos = graphene.List(CompraProductoType)
    envio = graphene.Field(EnvioType)
    venta = graphene.Field(VentaType)

    def resolve_vendedor(self, info):
        return self.id_vendedor

    def resolve_productos(self, info):
        return CompraProducto.objects.filter(id_compra=self.id)

    def resolve_envio(self, info):
        try:
            return Envio.objects.get(compra=self)
        except Envio.DoesNotExist:
            return None

    def resolve_venta(self, info):
        try:
            return Venta.objects.get(id_compra=self)
        except Venta.DoesNotExist:
            return None


class ClienteMovilLocalType(DjangoObjectType):
    class Meta:
        model = ClienteMovilLocal
        fields = ("id",
                  "nombre_cliente_movil_local",
                  "apellido_cliente_movil_local",
                  "telefono_cliente_movil_local",
                  "email_cliente_movil_local")
        
# Query compleja
class Query(graphene.ObjectType):
    compras_por_cliente_movil_local = graphene.List(
        CompraType,
        dni=graphene.Int(required=False),
        cliente_id=graphene.Int(required=False)
    )

    def resolve_compras_por_cliente_movil_local(self, info, dni=None, cliente_id=None):
        if dni:
            cliente = ClienteMovilLocal.objects.filter(dni_cliente_movil_local=dni).first()
            if not cliente:
                return []
            return Compra.objects.filter(id_cliente_movil_local=cliente.id)
        
        if cliente_id:
            return Compra.objects.filter(id_cliente_movil_local=cliente_id)

        return []

    

schema = graphene.Schema(query=Query)