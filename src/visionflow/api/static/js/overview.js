(function () {
  const { t, escape } = window.VisionFlow;
  const list = document.getElementById("overview-cameras");

  function renderCameras(cameras) {
    if (!cameras.length) {
      list.innerHTML = `<div class="empty-state"><span class="empty-illustration">▣</span><strong>${escape(t("noCamerasOverview"))}</strong><p>${escape(t("noCamerasHelp"))}</p><a class="button button-secondary button-small" href="/cameras">＋ ${escape(t("addCamera"))}</a></div>`;
      return;
    }
    list.innerHTML = cameras.map((camera) => {
      const count = Object.values(camera.counts).reduce((total, value) => total + value, 0);
      const status = camera.status === "online" ? "online" : camera.status === "connecting" ? "connecting" : "offline";
      return `<div class="camera-row">
        <span class="camera-thumb">▣</span>
        <span class="camera-row-name"><strong>${escape(camera.name)}</strong><small>${escape(camera.source)}</small></span>
        <span class="camera-status"><span class="status-dot ${status === "online" ? "is-ready" : status === "offline" ? "is-offline" : "is-warning"}"></span>${escape(t(status))}</span>
        <span class="camera-row-count">${count} ${escape(t("detections"))}</span>
      </div>`;
    }).join("");
  }

  async function refresh() {
    try {
      const response = await fetch("/api/overview");
      if (!response.ok) throw new Error(t("loadingError"));
      const data = await response.json();
      document.getElementById("metric-cameras").textContent = data.camera_count;
      document.getElementById("metric-online").textContent = data.online_cameras;
      document.getElementById("metric-detections").textContent = data.detections;
      document.getElementById("metric-classes").textContent = data.model.classes.length || "—";
      document.getElementById("nav-camera-count").textContent = data.camera_count;
      renderCameras(data.cameras);
    } catch (error) {
      list.innerHTML = `<div class="empty-state"><strong>${escape(error.message || t("networkError"))}</strong></div>`;
    }
  }

  refresh();
  window.setInterval(refresh, 4000);
})();
