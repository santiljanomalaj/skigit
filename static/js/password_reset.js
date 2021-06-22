$j = jQuery.noConflict();

var passwordResetForm = $j("#password_reset_form");

passwordReset_validator = passwordResetForm.validate({
ignore: "", //Hidden inputs
rules: {
  'email': {
    required: {
      depends: function () {
        $j(this).val($j.trim($j(this).val()));
        return true;
      }
    },
    customemail: true
  }
},
messages: {
  'email': {
    required: "Email address is required.",
    customemail: "Please enter a valid email address."
  }
}
});

$j(function () {
  function passwordResetFormValidation() {
      return passwordResetForm.valid()
  }

  $j('#form_submit').click(function () {
    is_valid = passwordResetFormValidation();
    if (is_valid){
        var id_email = $j('#id_email').val().trim();

        $j.ajax({
          url: "/email_exits_check/", // the endpoint
          type: "POST", // http method
          data: { 'email': id_email },
          success: function(response) {
            if (response.is_success){
              $j("#password_reset_form").submit();
            } else {
              passwordReset_validator.showErrors({
                  "email": "Email address not found"
              });
            }
          }
        });
    }
    return false;
  });

});
