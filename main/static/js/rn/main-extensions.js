"use strict";
$(document).ready(function() {
  initAllFormJs();
});

function initAllFormJs($container = null) {
  initFormWidgets($container);
  initMaxLength($container);
}

function initFormWidgets($container = null) {
  advancedQuery('.js-select2', $container).select2({
    theme: 'bootstrap4',
    language: 'ru',
  });

  advancedQuery('.js-multi-select2', $container).each(function(index) {
    initMultiSelect2($(this));
  });

  advancedQuery('.js-select2-larger', $container).select2({
    dropdownCssClass: 'rn-select2-increased-height',
    theme: 'bootstrap4',
    language: 'ru',
  });

  advancedQuery('.mat-date-picker', $container).bootstrapMaterialDatePicker({
    time: false,
    format: 'DD.MM.YYYY',
    weekStart: 1,
    clearButton: true,
    lang: 'ru',
    clearText: 'Очистить',
    cancelText: 'Отмена',
    switchOnClick: true,
  });

  advancedQuery('.mat-date-time-hm-picker', $container).bootstrapMaterialDatePicker({
    time: true,
    format: 'DD.MM.YYYY HH:mm',
    weekStart: 1,
    clearButton: true,
    lang: 'ru',
    clearText: 'Очистить',
    cancelText: 'Отмена',
    switchOnClick: true,
  });

  advancedQuery('.bootstrap-date-picker', $container).datepicker({
    format: 'dd.mm.yyyy',
    autoclose: true,
    language: 'ru',
  });

  initDateRangePicker('.bootstrap-date-picker2', {}, $container)

  advancedQuery('.date-picker-multiselect', $container).datepicker({
    multidate: true,
    format: 'dd.mm.yyyy',
    language: 'ru',
  });
}

function initMaxLength($container = null) {
  advancedQuery('input[maxlength]', $container).maxlength();

  advancedQuery('input.thresold-i', $container).maxlength({
    threshold: 20
  });

  advancedQuery('input.color-class', $container).maxlength({
    alwaysShow: true,
    threshold: 10,
    warningClass: "label label-success",
    limitReachedClass: "label label-danger"
  });

  advancedQuery('input.position-class', $container).maxlength({
    alwaysShow: true,
    placement: 'top-left'
  });

  advancedQuery('textarea.max-textarea', $container).maxlength({
    alwaysShow: true
  });
}

function initDateRangePicker(selector, options, $container = null) {
  moment.locale('ru');
  let defaultOptions = {
    autoclose: true,
    locale: {
      format: 'DD.MM.YYYY',
    },
    singleDatePicker: true,
    showDropdowns: true,
    minDate: '01.01.1900',
    maxDate: '01.01.2030',
    autoUpdateInput: false,
  }
  let allOptions = Object.assign({}, defaultOptions, options);
  let picker = advancedQuery(selector, $container);
  picker.daterangepicker(allOptions);
  picker.on('apply.daterangepicker', function(e, picker) {
    $(this).val(picker.startDate.format('L'));
    $(this).trigger('on-date-selected');
  });
  return picker;
}

function initMultiSelect2($elem) {
  // В django можно задавать атрибуты элемента select, но select2 с опцией мультиселект не использует их.
  // Поэтому приходится их прокидывать тут. Заодно используем placeholder при отсутствии элементов для выбора.

  let customLanguage = {}
  let placeholder = $elem.attr('placeholder');
  if (placeholder && $elem.children("option").length === 0) {
    customLanguage.noResults = function() {
      return placeholder;
    }
  }

  $elem.select2({
    theme: 'bootstrap4',
    placeholder: placeholder,
    language: [customLanguage, 'ru'],
  });
}

function advancedQuery(q, $container = null) {
  if ($container) {
    return $container.find(q);
  }
  return $(q);
}

function pop(dict, key, defaultValue = null) {
  if (key in dict) {
    let v = dict[key];
    delete dict[key];
    return v;
  }
  return defaultValue;
}

function showFadeOutMessage(message, delay = 2500) {
  $.growl({
    message: message,
  }, {
    element: 'body',
    type: 'inverse',
    allow_dismiss: true,
    placement: {
      from: 'top',
      align: 'right',
    },
    offset: {
      x: 60,
      y: 60
    },
    spacing: 10,
    delay: delay,
    animate: {
      enter: 'animated fadeInDown',
      exit: 'animated fadeOutDown'
    },
  });
}
