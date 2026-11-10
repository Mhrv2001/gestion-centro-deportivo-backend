"""Ejecuta la colección Postman con Newman y SQLite temporal, sin datos personales."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone
from urllib.error import URLError
from urllib.request import urlopen


RAIZ = Path(__file__).resolve().parent.parent


def main():
    npx = shutil.which("npx.cmd" if os.name == "nt" else "npx")
    if not npx:
        raise SystemExit("Instala Node.js con npm para ejecutar Newman, o importa la colección en Postman.")
    base_url = "http://127.0.0.1:8765"
    with tempfile.TemporaryDirectory(prefix="centro-deportivo-api-") as temporal:
        carpeta = Path(temporal)
        entorno = {**os.environ, "DJANGO_DB_PATH": str(carpeta / "prueba.sqlite3")}
        subprocess.run([sys.executable, "manage.py", "migrate", "--noinput"], cwd=RAIZ, env=entorno, check=True)
        with (carpeta / "servidor.log").open("w", encoding="utf-8") as log:
            servidor = subprocess.Popen(
                [sys.executable, "manage.py", "runserver", "127.0.0.1:8765", "--noreload"],
                cwd=RAIZ, env=entorno, stdout=log, stderr=subprocess.STDOUT,
            )
            try:
                for _ in range(30):
                    if servidor.poll() is not None:
                        raise RuntimeError((carpeta / "servidor.log").read_text(encoding="utf-8"))
                    try:
                        with urlopen(base_url + "/api/", timeout=1) as respuesta:
                            if respuesta.status == 200:
                                break
                    except (URLError, TimeoutError):
                        time.sleep(0.5)
                else:
                    raise RuntimeError("El servidor de prueba no respondió. Revisa si el puerto 8765 está ocupado.")
                informe = carpeta / "newman.json"
                resultado = subprocess.run([
                    npx, "--yes", "newman@6.2.1", "run",
                    str(RAIZ / "postman" / "centro_deportivo.postman_collection.json"),
                    "--env-var", "base_url=" + base_url,
                    "--reporters", "cli,json", "--reporter-json-export", str(informe),
                    "--timeout-request", "10000", "--bail",
                ], cwd=RAIZ)
                if not informe.exists():
                    raise RuntimeError("Newman no generó el informe. Revisa la conexión con npm y su salida.")
                datos = json.loads(informe.read_text(encoding="utf-8"))
                run = datos["run"]
                solicitudes = []
                for ejecucion in run["executions"]:
                    respuesta = ejecucion.get("response") or {}
                    contenido = respuesta.get("stream", {}).get("data", [])
                    texto = bytes(contenido).decode("utf-8", errors="replace")
                    try:
                        cuerpo = json.loads(texto) if texto else None
                    except json.JSONDecodeError:
                        cuerpo = texto
                    solicitudes.append({
                        "nombre": ejecucion["item"]["name"],
                        "metodo": ejecucion["request"]["method"],
                        "estado_http": respuesta.get("code"), "respuesta_json": cuerpo,
                        "comprobaciones": [{"nombre": a["assertion"], "correcta": not bool(a.get("error"))}
                                           for a in ejecucion.get("assertions", [])],
                    })
                resumen = {
                    "fecha_utc": datetime.now(timezone.utc).isoformat(),
                    "herramienta": "Newman 6.2.1 (ejecutor de colecciones Postman)",
                    "base_datos": "SQLite temporal independiente; eliminada al finalizar",
                    "solicitudes": run["stats"]["requests"],
                    "aserciones": run["stats"]["assertions"],
                    "fallos": len(run["failures"]), "resultados": solicitudes,
                }
                destino = RAIZ / "evidencias" / "postman_resultado.json"
                destino.parent.mkdir(exist_ok=True)
                destino.write_text(json.dumps(resumen, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
                print(f"Evidencia guardada: {destino}")
                if resultado.returncode or run["failures"]:
                    raise SystemExit(1)
            finally:
                servidor.terminate()
                try:
                    servidor.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    servidor.kill()
                    servidor.wait()


if __name__ == "__main__":
    main()
