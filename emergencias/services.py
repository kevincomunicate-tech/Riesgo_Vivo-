"""Lógica de datos de RiesgoVivo: lectura, limpieza, filtrado y estadísticas.

Toda la manipulación del CSV de la UNGRD vive aquí para que las vistas
solo reciban estructuras simples (listas y diccionarios) listas para mostrar.
"""
from __future__ import annotations

import re
import unicodedata
from functools import lru_cache
from pathlib import Path

import numpy as np
import pandas as pd
from django.conf import settings

# Columnas mínimas para que la aplicación funcione.
REQUIRED_COLUMNS = ["FECHA", "DEPARTAMENTO", "MUNICIPIO", "EVENTO", "PERSONAS", "FAMILIAS"]

# Columnas numéricas opcionales: si faltan se completan con 0 y se informa.
OPTIONAL_NUMERIC_COLUMNS = ["FALLECIDOS", "HERIDOS", "DESAPARECIDOS", "VIVIENDAS DESTRUIDAS"]

# Nombres alternativos que aparecen en otras versiones/exportaciones del conjunto.
COLUMN_ALIASES = {
    "MUERTOS": "FALLECIDOS",
    "DESAPA": "DESAPARECIDOS",
    "VIV DESTRU": "VIVIENDAS DESTRUIDAS",
}

TEXT_COLUMNS = ["DEPARTAMENTO", "MUNICIPIO", "EVENTO"]
SIN_DATO = "SIN DATO"


class DataSourceError(Exception):
    """Error controlado al leer o validar el archivo de datos."""


# --------------------------------------------------------------------------- #
# Lectura y limpieza
# --------------------------------------------------------------------------- #
def _normalize_column(name: str) -> str:
    """'Codificación  según Divipola' -> 'CODIFICACION SEGUN DIVIPOLA'."""
    text = unicodedata.normalize("NFKD", str(name))
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = re.sub(r"[_\s]+", " ", text).strip().upper()
    return COLUMN_ALIASES.get(text, text)


def _parse_dates(series: pd.Series) -> pd.Series:
    """El portal exporta fechas como '01/31/2025 12:00:00 AM'; si cambia, se infiere."""
    parsed = pd.to_datetime(series, format="%m/%d/%Y %I:%M:%S %p", errors="coerce")
    if parsed.isna().all():
        parsed = pd.to_datetime(series, errors="coerce", dayfirst=False)
    return parsed


def _clean(df: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
    warnings: list[str] = []
    df = df.copy()
    df.columns = [_normalize_column(c) for c in df.columns]

    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise DataSourceError(
            "El archivo de datos no tiene las columnas requeridas: " + ", ".join(missing)
        )

    for col in TEXT_COLUMNS:
        df[col] = (
            df[col].astype("string").str.strip().str.upper().replace("", pd.NA).fillna(SIN_DATO)
        )

    for col in ["PERSONAS", "FAMILIAS", *OPTIONAL_NUMERIC_COLUMNS]:
        if col not in df.columns:
            df[col] = 0
            warnings.append(f"La columna opcional '{col}' no está en el archivo; se asume 0.")
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).clip(lower=0).astype(int)

    df["FECHA"] = _parse_dates(df["FECHA"])
    sin_fecha = int(df["FECHA"].isna().sum())
    if sin_fecha:
        warnings.append(f"{sin_fecha} registros tienen fecha vacía o inválida.")

    keep = ["FECHA", *TEXT_COLUMNS, "PERSONAS", "FAMILIAS", *OPTIONAL_NUMERIC_COLUMNS]
    return df[keep], warnings


@lru_cache(maxsize=4)
def _load_cached(path_str: str, mtime: float) -> tuple[pd.DataFrame, tuple[str, ...]]:
    try:
        raw = pd.read_csv(path_str, low_memory=False, encoding="utf-8")
    except UnicodeDecodeError:
        raw = pd.read_csv(path_str, low_memory=False, encoding="latin-1")
    except pd.errors.EmptyDataError as exc:
        raise DataSourceError("El archivo de datos está vacío.") from exc
    except pd.errors.ParserError as exc:
        raise DataSourceError(f"El archivo de datos no es un CSV válido: {exc}") from exc
    df, warnings = _clean(raw)
    return df, tuple(warnings)


def load_dataset(path: str | Path | None = None) -> tuple[pd.DataFrame, list[str]]:
    """Carga y limpia el CSV. Se cachea mientras el archivo no cambie."""
    csv_path = Path(path or settings.RIESGOVIVO_CSV_PATH)
    if not csv_path.is_file():
        raise DataSourceError(
            f"No se encontró el archivo de datos '{csv_path.name}'. "
            "Descárgalo de datos.gov.co y ubícalo en la carpeta data/ (ver README)."
        )
    df, warnings = _load_cached(str(csv_path.resolve()), csv_path.stat().st_mtime)
    return df.copy(), list(warnings)


# --------------------------------------------------------------------------- #
# Opciones del formulario y filtrado
# --------------------------------------------------------------------------- #
def get_departamentos(df: pd.DataFrame) -> list[str]:
    return sorted(df["DEPARTAMENTO"].dropna().unique().tolist())


def get_municipios_por_departamento(df: pd.DataFrame) -> dict[str, list[str]]:
    grouped = df.groupby("DEPARTAMENTO")["MUNICIPIO"].unique()
    return {dep: sorted(muns.tolist()) for dep, muns in grouped.items()}


def filter_emergencias(
    df: pd.DataFrame, departamento: str = "", municipio: str = ""
) -> pd.DataFrame:
    result = df
    if departamento:
        result = result[result["DEPARTAMENTO"] == departamento.strip().upper()]
    if municipio:
        result = result[result["MUNICIPIO"] == municipio.strip().upper()]
    return result


# --------------------------------------------------------------------------- #
# Estadísticas
# --------------------------------------------------------------------------- #
def build_summary(df: pd.DataFrame) -> dict:
    """Totales y estadística descriptiva de personas afectadas por evento."""
    personas = df["PERSONAS"].to_numpy(dtype=float)
    n = len(df)
    con_afectados = int((personas > 0).sum())

    summary = {
        "total_eventos": n,
        "total_personas": int(df["PERSONAS"].sum()),
        "total_familias": int(df["FAMILIAS"].sum()),
        "total_fallecidos": int(df["FALLECIDOS"].sum()),
        "total_heridos": int(df["HERIDOS"].sum()),
        "total_viviendas_destruidas": int(df["VIVIENDAS DESTRUIDAS"].sum()),
        "promedio_personas": float(np.mean(personas)) if n else 0.0,
        "mediana_personas": float(np.median(personas)) if n else 0.0,
        "desviacion_personas": float(np.std(personas, ddof=1)) if n > 1 else 0.0,
        "p90_personas": float(np.percentile(personas, 90)) if n else 0.0,
        "max_personas": int(personas.max()) if n else 0,
        "pct_eventos_con_afectados": (con_afectados / n * 100) if n else 0.0,
        "fecha_min": None,
        "fecha_max": None,
        "evento_mayor_impacto": None,
    }

    fechas = df["FECHA"].dropna()
    if not fechas.empty:
        summary["fecha_min"] = fechas.min().date()
        summary["fecha_max"] = fechas.max().date()

    if n and summary["max_personas"] > 0:
        row = df.loc[df["PERSONAS"].idxmax()]
        summary["evento_mayor_impacto"] = {
            "evento": row["EVENTO"],
            "municipio": row["MUNICIPIO"],
            "departamento": row["DEPARTAMENTO"],
            "fecha": row["FECHA"].date() if pd.notna(row["FECHA"]) else None,
            "personas": int(row["PERSONAS"]),
        }
    return summary


def top_eventos(df: pd.DataFrame, n: int = 5) -> list[dict]:
    """Los n tipos de evento más frecuentes, con su peso y personas afectadas."""
    if df.empty:
        return []
    total = len(df)
    grouped = (
        df.groupby("EVENTO")
        .agg(cantidad=("EVENTO", "size"), personas=("PERSONAS", "sum"))
        .sort_values(["cantidad", "personas"], ascending=False)
        .head(n)
    )
    return [
        {
            "evento": evento,
            "cantidad": int(row.cantidad),
            "porcentaje": row.cantidad / total * 100,
            "personas": int(row.personas),
        }
        for evento, row in grouped.iterrows()
    ]


def monthly_trend(df: pd.DataFrame) -> pd.DataFrame:
    """Número de eventos y personas afectadas por mes (columnas: mes, eventos, personas)."""
    data = df.dropna(subset=["FECHA"])
    if data.empty:
        return pd.DataFrame(columns=["mes", "eventos", "personas"])
    monthly = (
        data.set_index("FECHA")
        .resample("MS")
        .agg({"EVENTO": "size", "PERSONAS": "sum"})
        .rename(columns={"EVENTO": "eventos", "PERSONAS": "personas"})
        .reset_index()
        .rename(columns={"FECHA": "mes"})
    )
    return monthly


def events_table(df: pd.DataFrame, limit: int | None = None) -> list[dict]:
    """Eventos ordenados del más reciente al más antiguo, listos para la plantilla."""
    limit = limit or settings.RIESGOVIVO_MAX_TABLE_ROWS
    rows = df.sort_values("FECHA", ascending=False, na_position="last").head(limit)
    return [
        {
            "fecha": r.FECHA.date() if pd.notna(r.FECHA) else None,
            "evento": r.EVENTO,
            "departamento": r.DEPARTAMENTO,
            "municipio": r.MUNICIPIO,
            "personas": int(r.PERSONAS),
            "familias": int(r.FAMILIAS),
        }
        for r in rows.itertuples(index=False)
    ]
