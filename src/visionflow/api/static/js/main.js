(function () {
  const translations = {
    en: {
      workspace: "WORKSPACE", workspaceInfo: "WORKSPACE INFO", overview: "Overview", cameras: "Cameras",
      analytics: "Analytics", inference: "Inference lab", model: "Model", about: "About", support: "Support",
      modelStatus: "Model status", systemReady: "Inference ready", modelUnavailable: "Model unavailable",
      footerNote: "Traffic intelligence, made actionable.", overviewEyebrow: "OPERATIONS OVERVIEW",
      overviewTitle: "Your traffic operations at a glance.", overviewSubtitle: "A live view of your camera network and vehicle activity.",
      addCamera: "Add camera", connectedCameras: "Connected cameras", liveDetections: "Live detections",
      modelReadiness: "Model readiness", supportedClasses: "Vehicle classes", onlineNow: "online now",
      acrossActiveFeeds: "Across active camera feeds", modelClassesCaption: "Defined by your trained model",
      cameraNetwork: "Camera network", cameraNetworkSubtitle: "Monitor the feeds that matter to your operation.",
      viewAllCameras: "View all cameras", loadingCameras: "Loading camera network…", quickActions: "Quick actions",
      quickActionsSubtitle: "Get from insight to action faster.", runInference: "Run an inference",
      runInferenceHelp: "Analyze an image or recorded video", exploreAnalytics: "Explore analytics",
      exploreAnalyticsHelp: "Review detections by class and camera", checkModel: "Check your model",
      checkModelHelp: "Verify the deployed best checkpoint", makeItActionable: "Make it actionable",
      actionableHelp: "Connect a camera to start monitoring live traffic.", liveOperations: "LIVE OPERATIONS",
      camerasTitle: "Your camera network.", camerasSubtitle: "Connect and monitor USB cameras and RTSP streams from a single workspace.",
      connectCamera: "Connect a camera", camerasOnline: "cameras online", totalCameras: "total cameras", refresh: "Refresh",
      newConnection: "NEW CONNECTION", cameraName: "Camera name", cameraNamePlaceholder: "e.g. North entrance",
      streamSource: "Stream source", streamSourcePlaceholder: "0 or rtsp://camera.local:554/stream",
      sourceHelp: "Use a device index (0) or an RTSP/RTSPS URL. Source credentials are not persisted.",
      cameraCapacity: "Camera capacity is limited by your device's compute resources.", cancel: "Cancel",
      liveInsights: "LIVE INSIGHTS", analyticsTitle: "See what's moving.", analyticsSubtitle: "A real-time snapshot of vehicle detections across your active camera feeds.",
      activeCameras: "Active cameras", connectedStreams: "Connected live streams", vehiclesInView: "Vehicles in view",
      currentFrameSnapshot: "Current frame snapshot", classesDetected: "Classes detected", acrossCameraNetwork: "Across the camera network",
      classDistribution: "Vehicle class distribution", classDistributionHelp: "Detections currently visible across all connected cameras.",
      live: "LIVE", noDetectionsYet: "No detections yet. Connect a camera to see live data.", byCamera: "By camera",
      cameraDetectionSnapshot: "Current detection snapshot for each feed.", camera: "CAMERA", status: "STATUS",
      vehicles: "VEHICLES", fps: "FPS", analyticsDisclaimer: "Live counts reflect the latest processed frame. Historical trends require a persistent analytics store.",
      deployment: "DEPLOYMENT", modelTitle: "Your model, in production.", modelSubtitle: "Check the trained checkpoint backing live streams and on-demand inference.",
      activeCheckpoint: "ACTIVE CHECKPOINT", weightsAvailable: "Weights available", weightsUnavailable: "Weights unavailable",
      tryInference: "Try an inference", bestCheckpointHint: "Configured by model.trained_weights", modelClasses: "Model classes",
      modelClassesHelp: "Labels embedded in the trained checkpoint.", loadingModel: "Loading model details…",
      deploymentNotes: "Deployment notes", deploymentNotesHelp: "How the application connects your trained model to production features.",
      modelNoteOne: "Single source of truth", modelNoteOneHelp: "The checkpoint path is read from configs/pipeline_config.yaml and defaults to weights/best.pt.",
      modelNoteTwo: "Live camera inference", modelNoteTwoHelp: "Each connected camera runs object tracking with this trained model.",
      modelNoteThree: "On-demand processing", modelNoteThreeHelp: "Images and videos can be analyzed and downloaded in the Inference Lab.",
      onDemandAnalysis: "ON-DEMAND ANALYSIS", inferenceTitle: "Put your model to work.",
      inferenceSubtitle: "Upload images or recorded video and get annotated results from your trained checkpoint.",
      uploadMedia: "Upload media", uploadMediaHelp: "Images and videos, up to 100 MB total per request.",
      dropFiles: "Drop files here or browse", supportedFormats: "JPG, PNG, WEBP, MP4, MOV, AVI, MKV",
      privacyLocal: "Files are processed locally by this server.", inferenceTipTitle: "Built for quick review",
      inferenceTipText: "Annotated outputs are ready to preview and download as soon as processing completes.",
      maxUpload: "maximum upload size", activeModel: "active trained model", processedResults: "Processed results",
      processedResultsHelp: "Your annotated media is ready for review.", platform: "THE PLATFORM",
      aboutTitle: "Traffic intelligence, built for the real world.",
      aboutSubtitle: "VisionFlow brings trained computer vision models into a practical, operator-friendly workflow.",
      visionflowPlatform: "VISIONFLOW PLATFORM", aboutStoryTitle: "From model training to measurable operations.",
      aboutStory: "Deploy your best YOLO checkpoint, connect cameras, and turn vehicle detections into a clearer view of traffic activity. The platform is designed to keep model, camera, and analytics workflows together.",
      builtFor: "Designed for operators", builtForSubtitle: "A focused toolset for everyday decisions.",
      featureCameras: "Multi-camera monitoring", featureCamerasHelp: "Manage USB and RTSP video sources in one place.",
      featureModel: "Trained model deployment", featureModelHelp: "Serve detections using the project's best.pt checkpoint.",
      featureAnalytics: "Operational analytics", featureAnalyticsHelp: "Inspect current detections by class and camera.",
      featureLanguages: "English and Vietnamese", featureLanguagesHelp: "Choose your preferred interface language anytime.",
      helpCenter: "HELP CENTER", supportTitle: "Let's keep your operation moving.",
      supportSubtitle: "Quick guidance for getting VisionFlow connected and ready to work.",
      gettingStarted: "Getting started", gettingStartedSubtitle: "Follow these steps to bring your first camera online.",
      stepOne: "Verify the trained checkpoint", stepOneHelp: "Place your best.pt file at the path configured in pipeline_config.yaml.",
      stepTwo: "Connect a camera", stepTwoHelp: "Add a local device index or an RTSP/RTSPS stream URL.",
      stepThree: "Review live activity", stepThreeHelp: "Open Analytics to see the detections reported by active feeds.",
      needHelp: "Need a hand?", needHelpText: "For project or deployment questions, contact the VisionFlow team.",
      privacyTip: "Camera source credentials are kept in application memory and are not written to a config file.",
      connecting: "Connecting", online: "Online", offline: "Offline", stopped: "Stopped", detections: "detections",
      currentView: "Current view", processingSpeed: "Processing speed", retry: "Reconnect", stop: "Stop",
      remove: "Remove", connectFirstCamera: "Connect your first camera", noCamerasHelp: "Add a USB camera or RTSP stream to start seeing live detections.",
      noCamerasOverview: "No cameras connected yet", cameraOnline: "camera online", uploadError: "Unable to process this request.",
      chooseFiles: "Choose at least one file.", fileTooLarge: "The total upload size must be under 100 MB.",
      processing: "Processing your files…", noDetections: "No detections", detectionCount: "detections",
      sourceConnected: "Source", copyReady: "Camera added. Connecting to the stream…", removedCamera: "Camera removed.",
      stoppedCamera: "Camera stopped.", startedCamera: "Camera reconnecting…", inferenceFinished: "Inference complete.",
      unsupportedFile: "Unsupported file type.", loadingError: "Could not load camera data.", deviceSource: "Device",
      uploadFailed: "Upload failed", networkError: "A network error occurred. Please try again.", download: "Download",
      language: "Language", ready: "Ready", unavailable: "Unavailable",
    },
    vi: {
      workspace: "KHÔNG GIAN LÀM VIỆC", workspaceInfo: "THÔNG TIN", overview: "Tổng quan", cameras: "Camera",
      analytics: "Phân tích", inference: "Thử nghiệm AI", model: "Mô hình", about: "Giới thiệu", support: "Hỗ trợ",
      modelStatus: "Trạng thái mô hình", systemReady: "Sẵn sàng nhận diện", modelUnavailable: "Mô hình chưa khả dụng",
      footerNote: "Biến dữ liệu giao thông thành hành động.", overviewEyebrow: "TỔNG QUAN VẬN HÀNH",
      overviewTitle: "Toàn cảnh hoạt động giao thông.", overviewSubtitle: "Theo dõi trực tiếp hệ thống camera và hoạt động phương tiện.",
      addCamera: "Thêm camera", connectedCameras: "Camera đã kết nối", liveDetections: "Đối tượng đang nhận diện",
      modelReadiness: "Mô hình", supportedClasses: "Nhóm phương tiện", onlineNow: "đang trực tuyến",
      acrossActiveFeeds: "Trên các luồng camera đang hoạt động", modelClassesCaption: "Theo mô hình đã huấn luyện",
      cameraNetwork: "Mạng lưới camera", cameraNetworkSubtitle: "Theo dõi các luồng hình ảnh phục vụ vận hành.",
      viewAllCameras: "Xem tất cả camera", loadingCameras: "Đang tải mạng lưới camera…", quickActions: "Thao tác nhanh",
      quickActionsSubtitle: "Nhanh chóng chuyển từ dữ liệu sang hành động.", runInference: "Chạy nhận diện",
      runInferenceHelp: "Phân tích ảnh hoặc video có sẵn", exploreAnalytics: "Xem phân tích",
      exploreAnalyticsHelp: "Xem kết quả theo lớp và camera", checkModel: "Kiểm tra mô hình",
      checkModelHelp: "Xác minh checkpoint best đang triển khai", makeItActionable: "Bắt đầu giám sát",
      actionableHelp: "Kết nối camera để theo dõi giao thông trực tiếp.", liveOperations: "VẬN HÀNH TRỰC TIẾP",
      camerasTitle: "Mạng lưới camera.", camerasSubtitle: "Kết nối và theo dõi camera USB, luồng RTSP trong cùng một không gian làm việc.",
      connectCamera: "Kết nối camera", camerasOnline: "camera trực tuyến", totalCameras: "tổng số camera", refresh: "Làm mới",
      newConnection: "KẾT NỐI MỚI", cameraName: "Tên camera", cameraNamePlaceholder: "VD: Cổng phía Bắc",
      streamSource: "Nguồn video", streamSourcePlaceholder: "0 hoặc rtsp://camera.local:554/stream",
      sourceHelp: "Nhập chỉ số thiết bị (0) hoặc URL RTSP/RTSPS. Thông tin xác thực không được lưu lâu dài.",
      cameraCapacity: "Số camera phụ thuộc vào năng lực xử lý của thiết bị.", cancel: "Hủy",
      liveInsights: "THÔNG TIN TRỰC TIẾP", analyticsTitle: "Theo dõi chuyển động.", analyticsSubtitle: "Ảnh chụp tức thời các phương tiện được nhận diện trên camera đang hoạt động.",
      activeCameras: "Camera đang chạy", connectedStreams: "Luồng trực tiếp đã kết nối", vehiclesInView: "Phương tiện trong khung hình",
      currentFrameSnapshot: "Thống kê khung hình hiện tại", classesDetected: "Lớp được nhận diện", acrossCameraNetwork: "Trên toàn mạng lưới camera",
      classDistribution: "Phân bố phương tiện theo lớp", classDistributionHelp: "Đối tượng đang xuất hiện trên các camera đã kết nối.",
      live: "TRỰC TIẾP", noDetectionsYet: "Chưa có kết quả. Hãy kết nối camera để xem dữ liệu.", byCamera: "Theo camera",
      cameraDetectionSnapshot: "Ảnh chụp nhận diện hiện tại của từng luồng.", camera: "CAMERA", status: "TRẠNG THÁI",
      vehicles: "PHƯƠNG TIỆN", fps: "FPS", analyticsDisclaimer: "Số liệu trực tiếp phản ánh khung hình mới nhất. Thống kê lịch sử cần kho dữ liệu lưu trữ riêng.",
      deployment: "TRIỂN KHAI", modelTitle: "Mô hình đang vận hành.", modelSubtitle: "Kiểm tra checkpoint đang phục vụ luồng trực tiếp và nhận diện theo yêu cầu.",
      activeCheckpoint: "CHECKPOINT ĐANG DÙNG", weightsAvailable: "Đã tìm thấy trọng số", weightsUnavailable: "Chưa tìm thấy trọng số",
      tryInference: "Thử nhận diện", bestCheckpointHint: "Được cấu hình tại model.trained_weights", modelClasses: "Các lớp của mô hình",
      modelClassesHelp: "Nhãn được nhúng trong checkpoint đã huấn luyện.", loadingModel: "Đang tải thông tin mô hình…",
      deploymentNotes: "Thông tin triển khai", deploymentNotesHelp: "Cách ứng dụng kết nối mô hình với các tính năng vận hành.",
      modelNoteOne: "Một nguồn cấu hình", modelNoteOneHelp: "Đường dẫn checkpoint đọc từ configs/pipeline_config.yaml, mặc định là weights/best.pt.",
      modelNoteTwo: "Nhận diện camera trực tiếp", modelNoteTwoHelp: "Mỗi camera kết nối chạy theo dõi đối tượng bằng mô hình đã huấn luyện.",
      modelNoteThree: "Xử lý theo yêu cầu", modelNoteThreeHelp: "Có thể phân tích và tải ảnh/video trong mục Thử nghiệm AI.",
      onDemandAnalysis: "PHÂN TÍCH THEO YÊU CẦU", inferenceTitle: "Đưa mô hình vào sử dụng.",
      inferenceSubtitle: "Tải ảnh hoặc video để nhận kết quả đã đánh dấu bằng checkpoint đã huấn luyện.",
      uploadMedia: "Tải dữ liệu", uploadMediaHelp: "Ảnh và video, tổng dung lượng tối đa 100 MB mỗi lần.",
      dropFiles: "Thả tệp vào đây hoặc chọn tệp", supportedFormats: "JPG, PNG, WEBP, MP4, MOV, AVI, MKV",
      privacyLocal: "Tệp được xử lý trực tiếp trên máy chủ này.", inferenceTipTitle: "Xem kết quả nhanh",
      inferenceTipText: "Kết quả đã đánh dấu có thể xem trước và tải xuống ngay sau khi xử lý.",
      maxUpload: "dung lượng tải lên tối đa", activeModel: "mô hình đang hoạt động", processedResults: "Kết quả xử lý",
      processedResultsHelp: "Dữ liệu đã đánh dấu sẵn sàng để xem.", platform: "NỀN TẢNG",
      aboutTitle: "Phân tích giao thông cho vận hành thực tế.",
      aboutSubtitle: "VisionFlow đưa mô hình thị giác máy tính đã huấn luyện vào quy trình làm việc thân thiện, thiết thực.",
      visionflowPlatform: "NỀN TẢNG VISIONFLOW", aboutStoryTitle: "Từ huấn luyện mô hình đến hiệu quả vận hành.",
      aboutStory: "Triển khai checkpoint YOLO tốt nhất, kết nối camera và biến kết quả nhận diện thành góc nhìn rõ ràng hơn về giao thông. Nền tảng kết nối quy trình mô hình, camera và phân tích.",
      builtFor: "Thiết kế cho người vận hành", builtForSubtitle: "Bộ công cụ tập trung cho các quyết định hằng ngày.",
      featureCameras: "Giám sát nhiều camera", featureCamerasHelp: "Quản lý nguồn video USB và RTSP tại một nơi.",
      featureModel: "Triển khai mô hình đã huấn luyện", featureModelHelp: "Nhận diện bằng checkpoint best.pt của dự án.",
      featureAnalytics: "Phân tích vận hành", featureAnalyticsHelp: "Kiểm tra kết quả hiện tại theo lớp và camera.",
      featureLanguages: "Tiếng Anh và tiếng Việt", featureLanguagesHelp: "Chọn ngôn ngữ giao diện bất kỳ lúc nào.",
      helpCenter: "TRUNG TÂM TRỢ GIÚP", supportTitle: "Giữ cho hoạt động luôn thông suốt.",
      supportSubtitle: "Hướng dẫn nhanh để kết nối và vận hành VisionFlow.",
      gettingStarted: "Bắt đầu sử dụng", gettingStartedSubtitle: "Làm theo các bước để kết nối camera đầu tiên.",
      stepOne: "Xác minh checkpoint", stepOneHelp: "Đặt tệp best.pt theo đường dẫn cấu hình trong pipeline_config.yaml.",
      stepTwo: "Kết nối camera", stepTwoHelp: "Thêm chỉ số thiết bị hoặc URL luồng RTSP/RTSPS.",
      stepThree: "Theo dõi hoạt động", stepThreeHelp: "Mở mục Phân tích để xem kết quả từ các luồng đang chạy.",
      needHelp: "Bạn cần hỗ trợ?", needHelpText: "Liên hệ nhóm VisionFlow nếu có câu hỏi về dự án hoặc triển khai.",
      privacyTip: "Thông tin xác thực của camera chỉ nằm trong bộ nhớ ứng dụng, không ghi vào tệp cấu hình.",
      connecting: "Đang kết nối", online: "Trực tuyến", offline: "Ngoại tuyến", stopped: "Đã dừng", detections: "đối tượng",
      currentView: "Khung hình hiện tại", processingSpeed: "Tốc độ xử lý", retry: "Kết nối lại", stop: "Dừng",
      remove: "Xóa", connectFirstCamera: "Kết nối camera đầu tiên", noCamerasHelp: "Thêm camera USB hoặc luồng RTSP để bắt đầu nhận diện trực tiếp.",
      noCamerasOverview: "Chưa có camera nào được kết nối", cameraOnline: "camera trực tuyến", uploadError: "Không thể xử lý yêu cầu này.",
      chooseFiles: "Hãy chọn ít nhất một tệp.", fileTooLarge: "Tổng dung lượng tải lên phải dưới 100 MB.",
      processing: "Đang xử lý tệp…", noDetections: "Không có đối tượng", detectionCount: "đối tượng",
      sourceConnected: "Nguồn", copyReady: "Đã thêm camera. Đang kết nối luồng…", removedCamera: "Đã xóa camera.",
      stoppedCamera: "Đã dừng camera.", startedCamera: "Đang kết nối lại camera…", inferenceFinished: "Đã hoàn tất nhận diện.",
      unsupportedFile: "Định dạng tệp không được hỗ trợ.", loadingError: "Không thể tải dữ liệu camera.", deviceSource: "Thiết bị",
      uploadFailed: "Tải lên thất bại", networkError: "Đã xảy ra lỗi mạng. Vui lòng thử lại.", download: "Tải xuống",
      language: "Ngôn ngữ", ready: "Sẵn sàng", unavailable: "Chưa khả dụng",
    },
  };

  let language = localStorage.getItem("visionflow-language") || "en";
  if (!translations[language]) language = "en";

  function applyLanguage() {
    document.documentElement.lang = language;
    document.querySelectorAll("[data-i18n]").forEach((element) => {
      const translated = translations[language][element.dataset.i18n];
      if (translated) element.textContent = translated;
    });
    document.querySelectorAll("[data-i18n-placeholder]").forEach((element) => {
      const translated = translations[language][element.dataset.i18nPlaceholder];
      if (translated) element.placeholder = translated;
    });
    document.querySelectorAll("[data-i18n-aria-label]").forEach((element) => {
      const translated = translations[language][element.dataset.i18nAriaLabel];
      if (translated) element.setAttribute("aria-label", translated);
    });
    document.querySelectorAll("[data-language]").forEach((button) => {
      button.setAttribute("aria-pressed", String(button.dataset.language === language));
    });
    const activeNavigation = document.querySelector(".nav-link.active [data-i18n]");
    if (activeNavigation) document.title = `${activeNavigation.textContent} · VisionFlow`;
    window.dispatchEvent(new CustomEvent("visionflow:language-change", { detail: { language } }));
  }

  document.querySelectorAll("[data-language]").forEach((button) => {
    button.addEventListener("click", () => {
      language = button.dataset.language;
      localStorage.setItem("visionflow-language", language);
      applyLanguage();
    });
  });

  const sidebar = document.getElementById("sidebar");
  const scrim = document.getElementById("mobile-scrim");
  function closeMenu() {
    sidebar?.classList.remove("is-open");
    scrim?.classList.remove("is-visible");
  }
  document.getElementById("mobile-menu")?.addEventListener("click", () => {
    sidebar?.classList.toggle("is-open");
    scrim?.classList.toggle("is-visible");
  });
  scrim?.addEventListener("click", closeMenu);
  sidebar?.querySelectorAll(".nav-link").forEach((link) => link.addEventListener("click", closeMenu));

  window.VisionFlow = {
    t: (key) => translations[language][key] || translations.en[key] || key,
    escape: (value) => String(value).replace(/[&<>"']/g, (character) => ({
      "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;",
    })[character]),
    toast(message, isError = false) {
      const region = document.getElementById("toast-region");
      if (!region) return;
      const toast = document.createElement("div");
      toast.className = `toast${isError ? " is-error" : ""}`;
      toast.textContent = message;
      region.append(toast);
      window.setTimeout(() => toast.remove(), 4200);
    },
  };
  applyLanguage();

  fetch("/api/cameras")
    .then((response) => response.ok ? response.json() : null)
    .then((data) => {
      const badge = document.getElementById("nav-camera-count");
      if (badge && data) badge.textContent = data.cameras.length;
    })
    .catch(() => {});
})();
