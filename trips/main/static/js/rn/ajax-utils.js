function simplePostRequest(options) {
  let defaultOptions = {
    type: 'POST',
    headers: {'X-CSRFToken': options.csrfToken},
    crossDomain: false,
    success: function(response) {
      document.location.reload();
    },
    error: function(response) {
      console.log(response);
      let responseJson = response["responseJSON"];
      if (responseJson && responseJson["error"]) {
        bootbox.alert(responseJson["error"]);
      } else {
        bootbox.alert("Ошибка при обработке запроса. Попробуйте перезагрузить страницу.");
      }
    }
  };
  let allOptions = Object.assign({}, defaultOptions, options);
  $.ajax(allOptions);
}

function simpleGetRequest(options) {
  let defaultOptions = {
    type: 'GET',
    success: function(response) {
      document.location.reload();
    },
    error: function(response) {
      console.log(response);
      bootbox.alert("Ошибка при обработке запроса. Попробуйте перезагрузить страницу.");
    }
  };
  let allOptions = Object.assign({}, defaultOptions, options);
  $.ajax(allOptions);
}
