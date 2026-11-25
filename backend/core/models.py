from django.conf import settings
from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator


ESTADOS = [(s, s.capitalize()) for s in ['PENDIENTE', 'APROBADO', 'RECHAZADO', 'RETIRADO', 'CANCELADO', 'FINALIZADO']]


class Propuesta(models.Model):
    nombre = models.CharField(max_length=150)
    descripcion = models.TextField(max_length=3000)
    estado = models.CharField(max_length=12, choices=ESTADOS[:4], default='PENDIENTE')
    autor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)

    class Meta:
        abstract = True


class Comunidad(Propuesta):
    def __str__(self):
        return self.nombre


class Lugar(Propuesta):
    zona = models.CharField(max_length=30, choices=[('puerto-montt', 'Puerto Montt'), ('puerto-varas', 'Puerto Varas')])
    latitud = models.FloatField(validators=[MinValueValidator(-90), MaxValueValidator(90)])
    longitud = models.FloatField(validators=[MinValueValidator(-180), MaxValueValidator(180)])

    def __str__(self):
        return self.nombre


class Perfil(models.Model):
    usuario = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(max_length=1000, blank=True)
    intereses = models.CharField(max_length=200, blank=True)
    verificado = models.BooleanField(default=False)


class Actividad(models.Model):
    class Zona(models.TextChoices):
        PUERTO_MONTT = "puerto-montt", "Puerto Montt"
        PUERTO_VARAS = "puerto-varas", "Puerto Varas"

    class Categoria(models.TextChoices):
        DEPORTES = "Deportes", "Deportes"
        CULTURA = "Cultura", "Cultura"
        FERIAS = "Ferias y Comunidad", "Ferias y Comunidad"
        AIRE_LIBRE = "Aire libre", "Aire libre"

    titulo = models.CharField(max_length=150)
    categoria = models.CharField(
            max_length=50,
            choices=Categoria.choices,
            default=Categoria.FERIAS,
        )
    zona = models.CharField(
            max_length=30,
            choices=Zona.choices,
            default=Zona.PUERTO_MONTT,
        )
    latitud = models.FloatField()
    longitud = models.FloatField()
    todo_el_ano = models.BooleanField(default=False)
    horario = models.CharField(max_length=120, blank=True)
    hora_inicio = models.TimeField(null=True, blank=True)
    hora_fin = models.TimeField(null=True, blank=True)
    fecha_hora = models.DateTimeField(null=True, blank=True)
    descripcion = models.TextField(blank=True)
    destacado = models.BooleanField(default=False)
    fin = models.DateTimeField(null=True, blank=True)
    estado = models.CharField(max_length=12, choices=ESTADOS, default='PENDIENTE')
    comunidad = models.ForeignKey(Comunidad, on_delete=models.PROTECT, null=True)
    lugar = models.ForeignKey(Lugar, on_delete=models.PROTECT, null=True)
    aperturas = models.PositiveIntegerField(default=0)
    
    creado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="actividades_creadas",
    )
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-destacado", "fecha_hora", "-creado_en"]

    def __str__(self):
        return f"{self.titulo} ({self.get_zona_display()})"

    def clean(self):
        if not self.todo_el_ano and (
            not self.fecha_hora or not self.fin or self.fin <= self.fecha_hora
        ):
            raise ValidationError('El fin debe ser posterior al inicio.')
        if self.todo_el_ano and not self.horario.strip():
            raise ValidationError('Indica el horario habitual.')
        if self.todo_el_ano and (
            not self.hora_inicio or not self.hora_fin or self.hora_fin <= self.hora_inicio
        ):
            raise ValidationError('Indica un horario válido dentro del mismo día.')
        if self.comunidad_id and self.comunidad.estado != 'APROBADO':
            raise ValidationError('La comunidad debe estar aprobada.')
        if self.lugar_id and self.lugar.estado != 'APROBADO':
            raise ValidationError('El lugar debe estar aprobado.')


class Asistencia(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    actividad = models.ForeignKey(Actividad, on_delete=models.CASCADE, related_name='asistencias')

    class Meta:
        constraints = [models.UniqueConstraint(fields=['usuario', 'actividad'], name='asistencia_unica')]


class Publicacion(models.Model):
    comunidad = models.ForeignKey(Comunidad, on_delete=models.PROTECT, related_name='publicaciones')
    autor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    texto = models.TextField(max_length=3000)
    estado = models.CharField(max_length=12, choices=ESTADOS[:4], default='APROBADO')
    fecha = models.DateTimeField(auto_now_add=True)


class Comentario(models.Model):
    publicacion = models.ForeignKey(Publicacion, on_delete=models.PROTECT, related_name='comentarios')
    autor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    texto = models.TextField(max_length=1500)
    estado = models.CharField(max_length=12, choices=ESTADOS[:4], default='APROBADO')
    fecha = models.DateTimeField(auto_now_add=True)


class Reporte(models.Model):
    tipo = models.CharField(max_length=20)
    objeto_id = models.PositiveIntegerField()
    autor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    motivo = models.CharField(max_length=500)
    estado = models.CharField(max_length=10, default='ABIERTO')
    resolucion = models.CharField(max_length=500, blank=True)
    responsable = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, null=True, related_name='reportes_resueltos')
    resuelto_en = models.DateTimeField(null=True)


class Auditoria(models.Model):
    tipo = models.CharField(max_length=20)
    objeto_id = models.PositiveIntegerField()
    responsable = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    decision = models.CharField(max_length=30)
    motivo = models.CharField(max_length=500)
    fecha = models.DateTimeField(auto_now_add=True)
