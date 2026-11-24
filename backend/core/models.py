from django.conf import settings
from django.db import models


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