"use strict";

$(document).on('click', '#id_today_btn', function(e) {
  submit_today();
});

$(document).on('click', '#id_yesterday_btn', function(e) {
  submit_yesterday();
});

$(document).on('change', '#id_start_date', function(e) {
  submit_date();
});

$(document).on('change', '#id_end_date', function(e) {
  submit_date();
});

$(document).on('on-date-selected', function() {
  submit_date();
});

$(document).on('change', '.js-submit-month', function(e) {
  submit_month();
});

function submit_month() {
  document.getElementById("id_start_date").value = "";
  document.getElementById("id_end_date").value = "";
  //document.forms[0].submit();
}

function submit_date() {
  document.getElementById("id_month").value = "";
  //document.forms[0].submit();
}

function submit_yesterday() {
  var today = new Date();
  today.setDate(today.getDate() - 1);
  set_date(today);
  submit_date();
}

function submit_today() {
  set_date(new Date());
  submit_date();
}

function set_date(today) {
  var start = document.getElementById("id_start_date");
  var end = document.getElementById("id_end_date");
  var day = today.getDate().toString().padStart(2, '0'); // получаем день и добавляем ведущий ноль, если нужно
  var month = (today.getMonth() + 1).toString().padStart(2, '0'); // получаем месяц и добавляем ведущий ноль, если нужно
  var year = today.getFullYear(); // получаем год
  start.value = day + '.' + month + '.' + year; // форматируем дату в формат dd.mm.yyyy
  end.value = day + '.' + month + '.' + year; // форматируем дату в формат dd.mm.yyyy
}
