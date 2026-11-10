from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.functions import Lower


class Profesor(models.Model):
    nombre = models.CharField(max_length=100)
    especialidad = models.CharField(max_length=100)
    correo = models.EmailField(unique=True)

    def clean(self):
        super().clean()
        self.correo = self.correo.strip().lower()
        if Profesor.objects.filter(correo__iexact=self.correo).exclude(pk=self.pk).exists():
            raise ValidationError({"correo": "Este correo ya pertenece a un profesor."})

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

    def clean(self):
        super().clean()
        if self.pk and self.capacidad is not None and self.capacidad < self.inscripciones.count():
            raise ValidationError({"capacidad": "La capacidad no puede ser menor a las inscripciones actuales."})

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

    def clean(self):
        # Los ModelForms del administrador llaman a clean antes de guardar.
        super().clean()
        self.correo_participante = self.correo_participante.strip().lower()
        actividad = Actividad.objects.filter(pk=self.actividad_id).first()
        if actividad is None:
            return  # La validación del ForeignKey informa el campo inválido.
        anterior = Inscripcion.objects.filter(pk=self.pk).first() if self.pk else None
        misma_actividad = anterior and anterior.actividad_id == self.actividad_id
        otras = actividad.inscripciones.exclude(pk=self.pk)
        if not misma_actividad and not actividad.activa:
            raise ValidationError({"actividad": "La actividad no está disponible."})
        if otras.count() >= actividad.capacidad:
            raise ValidationError({"actividad": "No quedan cupos disponibles."})
        if otras.filter(correo_participante__iexact=self.correo_participante).exists():
            raise ValidationError({"correo_participante": "Este correo ya está inscrito."})

    class Meta:
        constraints = [
            models.UniqueConstraint(
                Lower("correo_participante"), "actividad",
                name="inscripcion_unica_por_actividad_sin_mayusculas",
            )
        ]

    def __str__(self):
        return f"{self.nombre_participante} - {self.actividad.nombre}"


