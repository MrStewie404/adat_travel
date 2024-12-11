function customSelect(args) {
  let defaultArgs = {
    inputType: 'select',
    buttons: {
      cancel: {
        label: 'Отмена',
        className: 'btn btn-secondary'
      },
      confirm: {
        label: 'OK',
        className: 'btn btn-primary m-l-5'
      },
    },
  };
  let allArgs = Object.assign({}, defaultArgs, args);
  // Удаляем из allArgs все аргументы, которые не относятся к bootbox
  [
    'inputOptionsFieldId', 'initialValues', 'initialValuesFieldId',
    'selectSize', 'withSearch', 'twoSideMultiSelect', 'ajax', 'placeholder',
  ].forEach(e => delete allArgs[e]);
  if (args.inputOptionsFieldId) {
    allArgs.inputOptions = JSON.parse($('#' + args.inputOptionsFieldId).text());
  }
  if (args.initialValues) {
    allArgs.value = args.initialValues;
  } else if (args.initialValuesFieldId) {
    allArgs.value = JSON.parse($('#' + args.initialValuesFieldId).text());
  }

  let dialog = bootbox.prompt(allArgs);

  dialog.init(function() {
    if (args.twoSideMultiselect) {
      // Подменяем select на multiSelect с двумя списками
      let selectInput = dialog.find('.bootbox-input-select');
      let searchArgs = {};
      if (args.leftHeader) searchArgs.selectableHeader = args.leftHeader;
      if (args.leftHeaderText) searchArgs.selectableHeaderText = args.leftHeaderText;
      if (args.rightHeader) searchArgs.selectionHeader = args.rightHeader;
      if (args.rightHeaderText) searchArgs.selectionHeaderText = args.rightHeaderText;
      if (args.withSearch) searchArgs.withSearch = args.withSearch;
      initTwoSideMultiSelect(selectInput, searchArgs);
    } else if (args.withSearch || args.ajax) {
      let select2Args = {
        // Задаём родителя, чтобы окошко поиска могло получить фокус
        // (см. https://select2.org/troubleshooting/common-problems#select2-does-not-function-properly-when-i-use-it-inside-a-bootst)
        dropdownParent: dialog.find('.bootbox-body'),
        width: "100%",
        language: 'ru',
      };
      if (args.ajax) select2Args.ajax = args.ajax;
      if (args.placeholder) select2Args.placeholder = args.placeholder;
      dialog.find('.bootbox-input-select').select2(select2Args);
      dialog.on('shown.bs.modal', function() {
        dialog.find('.bootbox-input-select').trigger("change"); // Нужно обновить виджет, чтобы не обрезался placeholder
      });
    }
    if (args.selectSize) {
      dialog.find('.bootbox-input-select').attr("size", args.selectSize);
    }
  });
}

function confirmWithCallback(args) {
  let defaultArgs = {
    buttons: {
      cancel: {
        label: 'Отмена',
        className: 'btn btn-primary bootbox-accept'
      },
      confirm: {
        label: 'OK',
        className: 'btn btn-secondary m-l-5'
      },
    },
  };
  let allArgs = Object.assign({}, defaultArgs, args);
  bootbox.confirm(allArgs);
}

function confirmAndRedirect(msg, href) {
  confirmWithCallback({
    message: msg,
    callback: function(result) {
      if (result) location.href = href;
    },
  });
}

function promptWithCallback(args) {
  let defaultArgs = {
    buttons: {
      cancel: {
        label: 'Отмена',
        className: 'btn btn-primary bootbox-accept'
      },
      confirm: {
        label: 'OK',
        className: 'btn btn-secondary m-l-5'
      },
    },
  };
  let allArgs = Object.assign({}, defaultArgs, args);
  bootbox.prompt(allArgs);
}

function selectDate(args) {
  let defaultArgs = {
    title: 'Пожалуйста, выберите дату',
    inputType: 'date',
  };
  let allArgs = Object.assign({}, defaultArgs, args);
  promptWithCallback(allArgs);
}

function showWaitDialog() {
  return bootbox.dialog({
    message: '<p class="text-center mb-0"><i class="fa fa-spin fa-cog"></i> Пожалуйста, подождите...</p>',
    closeButton: false
  });
}

// Вспомогательная функция для создания multiSelect с двумя окошками,
// с сохранением порядка выбора элементов и с опцией текстового поиска.
function initTwoSideMultiSelect(selectInput, args) {
  let defaultArgs = {
    buttonWidth: '100%',
    keepOrder: true,
    afterSelect: function(value) {
      // Перемещаем выбранную опцию в конец списка, чтобы опции шли в том порядке, в котором их выбрал пользователь.
      selectInput.find(`option[value='${value}']`).appendTo(selectInput);
    },
  };
  let allArgs = Object.assign({}, defaultArgs, args);
  // Удаляем из allArgs все аргументы, которые не относятся к multiSelect
  ['withSearch', 'selectableHeaderText', 'selectionHeaderText'].forEach(e => delete allArgs[e]);
  if (args.selectableHeaderText) {
    allArgs.selectableHeader = `<div class=\'custom-header\'>${args.selectableHeaderText}</div>`;
    if (args.withSearch) {
      allArgs.selectableHeader = `${allArgs.selectableHeader}<input type='text' class='form-control' autocomplete='off' placeholder='Поиск'>`;
    }
  }
  if (args.selectionHeaderText) {
    allArgs.selectionHeader = `<div class=\'custom-header\'>${args.selectionHeaderText}</div>`;
    if (args.withSearch) {
      allArgs.selectionHeader = `${allArgs.selectionHeader}<input type='text' class='form-control' autocomplete='off' placeholder='Поиск'>`;
    }
  }
  if (args.withSearch) {
    allArgs.afterInit = function(ms) {
      let that = this,
        $selectableSearch = that.$selectableUl.prev(),
        $selectionSearch = that.$selectionUl.prev(),
        selectableSearchString = '#' + that.$container.attr('id') + ' .ms-elem-selectable:not(.ms-selected)',
        selectionSearchString = '#' + that.$container.attr('id') + ' .ms-elem-selection.ms-selected';

      that.qs1 = $selectableSearch.quicksearch(selectableSearchString)
        .on('keydown', function(e) {
          if (e.which === 40) {
            that.$selectableUl.focus();
            return false;
          }
        });
      that.qs2 = $selectionSearch.quicksearch(selectionSearchString)
        .on('keydown', function(e) {
          if (e.which === 40) {
            that.$selectionUl.focus();
            return false;
          }
        });
    };
    allArgs.afterSelect = function(value) {
      // Перемещаем выбранную опцию в конец списка, чтобы опции шли в том порядке, в котором их выбрал пользователь.
      selectInput.find(`option[value='${value}']`).appendTo(selectInput);
      this.qs1.cache();
      this.qs2.cache();
    };
    allArgs.afterDeselect = function() {
      this.qs1.cache();
      this.qs2.cache();
    };
  }
  selectInput.multiSelect(allArgs);
}
