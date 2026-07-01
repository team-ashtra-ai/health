(() => {
  "use strict";

  window.SofiatiAnalytics = window.SofiatiAnalytics || {
    enabled: false,
    track() {
      return false;
    },
  };
})();
