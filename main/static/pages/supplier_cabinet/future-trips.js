"use strict";
$(document).ready(function() {

  $('.js-description-popup').click(function() {
    let $self = $(this);
    let text = $self.attr("data-text");
    let dialog = bootbox.dialog({
      message: text,
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
