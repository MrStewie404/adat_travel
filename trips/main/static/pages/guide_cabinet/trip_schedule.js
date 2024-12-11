"use strict";
$(document).ready(function() {

  const csrfToken = getCsrfToken();

  $(document).delegate('.js-edit-guide-payment', "click", function() {
    let $self = $(this);
    let initialAmount = $self.attr("data-initial-amount");
    let totalAmount = $self.attr("data-total-amount");
    let purpose = $self.attr("data-purpose");
    let tag = $self.attr("data-payment-tag");
    let dataRequestUrl = $self.attr("data-request-url");
    let title = tag === 'service' ? `Оплата услуги "${purpose}"` :
      ('extra' ? `Редактирование доп. расходов "${purpose}"` : `Оплата гостиницы ${purpose}`);
    let message = totalAmount ?
      `Полная стоимость ${tag === 'service' ? 'услуги' : 'гостиницы'}: ${totalAmount}.<br>Всего оплачено:` :
      "Всего оплачено:";

    promptWithCallback({
      title: title,
      message: message,
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

  $('.js-payment-create').click(function() {
    showCreatePaymentDialog($(this).attr("data-content-url"));
  });

  function showCreatePaymentDialog(content_url) {
    simpleGetRequest({
      url: content_url,
      success: function(response) {
        bootbox.dialog({
          title: "Новая статья расходов",
          size: 'large',
          message: response,
        });
      },
    });
  }

});