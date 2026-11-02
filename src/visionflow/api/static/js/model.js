(function () {
  const { t, escape } = window.VisionFlow;
  const container = document.getElementById("model-classes");

  fetch("/api/model")
    .then(async (response) => {
      const data = await response.json();
      if (!response.ok) throw new Error(data.error || t("networkError"));
      if (!data.available) {
        container.textContent = t("weightsUnavailable");
        return;
      }
      if (!data.classes.length) {
        container.textContent = t("noDetectionsYet");
        return;
      }
      container.innerHTML = data.classes.map((name) => `<span class="class-chip">${escape(name)}</span>`).join("");
    })
    .catch((error) => { container.textContent = error.message || t("networkError"); });
})();
