"use strict";
$(document).ready(function() {

  const csrfToken = getCsrfToken();

  $(document).delegate('.js-add-commission-payment', "click", function() {
    let $self = $(this);
    addCommissionPayment($self.attr("data-initial-amount"), $self.attr("data-total-amount"),
      $self.attr("data-request-url"));
    return false;
  });

  function addCommissionPayment(initialAmount, totalAmount, dataRequestUrl) {
    let remainingAmount = initialAmount;
    promptWithCallback({
      title: "Новый платёж контрагенту",
      message: `Комиссия контрагента по договору: ${totalAmount}.<br>Остаток к оплате: ${remainingAmount}.<br>Сумма платежа:`,
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
  }

});
