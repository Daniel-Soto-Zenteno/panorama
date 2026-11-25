from django.conf import settings
from django.db import models


class Comunidad(models.Model):
    nombre = models.CharField(max_length=80, unique=True)
    categoria = models.CharField(max_length=50)
    descripcion = models.TextField(blank=True, max_length=1200)
    creado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    aprobado = models.BooleanField(default=False)
    rechazada = models.BooleanField(default=False)
    creado_en = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre


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
    fecha_hora = models.DateTimeField(null=True, blank=True)
    descripcion = models.TextField(blank=True)
    destacado = models.BooleanField(default=False)
    comunidad = models.ForeignKey(Comunidad, on_delete=models.SET_NULL, null=True, blank=True, related_name='publicaciones')
    imagen = models.FileField(upload_to='publicaciones/%Y/%m/', blank=True)
    estado = models.CharField(max_length=12, choices=[('published', 'Publicada'), ('pending', 'Pendiente'), ('rejected', 'Rechazada')], default='published')
    ritmo = models.CharField(max_length=10, choices=[('active', 'Más movimiento'), ('calm', 'Algo tranquilo')], default='calm')
    tipo = models.CharField(max_length=10, choices=[('event', 'Actividad o evento'), ('place', 'Lugar de encuentro')], default='event')
    lugar = models.CharField(max_length=150, blank=True)
    es_ejemplo = models.BooleanField(default=False)
    
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


class Conversacion(models.Model):
    actividad = models.ForeignKey(Actividad, on_delete=models.CASCADE, related_name='comentarios')
    autor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    texto = models.TextField(max_length=2000)
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['creado_en', 'id']


class Perfil(models.Model):
    usuario = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='perfil')
    nombre = models.CharField(max_length=40, blank=True)
    biografia = models.CharField(max_length=180, blank=True)


class Guardado(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='guardados')
    actividad = models.ForeignKey(Actividad, on_delete=models.CASCADE, related_name='guardados')

    class Meta:
        constraints = [models.UniqueConstraint(fields=['usuario', 'actividad'], name='guardado_unico_por_usuario')]


class Reporte(models.Model):
    actividad = models.ForeignKey(Actividad, on_delete=models.CASCADE, related_name='reportes')
    autor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    motivo = models.CharField(max_length=60)
    detalle = models.CharField(max_length=500, blank=True)
    resuelto = models.BooleanField(default=False)
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['creado_en', 'id']
