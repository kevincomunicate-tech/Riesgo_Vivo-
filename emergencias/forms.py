from django import forms


class FiltroEmergenciasForm(forms.Form):
    """Filtro por departamento y municipio. Las opciones salen del propio CSV."""

    departamento = forms.ChoiceField(required=False, label="Departamento")
    municipio = forms.ChoiceField(required=False, label="Municipio")

    def __init__(self, *args, departamentos=None, municipios_por_dep=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.municipios_por_dep = municipios_por_dep or {}
        departamentos = departamentos or []

        self.fields["departamento"].choices = [("", "Todos los departamentos")] + [
            (d, d.title()) for d in departamentos
        ]

        # Se aceptan todos los municipios; filtros.js acota la lista en el navegador
        # y clean() valida que el municipio pertenezca al departamento elegido.
        municipios = sorted({m for ms in self.municipios_por_dep.values() for m in ms})
        self.fields["municipio"].choices = [("", "Todos los municipios")] + [
            (m, m.title()) for m in municipios
        ]
        for field in self.fields.values():
            field.widget.attrs["class"] = "form-select"

    def clean(self):
        cleaned = super().clean()
        dep = cleaned.get("departamento")
        mun = cleaned.get("municipio")
        if dep and mun and mun not in self.municipios_por_dep.get(dep, []):
            self.add_error(
                "municipio",
                f"El municipio {mun.title()} no tiene registros en {dep.title()}.",
            )
        return cleaned
