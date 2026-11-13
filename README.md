# RiesgoVivo

Aplicación web desarrollada en Python y Django que permite consultar e interpretar el historial de emergencias reportadas por la Unidad Nacional para la Gestión del Riesgo de Desastres (UNGRD) a partir de datos abiertos de datos.gov.co.

---

## 1. Descubrimiento del problema

### Nombre de la aplicación
**RiesgoVivo**

### Problema / Hipótesis de necesidad
Las comunidades, juntas de acción comunal y funcionarios municipales tienen acceso a los datos abiertos de emergencias de la UNGRD, pero carecen de una herramienta sencilla que les permita filtrar y comprender el historial de eventos de su territorio de forma rápida y clara. Existe información pública valiosa, pero no una forma simple de convertirla en conocimiento útil para la prevención del riesgo.

### Usuario / Beneficiario potencial
- Líderes de juntas de acción comunal
- Funcionarios de gestión del riesgo de municipios
- Ciudadanos interesados en conocer el historial de emergencias de su zona

### Fuente de datos
- **Conjunto de datos:** Emergencias UNGRD V2
- **URL:** https://www.datos.gov.co/en/en/Environment-and-Sustainable-Development/Emergencias-UNGRD-V2/2343-nuqp
- **Entidad publicadora:** Unidad Nacional para la Gestión del Riesgo de Desastres – UNGRD
- **Cobertura:** Nacional
- **Campos relevantes utilizados:** FECHA, DEPARTAMENTO, MUNICIPIO, EVENTO, FALLECIDOS, HERIDOS, PERSONAS, FAMILIAS, VIVIENDAS DESTRUIDAS

### Funcionalidad principal
Permitir al usuario filtrar emergencias por departamento y municipio, y visualizar un resumen claro del historial (cantidad de eventos, personas y familias afectadas, tipos de eventos más frecuentes).

### Valor esperado
Que cualquier persona pueda responder en menos de un minuto la pregunta:  
**“¿Qué tan afectado ha sido mi municipio históricamente y por qué tipo de emergencias?”**

### Limitaciones conocidas
- Los datos se actualizan de forma anual (no son en tiempo real).
- Algunos registros pueden tener campos vacíos o incompletos.
- Se utiliza un archivo CSV descargado del portal (no se consume la API en tiempo real).
- Las coordenadas geográficas no siempre están completas.

---

## 2. Planificación (Scrum adaptado)

### Product Goal (Objetivo del Producto)
Permitir a ciudadanos y funcionarios municipales consultar de forma simple el historial de emergencias de su territorio usando datos reales de la UNGRD, para apoyar la toma de conciencia y la prevención del riesgo.

### Product Backlog

**PBI-1**  
Como ciudadano o líder comunitario, quiero filtrar emergencias por departamento y municipio, para ver rápidamente el historial de eventos de mi territorio.  

**Criterios de aceptación:**
- Existe un formulario con selección de departamento y municipio.
- Al enviar el formulario se muestran resultados reales o un mensaje claro de “sin coincidencias”.
- Se visualizan totales de eventos, personas afectadas y una lista de eventos recientes.

**PBI-2**  
Como usuario, quiero ver un resumen numérico y los tipos de eventos más frecuentes, para entender el patrón de riesgo de mi zona.  

**Criterios de aceptación:**
- Se muestran tarjetas o indicadores con totales (eventos, personas, familias).
- Se listan los tipos de evento más comunes en el resultado filtrado.

### Sprint Goal
Tener un recorrido web funcional completo en el que el usuario pueda filtrar por departamento y/o municipio y obtener un resumen comprensible de emergencias reales de la UNGRD, con manejo adecuado de resultados vacíos.

### Definition of Done (DoD)
- Django inicia sin errores bloqueantes.
- Se puede completar el recorrido principal desde el navegador.
- La aplicación utiliza datos reales de datos.gov.co y declara su fuente.
- Los resultados vacíos o entradas inválidas no provocan fallos.
- El README permite a otra persona instalar y ejecutar el proyecto.
- Los cambios están integrados en la rama principal mediante Pull Request revisado.
- Se ejecutó al menos una verificación funcional real del recorrido principal.

---

## 3. Cómo instalar y ejecutar el proyecto

### Requisitos previos
- Python 3.10 o superior
- pip
- Git (opcional pero recomendado)

### Pasos de instalación

1. Clonar el repositorio (o descargar el código):
```bash
git clone <URL_DEL_REPOSITORIO>
cd riesgovivo
