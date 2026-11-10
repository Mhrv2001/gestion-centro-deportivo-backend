from django.core.management.base import BaseCommand
from django.db import transaction

from deportes.models import Actividad, Profesor


class Command(BaseCommand):
    help = "Carga tres actividades ficticias sin sobrescribir datos existentes."

    @transaction.atomic
    def handle(self, *args, **options):
        ejemplos = [
            ("Carlos Pérez", "Fútbol", "Equipo", "Lunes y miércoles 18:00", 15, 6000),
            ("María González", "Natación", "Acuáticos", "Martes y jueves 17:00", 10, 9000),
            ("Laura Fernández", "Yoga", "Bienestar", "Miércoles y viernes 10:00", 12, 5000),
        ]
        for indice, (nombre, deporte, categoria, horario, capacidad, precio) in enumerate(ejemplos, 1):
            profesor, _ = Profesor.objects.get_or_create(
                correo=f"profesor{indice}@example.com",
                defaults={"nombre": nombre, "especialidad": deporte},
            )
            actividad, creada = Actividad.objects.get_or_create(
                nombre=deporte, profesor=profesor,
                defaults={"categoria": categoria, "horario": horario,
                          "capacidad": capacidad, "precio": precio},
            )
            estado = "creada" if creada else "existente"
            self.stdout.write(f"{actividad.pk}: {actividad.nombre} ({estado})")
