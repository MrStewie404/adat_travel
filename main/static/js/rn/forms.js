"use strict";
$(document).ready(function() {
  let submitTimeMs = 0;

  $(".js-form-submit-once").on("submit", function(e) {
    // Защита от случайной повторной отправки формы (например, при двойном щелчке мышью).
    let timeMs = Date.now();
    let timeoutMs = 10000;
    if (submitTimeMs + timeoutMs > timeMs) {
      showFadeOutMessage("Вы уже отправили эти данные. Подождите, пожалуйста...");
      e.preventDefault();
    }
    submitTimeMs = timeMs;
  });

  $(".js-cancel-btn").on('click', function() {
    if (submitTimeMs === 0) {
      location.href = $(this).attr("data-on-cancel-url");
    } else {
      showFadeOutMessage("Вы уже отправили эти данные. Подождите, пожалуйста...");
    }
  });
});
