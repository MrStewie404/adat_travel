"use strict";
$(document).ready(function() {

  $('.rn-messages').children('li').each(function() {
    bootbox.alert({
      message: $(this).html(),
      size: 'large',
    });
  });

  $('.js-custom-dialog').click(function() {
    let message = $('.js-custom-dialog-message').html();
    let dialog = bootbox.dialog({
      message: message,
    });
    dialog.find('.modal-dialog').css({
      'top': '50vh',
      'transform': 'translateY(-50%)',
    });
    dialog.find('.bootbox-body').css({
      'max-height': '80vh',
      'overflow-y': 'auto',
      'display': 'inline-block',
    });
    dialog.find('.bootbox-close-button').css({
      'font-size': '2.5rem',
      'transform': 'translateY(-15px)',
    });
  });

});
