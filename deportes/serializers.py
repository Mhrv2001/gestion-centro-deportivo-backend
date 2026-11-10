from rest_framework import serializers

from .models import Actividad, Inscripcion, Profesor


class ProfesorSerializer(serializers.ModelSerializer):
    def validate_correo(self, correo):
        correo = correo.strip().lower()
        profesores = Profesor.objects.filter(correo__iexact=correo)
        if self.instance:
            profesores = profesores.exclude(pk=self.instance.pk)
        if profesores.exists():
            raise serializers.ValidationError("Este correo ya pertenece a un profesor.")
        return correo

    class Meta:
        model = Profesor
        fields = "__all__"


class ActividadSerializer(serializers.ModelSerializer):
    profesor_nombre = serializers.CharField(
        source="profesor.nombre",
        read_only=True,
    )
    cupos_disponibles = serializers.IntegerField(read_only=True)

    class Meta:
        model = Actividad
        fields = [
            "id",
            "nombre",
            "categoria",
            "profesor",
            "profesor_nombre",
            "horario",
            "capacidad",
            "cupos_disponibles",
            "precio",
            "activa",
        ]

    def validate_capacidad(self, capacidad):
        if self.instance:
            inscritos = self.instance.inscripciones.count()

            if capacidad < inscritos:
                raise serializers.ValidationError(
                    "La capacidad no puede ser menor a las inscripciones actuales."
                )

        return capacidad


class InscripcionSerializer(serializers.ModelSerializer):
    actividad_nombre = serializers.CharField(
        source="actividad.nombre",
        read_only=True,
    )

    class Meta:
        model = Inscripcion
        fields = [
            "id",
            "actividad",
            "actividad_nombre",
            "nombre_participante",
            "correo_participante",
            "fecha_inscripcion",
        ]
        read_only_fields = ["fecha_inscripcion"]

    def validate(self, datos):
        actividad = datos.get("actividad", getattr(self.instance, "actividad", None))
        correo = datos.get(
            "correo_participante", getattr(self.instance, "correo_participante", "")
        ).strip().lower()
        if actividad is None:
            raise serializers.ValidationError({"actividad": "Selecciona una actividad."})

        misma_actividad = self.instance and self.instance.actividad_id == actividad.pk
        inscripciones = actividad.inscripciones.all()
        if self.instance:
            inscripciones = inscripciones.exclude(pk=self.instance.pk)

        if not misma_actividad and not actividad.activa:
            raise serializers.ValidationError(
                {"actividad": "La actividad no está disponible."}
            )

        if inscripciones.count() >= actividad.capacidad:
            raise serializers.ValidationError(
                {"actividad": "No quedan cupos disponibles."}
            )

        if inscripciones.filter(
            correo_participante__iexact=correo
        ).exists():
            raise serializers.ValidationError(
                {"correo_participante": "Este correo ya está inscrito."}
            )

        datos["correo_participante"] = correo
        return datos
