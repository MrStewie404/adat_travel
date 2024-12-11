"use strict";

$(document).on('click', '.dropdown-toggle[data-toggle="dropdown-filter"]', function(e) {
  $(this).closest('.dropdown').toggleClass('open');
});

$(document).on('click', '.dropdown-filter-menu .js-reset, .dropdown-filter-menu button[type="submit"]', function(e) {
  $(this).closest('.dropdown').toggleClass('open');
});
