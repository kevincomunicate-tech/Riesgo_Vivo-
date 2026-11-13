# RiesgoVivo

Aplicación web desarrollada en Python y Django que permite consultar e interpretar el historial de emergencias reportadas por la Unidad Nacional para la Gestión del Riesgo de Desastres (UNGRD) a partir de datos abiertos de datos.gov.co.

> Hackathon — Innovación con Datos Abiertos de Colombia (Python + Django). Lema: *Construye, aprende e innova.*

---

## 1. Descubrimiento del problema

### Nombre de la aplicación
**RiesgoVivo**

### Problema / Hipótesis de necesidad
Las comunidades, juntas de acción comunal y funcionarios municipales tienen acceso a los datos abiertos de emergencias de la UNGRD, pero carecen de una herramienta sencilla que les permita filtrar y comprender el historial de eventos de su territorio de forma rápida y clara. Existe información pública valiosa, pero no una forma simple de convertirla en conocimiento útil para la prevención del riesgo.

> **Importante:** esta necesidad **no fue contrastada con usuarios reales** durante el hackathon; se presenta como **hipótesis**, no como un hecho comprobado.

### Usuario / Beneficiario potencial
- Líderes de juntas de acción comunal
- Funcionarios de gestión del riesgo de municipios
- Ciudadanos interesados en conocer el historial de emergencias de su zona

### Fuente de datos
- **Conjunto de datos:** Emergencias UNGRD V2
- **URL:** https://www.datos.gov.co/en/en/Environment-and-Sustainable-Development/Emergencias-UNGRD-V2/2343-nuqp
- **Entidad publicadora:** Unidad Nacional para la Gestión del Riesgo de Desastres – UNGRD
- **Cobertura:** Nacional (32 departamentos en el archivo descargado)
- **Periodo del archivo descargado:** 01/01/2025 – 31/12/2025, **6.506 registros**, 61 columnas
- **Campos relevantes utilizados:** FECHA, DEPARTAMENTO, MUNICIPIO, EVENTO, FALLECIDOS, HERIDOS, DESAPARECIDOS, PERSONAS, FAMILIAS, VIVIENDAS DESTRUIDAS
- **Modalidad de acceso:** Opción B — archivo CSV descargado del portal el 13/11/2026 (`data/emergencias_ungrd.csv`). Se usa el **archivo completo, no una muestra**.

### Funcionalidad principal
Permitir al usuario filtrar emergencias por departamento y municipio, y visualizar un resumen claro del historial (cantidad de eventos, personas y familias afectadas, tipos de eventos más frecuentes).

### Valor esperado
Que cualquier persona pueda responder en menos de un minuto la pregunta:
**“¿Qué tan afectado ha sido mi municipio históricamente y por qué tipo de emergencias?”**

### Limitaciones conocidas
- Los datos se actualizan de forma periódica (no son en tiempo real); el archivo descargado cubre solo 2025.
- Solo se incluyen emergencias **reportadas** a la UNGRD; puede haber subregistro de eventos pequeños.
- Algunos registros pueden tener campos vacíos o incompletos: los valores numéricos vacíos se cuentan como 0.
- Se utiliza un archivo CSV descargado del portal (no se consume la API en tiempo real).
- Las coordenadas geográficas no siempre están completas (por eso no se usa un mapa).
- Los nombres de municipios vienen sin tildes y en mayúsculas, tal como los publica la fuente.
- La aplicación muestra historia reportada; **no es un pronóstico ni una evaluación oficial del riesgo**.

---

## 2. Planificación (Scrum adaptado)

### Product Goal (Objetivo del Producto)
Permitir a ciudadanos y funcionarios municipales consultar de forma simple el historial de emergencias de su territorio usando datos reales de la UNGRD, para apoyar la toma de conciencia y la prevención del riesgo.

### Product Backlog

**PBI-1 — Prioridad: High**
Como ciudadano o líder comunitario, quiero filtrar emergencias por departamento y municipio, para ver rápidamente el historial de eventos de mi territorio.

**Criterios de aceptación:**
- Existe un formulario con selección de departamento y municipio.
- Al elegir un departamento, la lista de municipios muestra solo los de ese departamento.
- Al enviar el formulario se muestran resultados reales o un mensaje claro: *“No se encontraron emergencias con los filtros seleccionados”*.
- Se visualizan totales de eventos, personas afectadas y una lista de eventos (fecha, evento, departamento, municipio, personas afectadas).
- Una combinación inválida (p. ej. municipio de otro departamento) muestra un aviso y no provoca error.

**PBI-2 — Prioridad: High**
Como usuario, quiero ver un resumen numérico y los tipos de eventos más frecuentes, para entender el patrón de riesgo de mi zona.

**Criterios de aceptación:**
- Se muestran tarjetas o indicadores con totales (eventos, personas, familias, fallecidos y heridos).
- Se listan los 5 tipos de evento más comunes en el resultado filtrado, con su porcentaje.

**PBI-3 — Prioridad: Medium**
Como funcionario municipal, quiero ver estadísticas y gráficos del resultado filtrado, para identificar cuándo ocurren las emergencias y qué tan concentrado está su impacto.

**Criterios de aceptación:**
- Se muestran promedio, mediana, desviación estándar, percentil 90 y máximo de personas afectadas por evento.
- Se muestran gráficos **interactivos** (no imágenes) calculados desde el CSV filtrado: top de eventos, evolución mensual y distribución de personas afectadas.
- Los gráficos tienen tooltips, leyenda para mostrar/ocultar series, cambio de métrica (eventos/personas) y clic en una barra para filtrar la tabla.
- Si no hay datos, el gráfico queda vacío y la página no falla.

**PBI-4 — Prioridad: Low (fuera del Sprint)**
Como usuario, quiero comparar dos municipios lado a lado, para saber cuál ha tenido más afectación.

### Sprint Goal
Tener un recorrido web funcional completo en el que el usuario pueda filtrar por departamento y/o municipio y obtener un resumen comprensible de emergencias reales de la UNGRD, con manejo adecuado de resultados vacíos.

### Sprint Backlog
Sprint Goal + PBI-1, PBI-2 y PBI-3. Plan de implementación:

| Trabajo | PBI | Verificación |
|---|---|---|
| Descargar CSV y documentar su origen en `data/` | 1 | Archivo presente, fuente en README y en el pie de la página |
| `services.py`: lectura con pandas, limpieza, validación de columnas, filtrado | 1 | Tests de carga, archivo ausente y columnas faltantes |
| Formulario Django + select dependiente (`filtros.js`) | 1 | Prueba manual en navegador + test de combinación inválida |
| Resumen numérico y top 5 de eventos | 2 | Test de totales y top con CSV de prueba |
| Estadística descriptiva (numpy), datos de gráficos (`services.chart_data`) y gráficos interactivos (`graficos.js`, Chart.js) | 3 | Test de los datos de los gráficos + prueba manual en navegador |
| Plantillas Bootstrap 5, fuente y limitaciones visibles | 1, 2 | Revisión visual en navegador |
| README, `requirements.txt`, `.gitignore`, tests | — | `python manage.py test` |

### Definition of Done (DoD)
- Django inicia sin errores bloqueantes.
- Se puede completar el recorrido principal desde el navegador.
- La aplicación utiliza datos reales de datos.gov.co y declara su fuente.
- Los criterios de aceptación del trabajo completado se cumplen.
- Los resultados vacíos o entradas inválidas no provocan fallos.
- Se ejecutó y registró al menos una verificación funcional real del recorrido principal.
- `python manage.py test` se ejecutó y su resultado está registrado con honestidad.
- El README permite a otra persona instalar y ejecutar el proyecto.
- Los cambios están integrados en la rama principal mediante Pull Request revisado.
- GitHub Issues y Projects reflejan el estado verdadero del trabajo.

---

## 3. Cómo instalar y ejecutar el proyecto

### Requisitos previos
- Python 3.11 o superior (pandas 3.1 lo exige; probado con Python 3.14.10)
- pip
- Git (opcional pero recomendado)

### Pasos de instalación

1. Clonar el repositorio (o descargar el código):
   ```bash
   git clone https://github.com/kevincomunicate-tech/Riesgo_Vivo-.git
   cd Riesgo_Vivo-
   ```

2. Crear y activar un entorno virtual:
   ```bash
   python -m venv .venv
   # Windows
   .venv\Scripts\activate
   # macOS / Linux
   source .venv/bin/activate
   ```

3. Instalar dependencias:
   ```bash
   pip install -r requirements.txt
   ```

4. Verificar que existe el archivo de datos `data/emergencias_ungrd.csv` (ya viene en el repositorio). Si falta, descárgalo así:
   - Abre la URL del conjunto, pulsa **Export → CSV**, y guárdalo como `data/emergencias_ungrd.csv`, o
   - Descarga directa: `https://www.datos.gov.co/api/views/2343-nuqp/rows.csv?accessType=DOWNLOAD`

5. Ejecutar el servidor:
   ```bash
   python manage.py runserver
   ```

6. Abrir http://127.0.0.1:8000/ en el navegador.

> **Atajo en Windows:** doble clic en `iniciar.bat` (crea el entorno, instala dependencias, inicia el servidor y abre el navegador).

> No se necesita `migrate`: la aplicación no usa base de datos. Django procesa el CSV directamente con pandas.

### Ejecutar las pruebas
```bash
python manage.py test
```

---

## 4. Estructura del proyecto

```
├── manage.py
├── iniciar.bat                    # iniciador para Windows (doble clic)
├── requirements.txt
├── .gitignore
├── data/
│   └── emergencias_ungrd.csv      # datos reales UNGRD (Opción B)
├── config/                        # configuración Django (settings, urls, wsgi, asgi)
└── emergencias/                   # aplicación principal
    ├── services.py                # lectura, limpieza, filtrado, estadísticas y datos de gráficos (pandas + numpy)
    ├── forms.py                   # formulario de filtros y validación
    ├── views.py                   # recibe la solicitud y prepara la respuesta
    ├── urls.py
    ├── tests.py                   # 12 pruebas automatizadas
    ├── templates/emergencias/     # base.html, index.html (Bootstrap 5, archivos locales)
    └── static/emergencias/        # styles.css, filtros.js (select dependiente), graficos.js (Chart.js)
        └── vendor/                # Bootstrap 5.3.3, Bootstrap Icons 1.11.3 y Chart.js 4.4.1 (locales, funciona sin internet)
```

**Librerías:** Django (web), pandas (lectura y filtrado del CSV), numpy (estadística descriptiva e histograma). Gráficos interactivos con Chart.js 4.4.1 (incluido en `static/`, sin depender de internet): pandas calcula las series en el servidor y se envían a la página con `json_script`, así cada gráfico refleja exactamente el filtro consultado.

**Manejo de errores:** archivo no encontrado, CSV vacío o mal formado y columnas requeridas faltantes se muestran como un mensaje claro en la página (sin error 500). Las columnas opcionales que falten se completan con 0 y se avisa.

---

## 5. Verificación (registro real)

| Fecha | Verificación | Resultado |
|---|---|---|
| 13/11/2026 | `python manage.py check` | Sin problemas (0 issues) |
| 13/11/2026 | `python manage.py test` (Python 3.14.10, Django 5.2.19, pandas 3.1.1, numpy 2.5.4) | **12 pruebas, OK** |
| 13/11/2026 | Manual: Antioquia → Medellín → Consultar | 21 eventos, 1.992 personas afectadas, 575 familias; top 5, estadística, gráficos y tabla visibles |
| 13/11/2026 | Manual: al elegir Chocó, la lista de municipios se reduce a los de Chocó | OK (32 municipios + “Todos”) |
| 13/11/2026 | Manual: departamento inexistente en la URL | Página carga (200) con aviso “Revisa los filtros” |
| 13/11/2026 | Manual: consulta sin filtros (todo el país) | 6.506 eventos |
| 13/11/2026 | Manual: Antioquia → gráficos interactivos | 3 gráficos Chart.js con tooltips; clic en “Movimiento en masa” filtra la tabla a ese evento y resalta la barra |
| 13/11/2026 | `iniciar.bat` (doble clic): crea `.venv`, instala dependencias y arranca el servidor | OK: la app responde en http://127.0.0.1:8000/ |
| 13/11/2026 | `pip install -r requirements.txt` con versiones fijadas + `python manage.py test` dentro de `.venv` | Instalación sin errores; 12 pruebas OK |
| 13/11/2026 | Página sin recursos externos (Bootstrap, íconos y Chart.js servidos desde `static/`) | 0 recursos externos; 3 gráficos e íconos cargan |

Pruebas automatizadas incluidas: carga y limpieza, filtro + resumen + top 5, sin coincidencias, archivo no encontrado, columnas faltantes, datos de los gráficos, página inicial con fuente y limitaciones, recorrido principal, municipio de otro departamento, departamento inválido, mensaje de sin resultados y error controlado sin archivo.

---

## 6. Flujo de trabajo en GitHub

Flujo esperado: **Issue → Rama → Commit → Pull Request → Revisión → Comprobación → Integración → Verificación de DoD → Done.**

- Un issue por PBI (PBI-1, PBI-2, PBI-3) con contexto y criterios de aceptación; PBI-4 queda en **Backlog**.
- Project con columnas **Backlog / Ready / In Progress / In Review / Done** y campo **Priority** (High, Medium, Low).
- Ramas y commits en inglés, p. ej. `feature/emergency-filter`, `feat: add UNGRD emergency filter and summary`.
- PR con qué cambia, por qué, cómo se verificó y `Refs #N` (no `Closes`, para que *Done* dependa de verificar la DoD).

---

## 7. Revisión y retrospectiva del Sprint

*(Completar por el equipo después de la demostración; no se registran aquí resultados que no hayan ocurrido.)*

- **Qué se demostró:**
- **Qué cumplió la DoD y qué quedó pendiente:** PBI-4 (comparar municipios) no se inició.
- **¿Qué funcionó bien?**
- **¿Qué obstáculo afectó más el resultado?**
- **Acción concreta de mejora para el próximo ciclo:**

---

## 8. Uso responsable de los datos
- Se conserva la atribución a la UNGRD y a datos.gov.co en la página y en este README.
- El conjunto no contiene datos personales; la aplicación solo muestra cifras agregadas y registros de eventos.
- No se publican secretos: `SECRET_KEY` se puede definir con la variable de entorno `DJANGO_SECRET_KEY` (el valor por defecto es solo para desarrollo local).
