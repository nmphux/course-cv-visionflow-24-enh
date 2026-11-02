(function () {
  const { t, escape, toast } = window.VisionFlow;
  const input = document.getElementById("inference-files");
  const form = document.getElementById("inference-form");
  const dropzone = document.getElementById("dropzone");
  const selectedFiles = document.getElementById("selected-files");

  function formatSize(size) {
    if (size < 1024 * 1024) return `${Math.max(1, Math.round(size / 1024))} KB`;
    return `${(size / (1024 * 1024)).toFixed(1)} MB`;
  }

  function renderSelectedFiles() {
    selectedFiles.innerHTML = Array.from(input.files).map((file) => `
      <div class="selected-file"><span>${escape(file.name)}</span><small>${formatSize(file.size)}</small></div>
    `).join("");
  }

  function renderResults(results) {
    const panel = document.getElementById("results-panel");
    const container = document.getElementById("inference-results");
    container.innerHTML = results.map((result) => {
      const preview = result.type === "jpg"
        ? `<img src="${escape(result.url)}" alt="Annotated ${escape(result.name)}">`
        : `<video controls preload="metadata" src="${escape(result.url)}"></video>`;
      return `<article class="result-card">${preview}<div class="result-meta"><div><strong>${escape(result.name)}</strong><small>${result.detections} ${escape(t("detectionCount"))}</small></div><a class="button button-quiet button-small" href="${escape(result.url)}" download="${escape(result.name.replace(/\.[^.]+$/, "") + "-annotated." + result.type)}">${escape(t("download") || "Download")}</a></div></article>`;
    }).join("");
    panel.hidden = false;
    panel.scrollIntoView({ behavior: "smooth", block: "start" });
  }

  input.addEventListener("change", renderSelectedFiles);
  ["dragenter", "dragover"].forEach((eventName) => dropzone.addEventListener(eventName, (event) => {
    event.preventDefault();
    dropzone.classList.add("is-dragging");
  }));
  ["dragleave", "drop"].forEach((eventName) => dropzone.addEventListener(eventName, (event) => {
    event.preventDefault();
    dropzone.classList.remove("is-dragging");
  }));
  dropzone.addEventListener("drop", (event) => {
    const files = Array.from(event.dataTransfer.files);
    if (!files.length) return;
    const transfer = new DataTransfer();
    files.forEach((file) => transfer.items.add(file));
    input.files = transfer.files;
    renderSelectedFiles();
  });

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    const files = Array.from(input.files);
    if (!files.length) {
      toast(t("chooseFiles"), true);
      return;
    }
    if (files.reduce((sum, file) => sum + file.size, 0) > 100 * 1024 * 1024) {
      toast(t("fileTooLarge"), true);
      return;
    }
    const submitButton = document.getElementById("run-inference");
    const originalLabel = submitButton.innerHTML;
    submitButton.disabled = true;
    submitButton.innerHTML = `<span class="spinner"></span><span>${escape(t("processing"))}</span>`;
    try {
      const response = await fetch("/api/inference", { method: "POST", body: new FormData(form) });
      const data = await response.json();
      if (!response.ok) throw new Error(data.error || t("uploadFailed"));
      renderResults(data.results);
      toast(t("inferenceFinished"));
    } catch (error) {
      toast(error.message || t("networkError"), true);
    } finally {
      submitButton.disabled = false;
      submitButton.innerHTML = originalLabel;
    }
  });
})();
