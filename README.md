# Riesgo_Vivo

Product Goal (Objetivo del Producto)

Permitir a un ciudadano o funcionario municipal consultar de forma simple el historial de emergencias de su territorio usando datos reales de la UNGRD, para apoyar la toma de conciencia y prevención del riesgo.Product Backlog (2-3 ítems prioritarios)
Como ciudadano o líder comunitario, quiero filtrar emergencias por departamento y municipio, para ver rápidamente el historial de eventos de mi territorio.

Criterios de aceptación:
Formulario con selects de Departamento y Municipio.
Al enviar, se muestran resultados reales o mensaje de “sin coincidencias”.
Se muestran al menos: cantidad de eventos, personas afectadas y lista de los últimos eventos.

Como usuario, quiero ver un resumen numérico y los tipos de eventos más frecuentes, para entender el patrón de riesgo de mi zona.

Criterios de aceptación:
Tarjetas o sección con totales (eventos, personas, familias, viviendas).
Lista o conteo de los tipos de evento más comunes.

(Opcional si alcanza tiempo) Manejo claro de datos vacíos y mensaje de fuente de datos.
Sprint Goal

Tener un recorrido web funcional completo: el usuario puede filtrar por departamento/municipio y ver un resumen comprensible de emergencias reales de la UNGRD, con manejo de resultados vacíos, en menos de 3 horas de desarrollo.Definition of Done (DoD)
Django inicia sin errores.
Se puede completar el flujo principal desde el navegador.
Usa datos reales de datos.gov.co (fuente documentada).
Resultados vacíos no rompen la aplicación.
README permite a otra persona instalar y ejecutar.
Cambios integrados en main vía Pull Request revisado.
Al menos una prueba automatizada o verificación manual registrada.
