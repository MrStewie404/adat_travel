"use strict";
$(document).ready(function() {

  const csrfToken = getCsrfToken();

  $('.js-table-view-multi_select_two_side').click(function() {
    let self = $(this);
    customSelect({
      title: self.attr("data-dialog-title"),
      inputOptionsFieldId: self.attr("data-choices"),
      initialValuesFieldId: self.attr("data-initial-values"),
      multiple: true,
      message: self.attr("data-dialog-message"),
      className: 'bootbox-select-height-lg',
      size: 'large',
      twoSideMultiselect: true,
      leftHeaderText: self.attr("data-left-header"),
      rightHeaderText: self.attr("data-right-header"),
      callback: function(result) {
        if (result) {
          sendAjaxRequest(result, self.attr("data-row-pk"), self.attr("data-action-name"));
        }
      }
    });
  });

  $('.js-table-view-multi_select').click(function() {
    let self = $(this);
    customSelect({
      title: self.attr("data-dialog-title"),
      inputOptionsFieldId: self.attr("data-choices"),
      initialValuesFieldId: self.attr("data-initial-values"),
      multiple: true,
      message: self.attr("data-dialog-message"),
      className: 'bootbox-select-height-lg',
      twoSideMultiselect: false,
      callback: function(result) {
        if (result) {
          sendAjaxRequest(result, self.attr("data-row-pk"), self.attr("data-action-name"));
        }
      }
    });
  });

  $('.js-table-view-select').click(function() {
    let self = $(this);
    customSelect({
      title: self.attr("data-dialog-title"),
      inputOptionsFieldId: self.attr("data-choices"),
      initialValuesFieldId: self.attr("data-initial-values"),
      multiple: false,
      message: self.attr("data-dialog-message"),
      callback: function(result) {
        if (result) {
          sendAjaxRequest(result, self.attr("data-row-pk"), self.attr("data-action-name"));
        }
      }
    });
  });

  $('.js-table-view-confirm').click(function() {
    let self = $(this);
    confirmWithCallback({
      message: self.attr("data-dialog-message"),
      callback: function(result) {
        if (result) {
          sendAjaxRequest(result, self.attr("data-row-pk"), self.attr("data-action-name"));
        }
      },
    });
  });

  $('.js-table-view-confirm_and_redirect').click(function() {
    let self = $(this);
    confirmWithCallback({
      message: self.attr("data-dialog-message"),
      callback: function(result) {
        if (result) {
          let redirect_to = self.attr("data-redirect-url");
          sendAjaxRequest(result, self.attr("data-row-pk"), self.attr("data-action-name"),
            function(response) {
              location.href = redirect_to
            })
        }
      },
    });
  });

  $('.js-table-view-redirect').click(function() {
    location.href = $(this).attr("data-redirect-url");
  });

  $('.js-table-view-submit').click(function() {
    let self = $(this);
    sendAjaxRequest('', self.attr("data-row-pk"), self.attr("data-action-name"));
  });

  $('.js-table-view-alert').click(function() {
    let self = $(this);
    bootbox.alert(self.attr("data-dialog-message"));
  });

  function sendAjaxRequest(result, rowPk, actionName, success = null) {
    if (success == null) {
      success = function(response) {
        if (response.redirect_to) {
          location.href = response.redirect_to
        } else {
          document.location.reload();
        }
      }
    }
    $.ajax({
      type: 'POST',
      data: {'result': JSON.stringify(result), 'pk': rowPk, 'action_name': actionName},
      headers: {'X-CSRFToken': csrfToken},
      success: success,
      error: function(response) {
        console.log(response);
        bootbox.alert("Ошибка при обработке запроса.");
      }
    });
  }

});
