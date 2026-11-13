"""Gráficos con matplotlib.pyplot, devueltos como imágenes PNG en base64.

Se usa el backend 'Agg' (sin ventana) para que funcione dentro del servidor web.
"""
from __future__ import annotations

import base64
import io
import textwrap

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.ticker import MaxNLocator  # noqa: E402

PRIMARY = "#0d6efd"
ACCENT = "#dc3545"
GRID = "#dee2e6"
TEXT = "#343a40"

MESES = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]


def _style(ax) -> None:
    ax.spines[["top", "right"]].set_visible(False)
    ax.spines[["left", "bottom"]].set_color(GRID)
    ax.tick_params(colors=TEXT, labelsize=9)
    ax.grid(axis="x", color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)


def _to_base64(fig) -> str:
    buffer = io.BytesIO()
    fig.savefig(buffer, format="png", dpi=110, bbox_inches="tight")
    plt.close(fig)
    return base64.b64encode(buffer.getvalue()).decode("ascii")


def chart_top_eventos(top: list[dict]) -> str | None:
    """Barras horizontales: frecuencia de los 5 tipos de evento más comunes."""
    if not top:
        return None
    labels = [textwrap.fill(t["evento"].title(), 22) for t in top][::-1]
    values = [t["cantidad"] for t in top][::-1]

    fig, ax = plt.subplots(figsize=(6.4, 3.6))
    bars = ax.barh(labels, values, color=PRIMARY)
    ax.bar_label(bars, padding=3, fontsize=9, color=TEXT)
    ax.set_xlabel("Número de eventos", color=TEXT)
    ax.set_title("Tipos de evento más frecuentes", color=TEXT, fontsize=11, loc="left")
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    ax.margins(x=0.12)
    _style(ax)
    return _to_base64(fig)


def chart_tendencia_mensual(monthly) -> str | None:
    """Línea de eventos por mes con barras de personas afectadas en eje secundario."""
    if monthly is None or monthly.empty:
        return None
    multi_year = monthly["mes"].dt.year.nunique() > 1
    labels = [
        f"{MESES[m.month - 1]} {m.year % 100:02d}" if multi_year else MESES[m.month - 1]
        for m in monthly["mes"]
    ]
    x = range(len(labels))

    fig, ax = plt.subplots(figsize=(6.4, 3.6))
    ax2 = ax.twinx()
    ax2.bar(x, monthly["personas"], color=ACCENT, alpha=0.18, label="Personas afectadas")
    ax.plot(x, monthly["eventos"], color=PRIMARY, marker="o", linewidth=2, label="Eventos")
    ax.set_zorder(ax2.get_zorder() + 1)
    ax.patch.set_visible(False)

    ax.set_xticks(list(x), labels, rotation=45 if len(labels) > 8 else 0)
    ax.set_ylabel("Eventos", color=PRIMARY)
    ax2.set_ylabel("Personas afectadas", color=ACCENT)
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))
    ax.set_title("Evolución mensual", color=TEXT, fontsize=11, loc="left")
    _style(ax)
    ax.grid(axis="x", visible=False)
    ax.grid(axis="y", color=GRID, linewidth=0.8)
    ax2.spines[["top"]].set_visible(False)
    ax2.spines[["right"]].set_color(GRID)
    ax2.tick_params(colors=TEXT, labelsize=9)
    return _to_base64(fig)


def chart_distribucion_personas(df) -> str | None:
    """Histograma (escala log) de personas afectadas por evento, con media y mediana."""
    personas = df.loc[df["PERSONAS"] > 0, "PERSONAS"]
    if personas.empty:
        return None

    fig, ax = plt.subplots(figsize=(6.4, 3.6))
    upper = max(personas.max(), 2)
    bins = sorted(set(int(b) for b in _log_bins(1, upper)))
    ax.hist(personas, bins=bins, color=PRIMARY, alpha=0.85, edgecolor="white")
    ax.set_xscale("log")
    media, mediana = personas.mean(), personas.median()
    ax.axvline(mediana, color=TEXT, linestyle="--", linewidth=1.2, label=f"Mediana: {mediana:,.0f}")
    ax.axvline(media, color=ACCENT, linestyle="-", linewidth=1.2, label=f"Media: {media:,.0f}")
    ax.set_xlabel("Personas afectadas por evento (escala logarítmica)", color=TEXT)
    ax.set_ylabel("Eventos", color=TEXT)
    ax.set_title("Distribución del impacto (eventos con afectados)", color=TEXT, fontsize=11, loc="left")
    ax.legend(frameon=False, fontsize=9)
    _style(ax)
    ax.grid(axis="x", visible=False)
    ax.grid(axis="y", color=GRID, linewidth=0.8)
    return _to_base64(fig)


def _log_bins(start: float, stop: float, n: int = 20):
    return np.unique(np.geomspace(start, stop + 1, n).round())
