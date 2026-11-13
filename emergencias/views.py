import logging

from django.conf import settings
from django.shortcuts import render

from . import services
from .forms import FiltroEmergenciasForm

logger = logging.getLogger(__name__)

NO_RESULTS_MESSAGE = "No se encontraron emergencias con los filtros seleccionados."


def index(request):
    context = {
        "source_url": settings.RIESGOVIVO_DATA_SOURCE_URL,
        "max_rows": settings.RIESGOVIVO_MAX_TABLE_ROWS,
        "submitted": "consultar" in request.GET,
    }

    try:
        df, data_warnings = services.load_dataset()
    except services.DataSourceError as exc:
        context["data_error"] = str(exc)
        context["form"] = FiltroEmergenciasForm()
        return render(request, "emergencias/index.html", context)
    except Exception:  # Fallo inesperado: no se muestra un error 500 al usuario.
        logger.exception("Error inesperado al cargar el CSV")
        context["data_error"] = "Ocurrió un error inesperado al leer el archivo de datos."
        context["form"] = FiltroEmergenciasForm()
        return render(request, "emergencias/index.html", context)

    municipios_por_dep = services.get_municipios_por_departamento(df)
    form = FiltroEmergenciasForm(
        request.GET if context["submitted"] else None,
        departamentos=services.get_departamentos(df),
        municipios_por_dep=municipios_por_dep,
    )
    context.update(
        form=form,
        data_warnings=data_warnings,
        municipios_por_dep=municipios_por_dep,
        dataset_summary=services.build_summary(df),
    )

    if not context["submitted"] or not form.is_valid():
        return render(request, "emergencias/index.html", context)

    departamento = form.cleaned_data["departamento"]
    municipio = form.cleaned_data["municipio"]
    filtered = services.filter_emergencias(df, departamento, municipio)
    context["filtro"] = {"departamento": departamento, "municipio": municipio}

    if filtered.empty:
        context["no_results"] = NO_RESULTS_MESSAGE
        return render(request, "emergencias/index.html", context)

    top = services.top_eventos(filtered, 5)
    context.update(
        summary=services.build_summary(filtered),
        top_eventos=top,
        eventos=services.events_table(filtered),
        chart_data=services.chart_data(filtered, top),
    )
    return render(request, "emergencias/index.html", context)
