"use strict";
$(document).ready(function() {
  $(".js-select-object-checkbox").on("click", function() {
    updateActionButtonsForSelection();
  });
});

function updateActionButtonsForSelection() {
  let isAnyChecked = $(".js-select-object-checkbox").is(":checked");
  let $btn = $(".js-selected-objects-action-btn");
  if (isAnyChecked) {
    $btn.show();
  } else {
    $btn.hide();
  }
}

function setDeleteButtonHandler(objsParamName, prevPageParamName, cannotDeleteMsgPrefix) {
  $(".js-delete-selected-objects-btn").on("click", function() {
    let $self = $(this);
    deleteSelectedObjects($self.attr("data-request-url"), objsParamName, prevPageParamName, cannotDeleteMsgPrefix);
  });
}

function getSelectedCheckboxes() {
  return $(".js-select-object-checkbox").filter(":checked");
}

function deleteSelectedObjects(requestUrl, objsParamName, prevPageParamName, cannotDeleteMsgPrefix) {
  let $selectedCheckboxes = getSelectedCheckboxes();
  let $forbiddenObjectNames = $selectedCheckboxes.filter(function() {
    let mayDelete = $(this).attr("data-may-delete");
    return mayDelete === "False";
  }).map(function() {
    return $(this).attr("data-object-name");
  });

  if ($forbiddenObjectNames.length === 0) {
    let itemPks = $selectedCheckboxes.map(function() {
      return $(this).attr("data-object-pk");
    }).get();
    let joinedPks = itemPks.join(`&${objsParamName}=`);
    location.href = `${requestUrl}?${objsParamName}=${joinedPks}&${prevPageParamName}=${encodeURIComponent(location.href)}`;
  } else {
    let objectsStr = $forbiddenObjectNames.get().join("<br>");
    bootbox.alert(`${cannotDeleteMsgPrefix}<br>${objectsStr}`);
  }
}
