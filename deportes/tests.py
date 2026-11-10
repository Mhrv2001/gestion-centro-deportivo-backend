from django.db import IntegrityError, transaction
from django.core.management import call_command
from django.test import TestCase
from io import StringIO
from django.forms import modelform_factory
from rest_framework.test import APITestCase

from .models import Actividad, Inscripcion, Profesor


class DatosEjemploTests(TestCase):
    def test_carga_idempotente_y_conserva_cambios(self):
        call_command("cargar_ejemplos", stdout=StringIO())
        self.assertEqual(Profesor.objects.count(), 3)
        self.assertEqual(Actividad.objects.count(), 3)
        actividad = Actividad.objects.get(nombre="Yoga")
        actividad.precio = 7500
        actividad.save()
        call_command("cargar_ejemplos", stdout=StringIO())
        actividad.refresh_from_db()
        self.assertEqual(actividad.precio, 7500)
        self.assertEqual(Actividad.objects.count(), 3)
        self.assertEqual(Inscripcion.objects.count(), 0)


class ProfesoresAPITests(APITestCase):
    def test_crud_y_persistencia(self):
        datos = {"nombre": "Laura", "especialidad": "Yoga", "correo": "LAURA@example.com"}
        respuesta = self.client.post("/api/profesores/", datos, format="json")
        self.assertEqual(respuesta.status_code, 201)
        url = f"/api/profesores/{respuesta.data['id']}/"
        self.assertEqual(Profesor.objects.get(pk=respuesta.data["id"]).correo, "laura@example.com")
        self.assertEqual(self.client.get(url).status_code, 200)
        datos["nombre"] = "Laura Fernández"
        self.assertEqual(self.client.put(url, datos, format="json").status_code, 200)
        self.assertEqual(self.client.patch(url, {"especialidad": "Pilates"}, format="json").status_code, 200)
        self.assertEqual(self.client.get(url).data["especialidad"], "Pilates")
        self.assertEqual(self.client.delete(url).status_code, 204)
        self.assertEqual(self.client.get(url).status_code, 404)

    def test_datos_obligatorios_y_correo_invalido(self):
        for datos in ({}, {"nombre": "Laura", "especialidad": "Yoga", "correo": "invalido"}):
            with self.subTest(datos=datos):
                self.assertEqual(self.client.post("/api/profesores/", datos, format="json").status_code, 400)
        self.assertFalse(Profesor.objects.exists())

    def test_busqueda_de_profesores(self):
        Profesor.objects.create(nombre="Laura", especialidad="Yoga", correo="laura@example.com")
        self.assertEqual(len(self.client.get("/api/profesores/?search=Yoga").data), 1)
        self.assertEqual(self.client.get("/api/profesores/?search=Boxeo").data, [])


class ActividadesAPITests(APITestCase):
    def setUp(self):
        self.profesor = Profesor.objects.create(nombre="Laura", especialidad="Yoga", correo="laura@example.com")
        self.datos = {"nombre": "Yoga", "categoria": "Bienestar", "profesor": self.profesor.pk,
                      "horario": "Lunes 10:00", "capacidad": 3, "precio": "5000.00", "activa": True}

    def test_crud_y_campos_calculados(self):
        respuesta = self.client.post("/api/actividades/", self.datos, format="json")
        self.assertEqual(respuesta.status_code, 201)
        url = f"/api/actividades/{respuesta.data['id']}/"
        self.assertEqual(respuesta.data["profesor_nombre"], "Laura")
        self.assertEqual(respuesta.data["cupos_disponibles"], 3)
        self.datos["horario"] = "Viernes 11:00"
        self.assertEqual(self.client.put(url, self.datos, format="json").status_code, 200)
        respuesta = self.client.patch(url, {"precio": "0.00", "cupos_disponibles": 100}, format="json")
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(respuesta.data["precio"], "0.00")
        self.assertEqual(respuesta.data["cupos_disponibles"], 3)
        self.assertEqual(self.client.delete(url).status_code, 204)
        self.assertEqual(self.client.get(url).status_code, 404)

    def test_campos_obligatorios(self):
        self.assertEqual(self.client.post("/api/actividades/", {}, format="json").status_code, 400)
        self.assertFalse(Actividad.objects.exists())

    def test_filtros_combinados(self):
        self.client.post("/api/actividades/", self.datos, format="json")
        respuesta = self.client.get(f"/api/actividades/?categoria=Bienestar&activa=true&profesor={self.profesor.pk}")
        self.assertEqual(len(respuesta.data), 1)
        self.assertEqual(self.client.get("/api/actividades/?categoria=Equipo&activa=true").data, [])


class ValidacionAdminTests(TestCase):
    def setUp(self):
        self.profesor = Profesor.objects.create(nombre="Laura", especialidad="Yoga", correo="laura@example.com")
        self.actividad = Actividad.objects.create(nombre="Yoga", categoria="Bienestar", profesor=self.profesor,
                                                  horario="Lunes 10:00", capacidad=1, precio=5000)
        self.formulario = modelform_factory(Inscripcion, fields=["actividad", "nombre_participante", "correo_participante"])
        self.datos = {"actividad": self.actividad.pk, "nombre_participante": "Ana", "correo_participante": "ANA@example.com"}

    def test_formulario_normaliza_correo_y_rechaza_sin_cupos(self):
        formulario = self.formulario(data=self.datos)
        self.assertTrue(formulario.is_valid(), formulario.errors)
        registro = formulario.save()
        self.assertEqual(registro.correo_participante, "ana@example.com")
        otro = self.formulario(data={**self.datos, "correo_participante": "bea@example.com"})
        self.assertFalse(otro.is_valid())
        self.assertIn("actividad", otro.errors)
        editar = self.formulario(data=self.datos, instance=registro)
        self.assertTrue(editar.is_valid(), editar.errors)

    def test_formulario_rechaza_actividad_inactiva(self):
        self.actividad.activa = False
        self.actividad.save()
        formulario = self.formulario(data=self.datos)
        self.assertFalse(formulario.is_valid())
        self.assertIn("actividad", formulario.errors)

    def test_formulario_rechaza_capacidad_menor_que_inscritos(self):
        self.actividad.capacidad = 2
        self.actividad.save()
        for nombre in ("Ana", "Bea"):
            Inscripcion.objects.create(actividad=self.actividad, nombre_participante=nombre, correo_participante=f"{nombre.lower()}@example.com")
        clase = modelform_factory(Actividad, fields=["capacidad"])
        formulario = clase(data={"capacidad": 1}, instance=self.actividad)
        self.assertFalse(formulario.is_valid())
        self.assertIn("capacidad", formulario.errors)

    def test_formulario_rechaza_correo_profesor_duplicado(self):
        clase = modelform_factory(Profesor, fields="__all__")
        formulario = clase(data={"nombre": "Otra", "especialidad": "Yoga", "correo": "LAURA@example.com"})
        self.assertFalse(formulario.is_valid())
        self.assertIn("correo", formulario.errors)


class InscripcionesAPITests(APITestCase):
    def setUp(self):
        self.profesor = Profesor.objects.create(
            nombre="Profesora de prueba", especialidad="Yoga", correo="profe@example.com"
        )
        self.actividad = Actividad.objects.create(
            nombre="Yoga", categoria="Bienestar", profesor=self.profesor,
            horario="Lunes 10:00", capacidad=1, precio="5000.00",
        )
        self.url_actividad = f"/api/actividades/{self.actividad.pk}/"

    def inscribir(self, correo="ana@example.com"):
        return self.client.post("/api/inscripciones/", {
            "actividad": self.actividad.pk,
            "nombre_participante": "Ana",
            "correo_participante": correo,
        }, format="json")

    def test_crear_consultar_y_cancelar_devuelve_cupo(self):
        respuesta = self.inscribir()
        self.assertEqual(respuesta.status_code, 201)
        url = f"/api/inscripciones/{respuesta.data['id']}/"
        self.assertEqual(self.client.get(url).status_code, 200)
        self.assertEqual(self.client.get(self.url_actividad).data["cupos_disponibles"], 0)
        self.assertEqual(self.client.delete(url).status_code, 204)
        self.assertEqual(self.actividad.cupos_disponibles, 1)
        self.assertFalse(Inscripcion.objects.exists())

    def test_sin_cupos_rechaza_otro_participante(self):
        self.assertEqual(self.inscribir().status_code, 201)
        self.assertEqual(self.inscribir("bea@example.com").status_code, 400)
        self.assertEqual(Inscripcion.objects.count(), 1)

    def test_correo_duplicado_con_mayusculas(self):
        self.actividad.capacidad = 3
        self.actividad.save()
        self.assertEqual(self.inscribir("ANA@example.com").status_code, 201)
        respuesta = self.inscribir("ana@example.com")
        self.assertEqual(respuesta.status_code, 400)
        self.assertIn("correo_participante", respuesta.data)

    def test_actividad_inactiva(self):
        self.actividad.activa = False
        self.actividad.save()
        self.assertEqual(self.inscribir().status_code, 400)

    def test_patch_conserva_campos_no_enviados_y_no_cuenta_su_cupo(self):
        registro = self.inscribir().data
        respuesta = self.client.patch(f"/api/inscripciones/{registro['id']}/", {
            "nombre_participante": "Ana Actualizada",
        }, format="json")
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(respuesta.data["nombre_participante"], "Ana Actualizada")
        self.assertEqual(respuesta.data["correo_participante"], "ana@example.com")
        self.assertEqual(respuesta.data["actividad"], self.actividad.pk)

    def test_put_inscripcion_llena_no_se_rechaza_a_si_misma(self):
        registro = self.inscribir().data
        respuesta = self.client.put(f"/api/inscripciones/{registro['id']}/", {
            "actividad": self.actividad.pk, "nombre_participante": "Ana",
            "correo_participante": "ANA@example.com",
        }, format="json")
        self.assertEqual(respuesta.status_code, 200)

    def test_transferencia_a_otra_actividad(self):
        registro = self.inscribir().data
        otra = Actividad.objects.create(
            nombre="Yoga tarde", categoria="Bienestar", profesor=self.profesor,
            horario="Lunes 18:00", capacidad=1, precio="5000.00",
        )
        url = f"/api/inscripciones/{registro['id']}/"
        otra.activa = False
        otra.save()
        self.assertEqual(self.client.patch(url, {"actividad": otra.pk}, format="json").status_code, 400)
        otra.activa = True
        otra.save()
        Inscripcion.objects.create(actividad=otra, nombre_participante="Bea", correo_participante="bea@example.com")
        self.assertEqual(self.client.patch(url, {"actividad": otra.pk}, format="json").status_code, 400)
        otra.inscripciones.all().delete()
        self.assertEqual(self.client.patch(url, {"actividad": otra.pk}, format="json").status_code, 200)
        self.assertEqual(self.actividad.cupos_disponibles, 1)
        self.assertEqual(otra.cupos_disponibles, 0)

    def test_no_reducir_capacidad_por_debajo_de_inscritos(self):
        self.actividad.capacidad = 2
        self.actividad.save()
        self.inscribir()
        self.inscribir("bea@example.com")
        respuesta = self.client.patch(self.url_actividad, {"capacidad": 1}, format="json")
        self.assertEqual(respuesta.status_code, 400)
        self.actividad.refresh_from_db()
        self.assertEqual(self.actividad.capacidad, 2)

    def test_datos_invalidos(self):
        self.assertEqual(self.inscribir("no-es-correo").status_code, 400)
        self.assertEqual(self.client.post("/api/inscripciones/", {}, format="json").status_code, 400)
        for datos in ({"capacidad": 0}, {"precio": "-1"}, {"profesor": 999999}):
            with self.subTest(datos=datos):
                self.assertEqual(self.client.patch(self.url_actividad, datos, format="json").status_code, 400)

    def test_filtros_actividades_e_inscripciones(self):
        self.inscribir()
        for filtro in ("categoria=bienestar", f"profesor={self.profesor.pk}", "activa=true", "search=Yoga"):
            with self.subTest(filtro=filtro):
                respuesta = self.client.get(f"/api/actividades/?{filtro}")
                self.assertEqual(respuesta.status_code, 200)
                self.assertEqual(len(respuesta.data), 1)
        self.assertEqual(self.client.get("/api/actividades/?activa=false").data, [])
        for filtro in (f"actividad={self.actividad.pk}", "correo=ANA@example.com"):
            self.assertEqual(len(self.client.get(f"/api/inscripciones/?{filtro}").data), 1)
        for ruta in ("actividades/?activa=quizas", "actividades/?profesor=abc", "inscripciones/?actividad=0"):
            self.assertEqual(self.client.get(f"/api/{ruta}").status_code, 400)

    def test_eliminar_profesor_protegido_y_actividad_en_cascada(self):
        self.inscribir()
        self.assertEqual(self.client.delete(f"/api/profesores/{self.profesor.pk}/").status_code, 400)
        self.assertEqual(self.client.delete(self.url_actividad).status_code, 204)
        self.assertFalse(Inscripcion.objects.exists())
        self.assertEqual(self.client.delete(f"/api/profesores/{self.profesor.pk}/").status_code, 204)

    def test_profesor_correo_duplicado(self):
        respuesta = self.client.post("/api/profesores/", {
            "nombre": "Otra persona", "especialidad": "Yoga", "correo": "PROFE@example.com",
        }, format="json")
        self.assertEqual(respuesta.status_code, 400)

    def test_restricciones_directas_de_la_base_de_datos(self):
        for campo, valor in (("precio", -1), ("capacidad", 0)):
            with self.subTest(campo=campo):
                with self.assertRaises(IntegrityError), transaction.atomic():
                    Actividad.objects.filter(pk=self.actividad.pk).update(**{campo: valor})
        self.inscribir()
        with self.assertRaises(IntegrityError), transaction.atomic():
            Inscripcion.objects.create(actividad=self.actividad, nombre_participante="Otra", correo_participante="ANA@example.com")

    def test_recurso_inexistente(self):
        for recurso in ("profesores", "actividades", "inscripciones"):
            self.assertEqual(self.client.get(f"/api/{recurso}/999999/").status_code, 404)
