// Genera una colección importable en Postman. Node se utiliza solo para las pruebas.
const fs = require('node:fs');
const path = require('node:path');

function solicitud(name, method, ruta, datos, esperado, comprobaciones = []) {
  return {
    name,
    request: {
      method,
      header: datos ? [{ key: 'Content-Type', value: 'application/json' }] : [],
      url: '{{base_url}}/api/' + ruta,
      ...(datos ? { body: { mode: 'raw', raw: JSON.stringify(datos, null, 2), options: { raw: { language: 'json' } } } } : {}),
    },
    event: [{ listen: 'test', script: { type: 'text/javascript', exec: [
      `pm.test('HTTP ${esperado}', () => pm.response.to.have.status(${esperado}));`,
      `if (pm.response.code === ${esperado}) {`, ...comprobaciones, '}',
    ] } }],
  };
}

const profesor = { nombre: 'Profesor Demo{{marca}}', especialidad: 'Yoga', correo: 'profe-{{marca}}@example.com' };
const crearProfesor = solicitud('01 Crear profesor', 'POST', 'profesores/', profesor, 201, [
  "pm.collectionVariables.set('profesor_id', pm.response.json().id);",
  "pm.test('Correo guardado', () => pm.expect(pm.response.json().correo).to.include('@example.com'));",
]);
crearProfesor.event.unshift({ listen: 'prerequest', script: { type: 'text/javascript', exec: [
  "pm.collectionVariables.set('marca', Date.now().toString());",
] } });

const profesores = [
  crearProfesor,
  solicitud('02 Buscar profesor', 'GET', 'profesores/?search=Demo{{marca}}', null, 200, [
    "pm.test('Encuentra el profesor creado', () => pm.expect(pm.response.json().some(p => p.id === Number(pm.collectionVariables.get('profesor_id')))).to.eql(true));",
  ]),
  solicitud('03 Consultar profesor', 'GET', 'profesores/{{profesor_id}}/', null, 200),
  solicitud('04 Reemplazar profesor PUT', 'PUT', 'profesores/{{profesor_id}}/', { ...profesor, especialidad: 'Entrenamiento' }, 200),
  solicitud('05 Modificar profesor PATCH', 'PATCH', 'profesores/{{profesor_id}}/', { especialidad: 'Yoga' }, 200),
  solicitud('06 Rechazar correo invalido', 'POST', 'profesores/', { ...profesor, correo: 'invalido' }, 400),
  solicitud('07 Rechazar correo duplicado', 'POST', 'profesores/', { ...profesor, correo: 'PROFE-{{marca}}@example.com' }, 400),
];

const actividad = { nombre: 'Actividad Demo{{marca}}', categoria: 'Bienestar', profesor: '{{profesor_id}}',
  horario: 'Lunes 10:00', capacidad: 2, precio: '5000.00', activa: true };
const actividades = [
  solicitud('08 Crear actividad', 'POST', 'actividades/', actividad, 201, [
    "pm.collectionVariables.set('actividad_id', pm.response.json().id);",
    "pm.test('Cupos iniciales', () => pm.expect(pm.response.json().cupos_disponibles).to.eql(2));",
  ]),
  solicitud('09 Filtrar actividades', 'GET', 'actividades/?categoria=Bienestar&profesor={{profesor_id}}&activa=true', null, 200, [
    "pm.test('Filtro encuentra la actividad', () => pm.expect(pm.response.json().some(a => a.id === Number(pm.collectionVariables.get('actividad_id')))).to.eql(true));",
  ]),
  solicitud('10 Consultar actividad', 'GET', 'actividades/{{actividad_id}}/', null, 200),
  solicitud('11 Reemplazar actividad PUT', 'PUT', 'actividades/{{actividad_id}}/', { ...actividad, horario: 'Martes 11:00' }, 200),
  solicitud('12 Modificar precio PATCH', 'PATCH', 'actividades/{{actividad_id}}/', { precio: '5500.00' }, 200, [
    "pm.test('Precio actualizado', () => pm.expect(pm.response.json().precio).to.eql('5500.00'));",
  ]),
  solicitud('13 Rechazar precio negativo', 'PATCH', 'actividades/{{actividad_id}}/', { precio: '-1' }, 400),
  solicitud('14 Rechazar capacidad cero', 'PATCH', 'actividades/{{actividad_id}}/', { capacidad: 0 }, 400),
  solicitud('15 Rechazar filtro invalido', 'GET', 'actividades/?activa=quizas', null, 400),
  solicitud('16 Proteger profesor con actividades', 'DELETE', 'profesores/{{profesor_id}}/', null, 400),
];

const inscripcion = { actividad: '{{actividad_id}}', nombre_participante: 'Ana Demo', correo_participante: 'ana-{{marca}}@example.com' };
const inscripciones = [
  solicitud('17 Inscribir participante', 'POST', 'inscripciones/', inscripcion, 201, [
    "pm.collectionVariables.set('inscripcion_id', pm.response.json().id);",
  ]),
  solicitud('18 Consultar inscripcion', 'GET', 'inscripciones/{{inscripcion_id}}/', null, 200),
  solicitud('19 Filtrar inscripciones', 'GET', 'inscripciones/?actividad={{actividad_id}}&correo=ANA-{{marca}}@example.com', null, 200, [
    "pm.test('Inscripcion encontrada', () => pm.expect(pm.response.json()).to.have.lengthOf(1));",
  ]),
  solicitud('20 Rechazar inscripcion duplicada', 'POST', 'inscripciones/', { ...inscripcion, correo_participante: 'ANA-{{marca}}@example.com' }, 400, [
    "pm.test('Error de correo duplicado', () => pm.expect(pm.response.json()).to.have.property('correo_participante'));",
  ]),
  solicitud('21 Ajustar capacidad al total inscrito', 'PATCH', 'actividades/{{actividad_id}}/', { capacidad: 1 }, 200),
  solicitud('22 Rechazar actividad llena', 'POST', 'inscripciones/', { ...inscripcion, correo_participante: 'bea-{{marca}}@example.com' }, 400, [
    "pm.test('Error por actividad llena', () => pm.expect(pm.response.json()).to.have.property('actividad'));",
  ]),
  solicitud('23 Modificar nombre sin reenviar actividad', 'PATCH', 'inscripciones/{{inscripcion_id}}/', { nombre_participante: 'Ana Actualizada' }, 200, [
    "pm.test('Nombre actualizado', () => pm.expect(pm.response.json().nombre_participante).to.eql('Ana Actualizada'));",
  ]),
  solicitud('24 Reemplazar inscripcion PUT', 'PUT', 'inscripciones/{{inscripcion_id}}/', inscripcion, 200),
  solicitud('25 Desactivar actividad', 'PATCH', 'actividades/{{actividad_id}}/', { activa: false }, 200),
  solicitud('26 Rechazar nuevas inscripciones en actividad inactiva', 'POST', 'inscripciones/', { ...inscripcion, correo_participante: 'bea-{{marca}}@example.com' }, 400),
  solicitud('27 Corregir contacto de inscripcion existente en actividad inactiva', 'PATCH', 'inscripciones/{{inscripcion_id}}/', { nombre_participante: 'Ana Corregida' }, 200),
  solicitud('28 Cancelar inscripcion', 'DELETE', 'inscripciones/{{inscripcion_id}}/', null, 204),
  solicitud('29 Verificar devolucion de cupo', 'GET', 'actividades/{{actividad_id}}/', null, 200, [
    "pm.test('Cupo recuperado', () => pm.expect(pm.response.json().cupos_disponibles).to.eql(1));",
  ]),
  solicitud('30 Reactivar actividad', 'PATCH', 'actividades/{{actividad_id}}/', { activa: true }, 200),
  solicitud('31 Volver a inscribir tras cancelar', 'POST', 'inscripciones/', inscripcion, 201, [
    "pm.collectionVariables.set('inscripcion_id', pm.response.json().id);",
  ]),
  solicitud('32 Cancelar segunda inscripcion de prueba', 'DELETE', 'inscripciones/{{inscripcion_id}}/', null, 204),
  solicitud('33 Comprobar que fue eliminada', 'GET', 'inscripciones/{{inscripcion_id}}/', null, 404),
];
const limpieza = [
  solicitud('34 Eliminar actividad de prueba', 'DELETE', 'actividades/{{actividad_id}}/', null, 204),
  solicitud('35 Eliminar profesor de prueba', 'DELETE', 'profesores/{{profesor_id}}/', null, 204),
];

const coleccion = {
  info: { name: 'Centro deportivo - API REST', schema: 'https://schema.getpostman.com/json/collection/v2.1.0/collection.json',
    description: 'Ejecutar en orden con Collection Runner o Newman. Usa solamente datos ficticios propios de la prueba.' },
  variable: [{ key: 'base_url', value: 'http://127.0.0.1:8000' }, { key: 'marca', value: '' },
    { key: 'profesor_id', value: '' }, { key: 'actividad_id', value: '' }, { key: 'inscripcion_id', value: '' }],
  item: [{ name: '01 Profesores', item: profesores }, { name: '02 Actividades', item: actividades },
    { name: '03 Inscripciones y reglas de negocio', item: inscripciones }, { name: '04 Limpieza de datos propios de prueba', item: limpieza }],
};

const destino = path.join(__dirname, '..', 'postman', 'centro_deportivo.postman_collection.json');
fs.mkdirSync(path.dirname(destino), { recursive: true });
fs.writeFileSync(destino, JSON.stringify(coleccion, null, 2) + '\n', 'utf8');
console.log(destino);
