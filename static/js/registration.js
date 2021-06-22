$j = jQuery.noConflict();

var registrationForm = $j("#registration_form");

var validator = registrationForm.validate({
    ignore: "", //Hidden inputs
    rules: {
      'username': {
        required: true,
      },
      'email': {
        required: {
          depends: function () {
            $j(this).val($j.trim($j(this).val()));
            return true;
          }
        },
        customemail: true,

      },
      'password1': {
        required: {
          depends: function () {
            $j(this).val($j.trim($j(this).val()));
            return true;
          }
        },
        oneuppercaseletter: true,
        minlength: 8,
        maxlength: 16
      },
      'password2': {
        required: true,
        equalTo: "#id_password1"
      },
      'type_check': {
        required: true
      },
      'usepolicy_check': {
        required: true
      },
      'ageconfirm_check': {
        required: true
      }
    },
    messages: {
      'username': {
        required: "A username is required",
      },
      'email': {
        required: "Email address is required.",
        customemail: "Please enter a valid email address."
      },
      'password1': {
        required: "A password is required",
        minlength: "Your password must contain minimum of 8 characters with at least one upper case character",
        oneuppercaseletter: "Your password must contain minimum of 8 characters with at least one upper case character",
        maxlength: "Your password must contain a no more than 16 characters with at least one upper case character.",
      },
      'password2': {
        required: "Your password verification did not match. Please re-type your verification",
        equalTo: "Your password verification did not match. Please re-type your verification"
      },
      'type_check': {
        required: "<div class='checkbox-error-msg'><span>Please check the box to proceed</span></div>",
      },
      'usepolicy_check': {
        required: "<div class='checkbox-error-msg'><span>Please check the box to proceed</span></div>",
      },
      'ageconfirm_check': {
        required: "<div class='checkbox-error-msg'><span>Please check the box to proceed</span></div>",
      }
    }
  });

$j(function () {

    if(username_error) {
        validator.showErrors({
            "username": username_error
        })
    }

    if(email_error) {
        validator.showErrors({
            "email": email_error
        })
    }

    if(password1_error) {
        validator.showErrors({
            "password1": password1_error
        })
    }

    if(password2_error) {
        validator.showErrors({
            "password2": password2_error
        })
    }

    $j('#pass_chang_form').on('focus', ':input', function () {
        $j(this).attr('autocomplete', 'off');
    });


      $j('.form-control').on('keypress', function () {
        $j('.errorlist').empty()
        $j('.errorlist').hide()
      });

      function RegisterFormValidation() {
        return registrationForm.valid();
      }

      $j('#form_submit').click(function () {
        RegisterFormValidation();
        $j('.errorlist').show();
      });

});

function myFunction1() {
    var x = document.getElementById(password1_label_text);
    if (x.type === "password") {
        x.type = "text";
    } else {
        x.type = "password";
    }
}

function myFunction2() {
    var x = document.getElementById(password2_label_text);
    if (x.type === "password") {
        x.type = "text";
    } else {
        x.type = "password";
    }
}
