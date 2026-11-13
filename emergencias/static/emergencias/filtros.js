// Actualiza el select de municipios según el departamento elegido.
(function () {
  const dataEl = document.getElementById("municipios-data");
  const dep = document.getElementById("id_departamento");
  const mun = document.getElementById("id_municipio");
  if (!dataEl || !dep || !mun) return;

  const porDep = JSON.parse(dataEl.textContent);
  const todos = [...new Set(Object.values(porDep).flat())].sort();
  const titulo = (s) => s.toLowerCase().replace(/(^|\s)\S/g, (c) => c.toUpperCase());

  function renderMunicipios(keepValue) {
    const lista = dep.value ? porDep[dep.value] || [] : todos;
    const actual = keepValue ? mun.value : "";
    mun.innerHTML = "";
    mun.add(new Option("Todos los municipios", ""));
    lista.forEach((m) => mun.add(new Option(titulo(m), m, false, m === actual)));
  }

  dep.addEventListener("change", () => renderMunicipios(false));
  renderMunicipios(true);
})();
