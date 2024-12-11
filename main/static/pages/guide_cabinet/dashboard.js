"use strict";
$(document).ready(function() {

  const csrfToken = getCsrfToken();

  $(document).delegate('.js-edit-guide-payment', "click", function() {
    let $self = $(this);
    let initialAmount = $self.attr("data-initial-amount");
    let contractRemaining = $self.attr("data-total-amount");
    let dataRequestUrl = $self.attr("data-request-url");

    promptWithCallback({
      title: "Оплата тура",
      message: `Доплата от гостя по договору: ${contractRemaining}.<br>Всего получено:`,
      inputType: 'number',
      value: initialAmount,
      callback: function(result) {
        if (result) {
          if (result <= 0) {
            bootbox.alert("Введите положительную сумму");
            return;
          }
          simplePostRequest({
            url: dataRequestUrl,
            data: {'amount': result},
            csrfToken: csrfToken,
          });
        }
      },
    });

    return false;
  });

});