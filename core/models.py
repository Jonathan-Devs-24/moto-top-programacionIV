# core/models.py
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.contrib.auth.hashers import make_password
from django.utils import timezone


# 0.0 TABLA: UsuarioManager
class UsuarioManager(BaseUserManager):
    def create_user(self, email, password=None, rol='cliente', **extra_fields):
        if not email:
            raise ValueError("El email es obligatorio")
        email = self.normalize_email(email)
        user = self.model(email=email, rol=rol, **extra_fields)
        user.password = make_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, rol='administrador', **extra_fields)

# 0.1 TABLA: Usuario
class Usuario(AbstractBaseUser, PermissionsMixin):
    ROLES = [
        ('administrador', 'Administrador'),
        ('cliente', 'Cliente'),
        ('vendedor', 'Vendedor'),
    ]

    email = models.EmailField(unique=True)
    rol = models.CharField(max_length=20, choices=ROLES)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    # Evita el conflicto con auth.User
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='custom_user_set', 
        blank=True,
        help_text='Los grupos a los que pertenece este usuario.'
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='custom_user_set',
        blank=True,
        help_text='Permisos específicos para este usuario.'
    )

    objects = UsuarioManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return f"{self.email} ({self.rol})"


# 1. Rubro ______________________________________________________________________________________________________
class Rubro(models.Model):
    nombre_rubro = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nombre_rubro


# 2. Producto ___________________________________________________________________________________________________
class Producto(models.Model):
    id_rubro = models.ForeignKey(Rubro, on_delete=models.CASCADE)
    nombre_producto = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    stock_actual = models.IntegerField()
    en_promocion = models.BooleanField(default=False)

    def __str__(self):
        return self.nombre_producto


# 3. Proveedor __________________________________________________________________________________________________
class Proveedor(models.Model):
    nombre_proveedor = models.CharField(max_length=100)
    telefono = models.CharField(max_length=20)
    domicilio = models.CharField(max_length=150)
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.nombre_proveedor


# 4. Producto_Proveedor (relación N:M) ___________________________________________________________________________
class ProductoProveedor(models.Model):
    id_proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE)
    id_producto = models.ForeignKey(Producto, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('id_proveedor', 'id_producto')


# 5. Cliente ___________________________________________________________________________________________________
class Cliente(models.Model):
    id_usuario = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, blank=True)
    nombre_cliente = models.CharField(max_length=150)
    apellido_cliente = models.CharField(max_length=150)
    telefono_cliente = models.CharField(max_length=20, blank=True, null=True)
    email_cliente = models.EmailField(unique=True, blank=True, null=True)
    direccion = models.CharField(max_length=150, blank=True, null=True)
    dni_cliente = models.CharField(max_length=20, unique=True, null=True, blank=True)

    
    def __str__(self):
        return f"{self.nombre_cliente} {self.apellido_cliente}"


# 6. Vendedor _________________________________________________________________________________________________
class Vendedor(models.Model):
    id_usuario = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, blank=True)
    nombre_vendedor = models.CharField(max_length=100)
    apellido_vendedor = models.CharField(max_length=100)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    email_vendedor = models.EmailField(unique=True)
    zona = models.CharField(max_length=150)
    dni_vendedor = models.CharField(max_length=20, unique=True, null=True, blank=True)

    def __str__(self):
        return f"{self.nombre_vendedor} {self.apellido_vendedor}"

# 7. Cliente_Local_Movil __________________________________________________________________________________________
# core/models.py

class ClienteMovilLocal(models.Model):
    nombre_cliente_movil_local = models.CharField(max_length=150)
    apellido_cliente_movil_local = models.CharField(max_length=150)
    telefono_cliente_movil_local = models.CharField(max_length=20, blank=True, null=True)
    email_cliente_movil_local = models.EmailField(max_length=150, blank=True, null=True)
    direccion_cliente_movil_local = models.CharField(max_length=150, blank=True, null=True)
    dni_cliente_movil_local = models.CharField(max_length=20)  # puede repetirse
    observaciones_cliente_movil_local = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'core_cliente_movil_local'
        verbose_name = "Cliente móvil local"
        verbose_name_plural = "Clientes móviles locales"

    def __str__(self):
        return f"{self.nombre_cliente_movil_local} {self.apellido_cliente_movil_local}"

    

# 8. Compra ___________________________________________________________________________________________________
# core/models.py

class Compra(models.Model):
    ESTADOS = [
        ('pendiente', 'Pendiente'),
        ('en_proceso', 'En proceso'),
        ('completada', 'Completada'),
        ('cancelada', 'Cancelada'),
    ]

    id_cliente_movil_local = models.ForeignKey(
        'ClienteMovilLocal', 
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    id_vendedor = models.ForeignKey(Vendedor, on_delete=models.CASCADE)
    fecha = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='pendiente')

    def __str__(self):
        return f"Compra {self.id} - {self.estado}"



# 9. Compra_Producto _____________________________________________________________________________________
class CompraProducto(models.Model):
    id_compra = models.ForeignKey(Compra, on_delete=models.CASCADE)
    id_producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.IntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        unique_together = ('id_compra', 'id_producto')

# 10. Venta ________________________________________________________________________________________________
class Venta(models.Model):
    id_compra = models.OneToOneField(Compra, on_delete=models.CASCADE)
    id_vendedor = models.ForeignKey(Vendedor, on_delete=models.SET_NULL, null=True)
    monto_total = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_venta = models.DateTimeField(auto_now_add=True)

# 11. Factura _______________________________________________________________________________________________
class Factura(models.Model):
    ESTADOS = [
        ('Activo', 'Activo'),
        ('Cancelado', 'Cancelado'),
        ('Proceso', 'Proceso')
    ]
    id_venta = models.OneToOneField(Venta, on_delete=models.CASCADE)
    fecha = models.DateField()
    estado = models.CharField(max_length=20, choices=ESTADOS)

# 12. Envio __________________________________________________________________________________________________
class Envio(models.Model):
    compra = models.OneToOneField(Compra, on_delete=models.CASCADE, primary_key=True)
    empresa_flete = models.CharField(max_length=100)
    fecha_envio = models.DateField()
    fecha_recepcion = models.DateField(blank=True, null=True)


# 13. Cliente_local ___________________________________________________________________________________________
class ClienteLocal(models.Model):
    nombre_cliente = models.CharField(max_length=150)
    apellido_cliente = models.CharField(max_length=150)
    telefono_cliente = models.CharField(max_length=20, blank=True, null=True)
    email_cliente = models.EmailField(max_length=150, blank=True, null=True)
    direccion = models.CharField(max_length=150, blank=True, null=True)
    dni = models.CharField(max_length=20, blank=True, null=True)
    observaciones = models.TextField(blank=True, null=True)

    class Meta:
        db_table='core_cliente_local'
        verbose_name="Cliente local"
        verbose_name_plural="Cliente locales"

    def __str__(self):
        return  f"{self.nombre_cliente}{self.apellido_cliente}"
    

# 14. VentaLocal _____________________________________________________________________________________________________________________
class VentaLocal(models.Model):
    id_cliente_local = models.ForeignKey('core.ClienteLocal', on_delete=models.SET_NULL, null=True, blank=True)
    id_vendedor = models.ForeignKey('core.Vendedor', on_delete=models.SET_NULL, null=True, blank=True)
    monto_total = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_venta = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'core_venta_local'
        verbose_name = "Venta local"
        verbose_name_plural = "Ventas locales"

    def __str__(self):
        cliente = self.id_cliente_local or "Consumidor Final"
        return f"VentaLocal #{self.id} - {cliente} - ${self.monto_total:.2f}"

# 15. SolicitudContacto
class SolicitudContacto(models.Model):
    ESTADOS = [
        ('pendiente', 'Pendiente'),
        ('aceptada', 'Aceptada'),
        ('cancelada', 'Cancelada'),
    ]

    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name='solicitudes_contacto'
    )

    fecha_creacion = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='pendiente')

    vendedor_acepta = models.ForeignKey(
        Vendedor,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    def __str__(self):
        return f"{self.usuario.email} - {self.estado}"

class Marca(models.Model):
    nombre = models.CharField(max_length=100)

