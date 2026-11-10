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

const coleccion = {
  info: { name: 'Centro deportivo - API REST', schema: 'https://schema.getpostman.com/json/collection/v2.1.0/collection.json',
    description: 'Ejecutar en orden con Collection Runner o Newman. Usa solamente datos ficticios propios de la prueba.' },
  variable: [{ key: 'base_url', value: 'http://127.0.0.1:8000' }, { key: 'marca', value: '' }, { key: 'profesor_id', value: '' }],
  item: [{ name: '01 Profesores', item: profesores }],
};

const destino = path.join(__dirname, '..', 'postman', 'centro_deportivo.postman_collection.json');
fs.mkdirSync(path.dirname(destino), { recursive: true });
fs.writeFileSync(destino, JSON.stringify(coleccion, null, 2) + '\n', 'utf8');
console.log(destino);
