from django.core.validators import MinValueValidator
from django.db import models
from django.db.models.functions import Lower


class Profesor(models.Model):
    nombre = models.CharField(max_length=100)
    especialidad = models.CharField(max_length=100)
    correo = models.EmailField(unique=True)

    def __str__(self):
        return self.nombre


class Actividad(models.Model):
    nombre = models.CharField(max_length=100)
    categoria = models.CharField(max_length=100)
    profesor = models.ForeignKey(
        Profesor,
        on_delete=models.PROTECT,
        related_name="actividades",
    )
    horario = models.CharField(max_length=100)
    capacidad = models.PositiveIntegerField(
        validators=[MinValueValidator(1)]
    )
    precio = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )
    activa = models.BooleanField(default=True)

    class Meta:
        constraints = [
            models.CheckConstraint(condition=models.Q(capacidad__gte=1), name="capacidad_positiva"),
            models.CheckConstraint(condition=models.Q(precio__gte=0), name="precio_no_negativo"),
        ]

    @property
    def cupos_disponibles(self):
        return max(self.capacidad - self.inscripciones.count(), 0)

    def __str__(self):
        return self.nombre


class Inscripcion(models.Model):
    actividad = models.ForeignKey(
        Actividad,
        on_delete=models.CASCADE,
        related_name="inscripciones",
    )
    nombre_participante = models.CharField(max_length=100)
    correo_participante = models.EmailField()
    fecha_inscripcion = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                Lower("correo_participante"), "actividad",
                name="inscripcion_unica_por_actividad_sin_mayusculas",
            )
        ]

    def __str__(self):
        return f"{self.nombre_participante} - {self.actividad.nombre}"


