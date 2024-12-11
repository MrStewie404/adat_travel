"use strict";
$(document).ready(function() {

  $('.js-dds-warning').click(function(e) {
    e.preventDefault()
    let $self = $(this);
    bootbox.alert({
      message:
        "Не удалось рассчитать стоимость некоторых услуг.\n" +
        "Для исправления ошибок в услугах перейдите в раздел Программа тура.",
      callback: function() {
        location.href = $self.attr("href");
      }
    });
  });

});
