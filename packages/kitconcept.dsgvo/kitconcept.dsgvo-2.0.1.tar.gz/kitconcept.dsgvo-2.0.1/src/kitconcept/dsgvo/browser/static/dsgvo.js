"use strict";

// Lightweight getCookie https://gomakethings.com/working-with-cookies-in-vanilla-js/
var getCookie = function(name) {
  var value = "; " + document.cookie;
  var parts = value.split("; " + name + "=");
  if (parts.length == 2)
    return parts
      .pop()
      .split(";")
      .shift();
};

(function() {
  var $ = jQuery;
  // We rely on Plone for setting the cookie, so no heavy JS deps on JQuery cookie
  var setCookie = function() {
    $.get("@@close-dsgvo-info");
  };

  $(function() {
    $(".dsgvo-close-banner").click(function(event) {
      setCookie();
      $(".dsgvo-banner").fadeOut();
      event.preventDefault();
    });
  });
})();

$(document).ready(function() {
  if (!getCookie("hide-dsgvo-banner")) {
    $(".dsgvo-banner").show();
  }
});
