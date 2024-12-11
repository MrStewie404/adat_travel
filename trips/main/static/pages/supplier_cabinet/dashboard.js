"use strict";
$(document).ready(function() {

  const csrfToken = getCsrfToken();

  $('.js-create-guest-link').click(function() {
    let self = $(this);
    createPersonalCabinet(self.attr("data-request-url"), function(response) {
      document.location.reload();
    });
  });

  $('.js-copy-qr-code').click(function() {
    copyQrCode($('.js-qr-code').find('img'));
  });

  $('.js-copy-guest-link').click(function() {
    copyToClipboard(
      $(this).attr('data-url'),
      "Ссылка для самозаписи скопирована в буфер обмена.",
      "Ссылка для самозаписи",
    );
  });

  function createPersonalCabinet(requestUrl, success) {
    simplePostRequest({
      url: requestUrl,
      csrfToken: csrfToken,
      success: success,
    });
  }

  function copyQrCode($img) {
    return copyImageToClipboard($img).then(
      function() {
        showFadeOutMessage("QR-код скопирован в буфер обмена.");
      },
      function(e) {
        bootbox.alert("Не удалось скопировать QR-код.");
        console.log(e);
      }
    );
  }

});
