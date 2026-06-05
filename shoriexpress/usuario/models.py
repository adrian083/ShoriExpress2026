from django.db import models

# IMPORTANTE: Hemos eliminado "from rol.models import Rol" para evitar el ImportError circular.
# Django resolverá la relación automáticamente usando el nombre de la app y el modelo.

class Usuario(models.Model):
    """
    Entidad que representa tanto a Clientes como a Empleados (Cajeros, Administradores).
    """
    TIPO_DOC_CHOICES = [
        ('CC', 'Cédula de Ciudadanía'),
        ('TI', 'Tarjeta de Identidad'),
        ('CE', 'Cédula de Extranjería'),
        ('PEP', 'Permiso Especial de Permanencia'),
    ]
    
    ESTADO_CHOICES = [
        ('activo', 'Activo'),
        ('inactivo', 'Inactivo'),
    ]

    # Identificación
    tipo_documento = models.CharField(max_length=10, choices=TIPO_DOC_CHOICES, default='CC')
    documento = models.CharField(max_length=15, unique=True)
    
    # Información Personal
    primer_nombre = models.CharField(max_length=40)
    apellido = models.CharField(max_length=40)
    correo = models.EmailField(max_length=100, unique=True)
    telefono = models.CharField(max_length=20, null=True, blank=True)
    direccion = models.CharField(max_length=100)
    
    # Credenciales y Perfil
    nombre_usuario = models.CharField(max_length=50, unique=True)
    # Guardar con hash (PBKDF2) vía cuentas.password_utils; login acepta legado en texto plano.
    contrasena = models.CharField(max_length=255)
    ultima_actualizacion_password = models.DateTimeField(
        auto_now_add=True,
        help_text="Fecha de última actualización de contraseña",
    )
    
    # RELACIÓN CORREGIDA: Usamos 'app_name.Modelo' como string
    rol = models.ForeignKey(
        'rol.Rol', 
        on_delete=models.PROTECT, 
        related_name='usuarios'
    )
    
    # Lógica de Negocio (Fidelización y Auditoría)
    puntos_acumulados = models.PositiveIntegerField(default=0)
    bonos_fidelidad = models.PositiveIntegerField(
        default=0,
        help_text="Bonos ganados (ej. compras iguales o superiores al umbral configurado)",
    )
    estado = models.CharField(max_length=10, choices=ESTADO_CHOICES, default='activo')
    fecha_registro = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Cap bonos_fidelidad a máximo 10
        if self.bonos_fidelidad > 10:
            self.bonos_fidelidad = 10
        super().save(*args, **kwargs)

    def clean(self):
        from django.core.exceptions import ValidationError
        import re
        USERNAME_RE = re.compile(r'^[A-Za-z0-9_.]{4,50}$')
        DOCUMENTO_RE = re.compile(r'^[A-Za-z0-9]{5,20}$')
        NOMBRE_RE = re.compile(r'^[A-Za-zÁÉÍÓÚáéíóúÑñ\s]{2,40}$')
        TELEFONO_RE = re.compile(r'^[0-9]{10}$')

        if not USERNAME_RE.fullmatch(self.nombre_usuario):
            raise ValidationError('El usuario debe tener 4 a 50 caracteres y solo usar letras, números, punto o guion bajo.')
        if not DOCUMENTO_RE.fullmatch(self.documento):
            raise ValidationError('El documento debe tener entre 5 y 20 caracteres alfanuméricos, sin espacios.')
        if not NOMBRE_RE.fullmatch(self.primer_nombre):
            raise ValidationError('El nombre solo puede contener letras y espacios (2 a 40 caracteres).')
        if not NOMBRE_RE.fullmatch(self.apellido):
            raise ValidationError('El apellido solo puede contener letras y espacios (2 a 40 caracteres).')
        if self.telefono and not TELEFONO_RE.fullmatch(self.telefono):
            raise ValidationError('El teléfono debe tener exactamente 10 dígitos numéricos.')
        if len(self.direccion) < 5 or len(self.direccion) > 100:
            raise ValidationError('La dirección debe tener entre 5 y 100 caracteres.')

    class Meta:
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"
        db_table = "usuario_usuario" # Mantiene compatibilidad con tu SQL

    def __str__(self):
        # Al momento de ejecutarse, self.rol ya será un objeto accesible
        return f"{self.primer_nombre} {self.apellido} - {self.rol.nombre_rol}"