"use strict";
$(document).ready(function() {
  let tomorrow = new Date();
  tomorrow.setDate(tomorrow.getDate() + 1);

  let $validDatesContainer = $('#id_valid_dates_info');
  let validDatesInfo = JSON.parse($validDatesContainer.text());

  let $form = $('form');
  let $btnSubmit = $form.find('button[type="submit"]');
  let $touristsCountInput = $('#id_tourists_count');
  let $tripDateInput = $('#id_trip_date');
  let $agreeWithPoliciesInput = $('#id_agree_with_policies');
  let $departurePointInput = $('#id_departure_point');
  let $initiallyHiddenPart = $form.find('#id_form_part2');

  $departurePointInput.select2({
    theme: 'bootstrap4',
    language: 'ru',
    templateResult: departurePointTemplateResult,
  });

  updateCalendar();
  updateFormContent(false);

  $touristsCountInput.change(function() {
    updateCalendar();
    updateFormContent(true);
  });

  $tripDateInput.change(function() {
    updateFormContent(true);
  }).on('on-date-selected', function() {
    updateFormContent(true);
  });

  $agreeWithPoliciesInput.change(function() {
    updateSubmitButton();
  });

  function updateFormContent(recalcCommission) {
    let touristsCount = +$touristsCountInput.val();
    let dateParts = $tripDateInput.val().split('.');
    if (dateParts.length < 3 || !touristsCount || touristsCount < 1) {
      $initiallyHiddenPart.attr('hidden', '');
      $('.trip-details').attr('hidden', '');
      $btnSubmit.find('#id_submit_details').text('');
      updateSubmitButton();
      return;
    }

    let d = dateParts[0];
    let m = dateParts[1];
    let y = dateParts[2];
    let tripInfoUrl = `${$form.attr('data-get-trip-info-url')}?y=${y}&m=${m}&d=${d}&count=${touristsCount}`;

    simpleGetRequest({
      url: tripInfoUrl,
      success: function(response) {
        onTripDataReceived(response, recalcCommission);
      },
      error: function(response) {
        console.log(response);
        showFadeOutMessage("Произошла ошибка. Попробуйте перезагрузить страницу, пожалуйста.");
      }
    });
  }

  function onTripDataReceived(tripInfoDict, recalcCommission) {
    $('#id_free_seats_count').text(tripInfoDict['free_seats_count']);
    $('#id_price_per_tourist').text(tripInfoDict['price_per_tourist_str']);
    $('#id_prepayment_per_tourist').text(tripInfoDict['prepayment_per_tourist_str']);
    $('#id_price_total').text(tripInfoDict['total_price_str']);
    let totalPrepaymentStr = tripInfoDict['total_prepayment_str'];
    $('#id_prepayment_total').text(totalPrepaymentStr);
    $btnSubmit.find('#id_submit_text').text(totalPrepaymentStr ? "Перейти к оплате" : "Оформить");
    $btnSubmit.find('#id_submit_details').text(totalPrepaymentStr ? `(${totalPrepaymentStr})` : "");

    $initiallyHiddenPart.removeAttr('hidden');
    $('.trip-details').removeAttr('hidden');
    updateSubmitButton()

    let commission = tripInfoDict['commission'];
    let $commissionInput = $('#id_supplier_commission');
    if (recalcCommission && commission > 0 && $commissionInput.length > 0) {
      $commissionInput.val(commission);
      showFadeOutMessage("Комиссия была автоматически пересчитана.");
    }

    let departurePointPks = tripInfoDict['departure_point_pks'];
    let $departurePointRow = $('#id_departure_point_row');
    if (departurePointPks.length === 0) {
      $departurePointRow.attr('hidden', '');
    } else {
      $departurePointRow.removeAttr('hidden');
      $departurePointInput.find('option').each(function() {
        let $option = $(this);
        let v = $option.val();
        let pk = v ? parseInt(v, 10) : null;
        if (pk === null || departurePointPks.includes(pk)) {
          $option.removeAttr('disabled');
          $option.removeClass('hidden-option');
          //if (departurePointPks.length === 1 && pk != null) $option.attr('selected', '');
        } else {
          $option.attr('disabled', '');
          $option.addClass('hidden-option');
          $option.removeAttr('selected');
        }
      });

      // if (departurePointPks.length === 1) {
      //   $departurePointInput.val(departurePointPks[0].toString());
      // }
    }
  }

  function updateSubmitButton() {
    let enabled = $initiallyHiddenPart.not('[hidden]').length > 0 &&
      ($agreeWithPoliciesInput.length === 0 || $agreeWithPoliciesInput.prop('checked'));
    if (enabled) $btnSubmit.removeAttr('disabled');
    else $btnSubmit.attr('disabled', '');
  }

  function updateCalendar() {
    let touristsCount = $touristsCountInput.val();
    let picker = initDateRangePicker('#id_trip_date', {
      minDate: tomorrow,
      isInvalidDate: function(input) {
        let date = input.format('DD.MM.YYYY');
        let validDates = validDatesInfo.filter(function(x) {
          return x['free_seats'] >= touristsCount;
        }).map(function(x) {
          return x['date_str'];
        });
        return !validDates.includes(date);
      }
    }, null);
    picker.on('show.daterangepicker', function(ev, picker) {
      picker.container.addClass('datepicker-with-disabled-dates');
    });
  }

  function departurePointTemplateResult(data, container) {
    if (data.element) {
      $(container).addClass($(data.element).attr("class"));
    }
    return data.text;
  }

});
