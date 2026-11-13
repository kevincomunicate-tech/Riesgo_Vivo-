"""Pruebas de RiesgoVivo. Ejecutar con: python manage.py test

Usan un CSV pequeño de prueba (no los datos reales) para que los resultados
sean deterministas. No requieren base de datos (SimpleTestCase).
"""
import shutil
import tempfile
from pathlib import Path
from unittest import mock

from django.test import SimpleTestCase, override_settings
from django.urls import reverse

from . import services

CSV_OK = """FECHA,DEPARTAMENTO,MUNICIPIO,EVENTO,FALLECIDOS,HERIDOS,DESAPARECIDOS,PERSONAS,FAMILIAS,VIVIENDAS DESTRUIDAS
01/15/2025 12:00:00 AM,ANTIOQUIA,MEDELLIN,INUNDACION,0,1,0,100,25,2
02/10/2025 12:00:00 AM,ANTIOQUIA,MEDELLIN,INUNDACION,0,0,0,40,10,0
03/05/2025 12:00:00 AM,ANTIOQUIA,MEDELLIN,DESLIZAMIENTO,1,2,0,12,3,1
03/20/2025 12:00:00 AM,ANTIOQUIA,BELLO,INCENDIO FORESTAL,0,0,0,,,0
04/01/2025 12:00:00 AM,CHOCO,QUIBDO,INUNDACION,0,0,0,500,120,5
"""

CSV_SIN_COLUMNAS = """FECHA,DEPARTAMENTO,EVENTO
01/15/2025 12:00:00 AM,ANTIOQUIA,INUNDACION
"""


class TempCsvMixin:
    def setUp(self):
        self.tmpdir = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmpdir, ignore_errors=True)

    def write_csv(self, content, name="emergencias.csv"):
        path = self.tmpdir / name
        path.write_text(content, encoding="utf-8")
        return path


class ServicesTests(TempCsvMixin, SimpleTestCase):
    def test_carga_y_limpieza(self):
        df, warnings = services.load_dataset(self.write_csv(CSV_OK))
        self.assertEqual(len(df), 5)
        # Valores vacíos en PERSONAS/FAMILIAS se convierten en 0, no fallan.
        self.assertEqual(df.loc[3, "PERSONAS"], 0)
        self.assertEqual(df["FECHA"].isna().sum(), 0)
        self.assertEqual(warnings, [])

    def test_filtro_resumen_y_top(self):
        df, _ = services.load_dataset(self.write_csv(CSV_OK))
        filtrado = services.filter_emergencias(df, "antioquia", "medellin")
        resumen = services.build_summary(filtrado)
        self.assertEqual(resumen["total_eventos"], 3)
        self.assertEqual(resumen["total_personas"], 152)
        self.assertEqual(resumen["total_familias"], 38)
        self.assertEqual(resumen["mediana_personas"], 40)
        self.assertEqual(resumen["evento_mayor_impacto"]["personas"], 100)

        top = services.top_eventos(filtrado)
        self.assertEqual(top[0]["evento"], "INUNDACION")
        self.assertEqual(top[0]["cantidad"], 2)

    def test_sin_coincidencias(self):
        df, _ = services.load_dataset(self.write_csv(CSV_OK))
        vacio = services.filter_emergencias(df, "CHOCO", "MEDELLIN")
        self.assertTrue(vacio.empty)
        self.assertEqual(services.build_summary(vacio)["total_eventos"], 0)
        self.assertEqual(services.top_eventos(vacio), [])
        self.assertEqual(services.chart_data(vacio)["mensual"]["labels"], [])

    def test_archivo_no_encontrado(self):
        with self.assertRaisesMessage(services.DataSourceError, "No se encontró"):
            services.load_dataset(self.tmpdir / "no_existe.csv")

    def test_columnas_faltantes(self):
        with self.assertRaisesMessage(services.DataSourceError, "MUNICIPIO"):
            services.load_dataset(self.write_csv(CSV_SIN_COLUMNAS))

    def test_datos_de_graficos(self):
        df, _ = services.load_dataset(self.write_csv(CSV_OK))
        data = services.chart_data(df)
        self.assertEqual(data["top"]["keys"][0], "INUNDACION")
        self.assertEqual(data["top"]["eventos"][0], 3)
        self.assertEqual(data["mensual"]["labels"], ["Ene", "Feb", "Mar", "Abr"])
        self.assertEqual(data["mensual"]["eventos"], [1, 1, 2, 1])
        # Distribución: 0 personas (1), 10–49 (12 y 40), 100–499 (100), 500–999 (500).
        self.assertEqual(data["distribucion"]["eventos"], [1, 0, 2, 0, 1, 1, 0])
        self.assertEqual(sum(data["distribucion"]["eventos"]), len(df))


class IndexViewTests(TempCsvMixin, SimpleTestCase):
    def get(self, csv_path, **params):
        with override_settings(RIESGOVIVO_CSV_PATH=csv_path):
            return self.client.get(reverse("emergencias:index"), params)

    def test_pagina_inicial_con_formulario_y_fuente(self):
        resp = self.get(self.write_csv(CSV_OK))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'name="departamento"')
        self.assertContains(resp, 'name="municipio"')
        self.assertContains(resp, "Emergencias UNGRD V2")
        self.assertContains(resp, "Limitaciones")

    def test_recorrido_principal_con_resultados(self):
        resp = self.get(
            self.write_csv(CSV_OK), departamento="ANTIOQUIA", municipio="MEDELLIN", consultar="1"
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.context["summary"]["total_eventos"], 3)
        self.assertContains(resp, "Inundacion")
        self.assertContains(resp, 'id="chart-data"')
        self.assertContains(resp, 'id="chart-top"')
        self.assertEqual(resp.context["chart_data"]["top"]["eventos"], [2, 1])

    def test_municipio_de_otro_departamento_no_rompe(self):
        resp = self.get(
            self.write_csv(CSV_OK), departamento="CHOCO", municipio="MEDELLIN", consultar="1"
        )
        self.assertEqual(resp.status_code, 200)
        self.assertNotIn("summary", resp.context)
        self.assertContains(resp, "no tiene registros en Choco")

    def test_departamento_invalido_no_rompe(self):
        resp = self.get(self.write_csv(CSV_OK), departamento="<script>", consultar="1")
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Revisa los filtros")
        self.assertNotContains(resp, "<script>alert")

    def test_sin_resultados_muestra_mensaje(self):
        # Con los selects de la UI no es fácil llegar a cero filas, así que se
        # fuerza un filtrado vacío para verificar el mensaje que exige el reto.
        empty = services.load_dataset(self.write_csv(CSV_OK))[0].iloc[0:0]
        with mock.patch.object(services, "filter_emergencias", return_value=empty):
            resp = self.get(self.tmpdir / "emergencias.csv", departamento="CHOCO", consultar="1")
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "No se encontraron emergencias con los filtros seleccionados")

    def test_archivo_ausente_muestra_error_controlado(self):
        resp = self.get(self.tmpdir / "no_existe.csv", consultar="1")
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "No se pudieron cargar los datos")
