$.domReady(function() {
  if (window.location.hash == '#badserver') {
    $(".error").html("Instance password should be alphanumeric with dashes, periods and underscores");
  } else if (window.location.hash == '#badusername') {
    $(".error").html("Code name should be alphanumeric with dashes, periods and underscores");
  }

  $("input:text:visible:first").focus();

  $("#login").submit(function(e) {
    var pwd = $("#server").val();
    if (!pwd) {
      $("#step2").css('display', 'block');
      $("input#server").focus();

      e.preventDefault();
      e.stopPropagation();
    }
  });
});
