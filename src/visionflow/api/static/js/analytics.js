(function () {
  const { t, escape } = window.VisionFlow;
  const canvas = document.getElementById("class-chart");
  const context = canvas.getContext("2d");
  const colors = ["#5272e9", "#8d73db", "#36a983", "#e3a23b", "#e16d68", "#4b9db6"];
  let latestData = null;

  function drawChart(classes) {
    const entries = Object.entries(classes || {}).sort((left, right) => right[1] - left[1]);
    const ratio = window.devicePixelRatio || 1;
    const bounds = canvas.getBoundingClientRect();
    canvas.width = Math.max(1, Math.floor(bounds.width * ratio));
    canvas.height = Math.max(1, Math.floor(bounds.height * ratio));
    context.setTransform(ratio, 0, 0, ratio, 0, 0);
    context.clearRect(0, 0, bounds.width, bounds.height);
    document.getElementById("chart-empty").hidden = entries.length > 0;
    if (!entries.length) return;

    const maxValue = Math.max(...entries.map((entry) => entry[1]), 1);
    const left = 20;
    const right = 16;
    const top = 14;
    const barHeight = 17;
    const gap = 16;
    const labelWidth = 94;
    const valueWidth = 32;
    const barWidth = Math.max(20, bounds.width - left - right - labelWidth - valueWidth);
    context.font = "10px DM Sans, sans-serif";
    entries.forEach(([name, count], index) => {
      const y = top + index * (barHeight + gap);
      context.fillStyle = "#637084";
      context.textAlign = "left";
      context.fillText(name, left, y + 12);
      context.fillStyle = "#f0f2f7";
      context.beginPath();
      context.roundRect(left + labelWidth, y, barWidth, barHeight, 5);
      context.fill();
      context.fillStyle = colors[index % colors.length];
      context.beginPath();
      context.roundRect(left + labelWidth, y, Math.max(4, barWidth * count / maxValue), barHeight, 5);
      context.fill();
      context.fillStyle = "#596579";
      context.textAlign = "right";
      context.fillText(String(count), left + labelWidth + barWidth + valueWidth, y + 12);
    });
  }

  function renderRows(cameras) {
    const rows = document.getElementById("analytics-camera-rows");
    if (!cameras.length) {
      rows.innerHTML = `<tr><td class="table-empty" colspan="4">${escape(t("noCamerasOverview"))}</td></tr>`;
      return;
    }
    rows.innerHTML = cameras.map((camera) => {
      const vehicles = Object.values(camera.counts || {}).reduce((sum, count) => sum + count, 0);
      const status = camera.status === "online" ? "online" : camera.status === "connecting" ? "connecting" : "offline";
      const dot = status === "online" ? "is-ready" : status === "offline" ? "is-offline" : "is-warning";
      return `<tr><td>${escape(camera.name)}</td><td><span class="camera-status"><span class="status-dot ${dot}"></span>${escape(t(status))}</span></td><td>${vehicles}</td><td>${camera.fps ? `${camera.fps} FPS` : "—"}</td></tr>`;
    }).join("");
  }

  async function refresh() {
    try {
      const response = await fetch("/api/analytics");
      if (!response.ok) throw new Error(t("loadingError"));
      latestData = await response.json();
      document.getElementById("analytics-online").textContent = latestData.online_cameras;
      document.getElementById("analytics-detections").textContent = latestData.detections;
      document.getElementById("analytics-classes").textContent = Object.keys(latestData.classes).length;
      document.getElementById("nav-camera-count").textContent = latestData.camera_count;
      renderRows(latestData.cameras);
      drawChart(latestData.classes);
    } catch (_error) {
      document.getElementById("analytics-camera-rows").innerHTML = `<tr><td class="table-empty" colspan="4">${escape(t("networkError"))}</td></tr>`;
    }
  }

  window.addEventListener("resize", () => latestData && drawChart(latestData.classes));
  window.addEventListener("visionflow:language-change", () => latestData && drawChart(latestData.classes));
  refresh();
  window.setInterval(refresh, 3500);
})();
