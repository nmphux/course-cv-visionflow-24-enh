(function () {
  const { t, escape, toast } = window.VisionFlow;
  const grid = document.getElementById("camera-grid");
  const dialog = document.getElementById("camera-dialog");
  const form = document.getElementById("camera-form");
  const cameras = new Map();
  let loading = false;

  function statusLabel(status) {
    return status === "online" ? t("online") : status === "connecting" ? t("connecting") : status === "stopped" ? t("stopped") : t("offline");
  }

  function makeCard(camera) {
    const card = document.createElement("article");
    card.className = "panel camera-card";
    card.dataset.cameraId = camera.id;
    card.innerHTML = `
      <div class="camera-preview" data-slot="preview">
        <div class="preview-placeholder" data-slot="placeholder"><span>▣</span><small>${escape(t("connecting"))}</small></div>
        <div class="preview-overlay"><span class="status-pill" data-slot="status"></span></div>
      </div>
      <div class="camera-card-content">
        <div class="camera-card-heading"><div><h3 data-slot="name"></h3><p data-slot="source"></p></div><span class="status-dot" data-slot="indicator"></span></div>
        <div class="camera-card-stats">
          <span>${escape(t("currentView"))}<strong data-slot="count">0</strong></span>
          <span>${escape(t("processingSpeed"))}<strong data-slot="fps">—</strong></span>
          <span>${escape(t("detections"))}<strong data-slot="total">0</strong></span>
        </div>
        <div class="camera-error" data-slot="error" hidden></div>
        <div class="camera-card-actions">
          <button class="button button-quiet button-small" type="button" data-action="toggle"></button>
          <button class="button button-quiet button-small" type="button" data-action="remove">${escape(t("remove"))}</button>
        </div>
      </div>`;
    return card;
  }

  function updateCard(card, camera) {
    card.querySelector('[data-slot="name"]').textContent = camera.name;
    card.querySelector('[data-slot="source"]').textContent = camera.source;
    const count = Object.values(camera.counts || {}).reduce((total, value) => total + value, 0);
    card.querySelector('[data-slot="count"]').textContent = count;
    card.querySelector('[data-slot="fps"]').textContent = camera.fps ? `${camera.fps} FPS` : "—";
    card.querySelector('[data-slot="total"]').textContent = camera.detections_total || 0;
    const status = card.querySelector('[data-slot="status"]');
    status.textContent = statusLabel(camera.status);
    status.className = `status-pill ${camera.status === "online" ? "status-online" : camera.status === "offline" ? "status-offline" : ""}`;
    const indicator = card.querySelector('[data-slot="indicator"]');
    indicator.className = `status-dot ${camera.status === "online" ? "is-ready" : camera.status === "offline" ? "is-offline" : "is-warning"}`;
    const toggleButton = card.querySelector('[data-action="toggle"]');
    toggleButton.textContent = camera.status === "online" || camera.status === "connecting" ? t("stop") : t("retry");
    toggleButton.dataset.nextAction = camera.status === "online" || camera.status === "connecting" ? "stop" : "start";

    const preview = card.querySelector('[data-slot="preview"]');
    const currentPreviewStatus = preview.dataset.status;
    if (camera.status === "online" && currentPreviewStatus !== "online") {
      preview.innerHTML = `<img alt="${escape(camera.name)} live stream" src="/api/cameras/${encodeURIComponent(camera.id)}/stream"><div class="preview-overlay"><span class="status-pill status-online"><span class="status-dot is-ready"></span>${escape(t("online"))}</span></div>`;
    } else if (camera.status !== "online" && currentPreviewStatus !== camera.status) {
      preview.innerHTML = `<div class="preview-placeholder"><span>▣</span><small>${escape(camera.error || statusLabel(camera.status))}</small></div><div class="preview-overlay"><span class="status-pill">${escape(statusLabel(camera.status))}</span></div>`;
    } else if (camera.status !== "online" && camera.error) {
      const placeholder = preview.querySelector(".preview-placeholder small");
      if (placeholder) placeholder.textContent = camera.error;
    }
    preview.dataset.status = camera.status;

    const error = card.querySelector('[data-slot="error"]');
    error.hidden = !camera.error;
    error.textContent = camera.error || "";
  }

  function renderEmpty() {
    grid.innerHTML = `<div class="panel empty-state"><span class="empty-illustration">▣</span><strong>${escape(t("connectFirstCamera"))}</strong><p>${escape(t("noCamerasHelp"))}</p><button class="button button-primary button-small" type="button" data-empty-add>＋ ${escape(t("connectCamera"))}</button></div>`;
    grid.querySelector("[data-empty-add]").addEventListener("click", openDialog);
  }

  function render(data) {
    document.getElementById("camera-total-count").textContent = data.length;
    document.getElementById("camera-online-count").textContent = data.filter((camera) => camera.status === "online").length;
    document.getElementById("nav-camera-count").textContent = data.length;
    if (!data.length) {
      cameras.clear();
      renderEmpty();
      return;
    }
    const activeIds = new Set(data.map((camera) => camera.id));
    for (const [id, card] of cameras) {
      if (!activeIds.has(id)) {
        card.remove();
        cameras.delete(id);
      }
    }
    const empty = grid.querySelector("[data-empty-add]");
    empty?.closest(".panel")?.remove();
    data.forEach((camera) => {
      let card = cameras.get(camera.id);
      if (!card) {
        card = makeCard(camera);
        cameras.set(camera.id, card);
        grid.append(card);
      }
      updateCard(card, camera);
    });
  }

  async function refresh() {
    if (loading) return;
    loading = true;
    try {
      const response = await fetch("/api/cameras");
      const data = await response.json();
      if (!response.ok) throw new Error(data.error || t("loadingError"));
      render(data.cameras);
    } catch (error) {
      toast(error.message || t("networkError"), true);
    } finally {
      loading = false;
    }
  }

  function openDialog() {
    form.reset();
    dialog.showModal();
    form.elements.name.focus();
  }

  document.getElementById("open-camera-form").addEventListener("click", openDialog);
  document.getElementById("close-camera-form").addEventListener("click", () => dialog.close());
  document.getElementById("cancel-camera-form").addEventListener("click", () => dialog.close());
  document.getElementById("refresh-cameras").addEventListener("click", refresh);
  dialog.addEventListener("click", (event) => {
    if (event.target === dialog) dialog.close();
  });

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    const submitButton = form.querySelector('[type="submit"]');
    submitButton.disabled = true;
    try {
      const payload = Object.fromEntries(new FormData(form));
      const response = await fetch("/api/cameras", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.error || t("networkError"));
      dialog.close();
      toast(t("copyReady"));
      await refresh();
    } catch (error) {
      toast(error.message || t("networkError"), true);
    } finally {
      submitButton.disabled = false;
    }
  });

  grid.addEventListener("click", async (event) => {
    const button = event.target.closest("button[data-action]");
    if (!button) return;
    const card = button.closest("[data-camera-id]");
    const action = button.dataset.action === "toggle" ? button.dataset.nextAction : button.dataset.action;
    const cameraId = card.dataset.cameraId;
    button.disabled = true;
    try {
      const response = await fetch(`/api/cameras/${encodeURIComponent(cameraId)}${action === "remove" ? "" : `/${action}`}`, {
        method: action === "remove" ? "DELETE" : "POST",
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.error || t("networkError"));
      toast(t(action === "remove" ? "removedCamera" : action === "stop" ? "stoppedCamera" : "startedCamera"));
      await refresh();
    } catch (error) {
      toast(error.message || t("networkError"), true);
    } finally {
      button.disabled = false;
    }
  });

  window.addEventListener("visionflow:language-change", refresh);
  refresh();
  window.setInterval(refresh, 3500);
})();
