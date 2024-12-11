"use strict";
$(document).ready(function() {

  const csrfToken = getCsrfToken();

  $(document).delegate('.js-booking-confirm', "click", function() {
    simplePostRequest({
      url: $(this).attr("data-request-url"),
      csrfToken: csrfToken,
    });
  });
});
