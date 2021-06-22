$j = jQuery.noConflict()
$j(document).ready(function () {

  var img1 = new Image();
  var img2 = new Image();
  var myMessages = ['info', 'warning', 'error', 'success']; // define the messages types
  var DELETE_ICON = '/static/skigit/wp-content/themes/detube/images/deleteIcon.png';
  var RIGHT_ICON = '/static/skigit/wp-content/themes/detube/images/success_icon.png';
  var DELETE_ICON_IMG = '<img width="17" height="17" src="' + DELETE_ICON + '">';
  var RIGHT_ICON_IMG = '<img width="17" height="17" src="' + RIGHT_ICON + '">';
  var BASE_URL = '/';


  function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
      var cookies = document.cookie.split(';');
      for (var i = 0; i < cookies.length; i++) {
        var cookie = $j.trim(cookies[i]);
        // Does this cookie string begin with the name we want?
        if (cookie.substring(0, name.length + 1) === (name + '=')) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }

  function is_empty(str) {
    return !str || !/[^\s]+/.test(str);
  }

  function rem_msg() {
    $j(".notify_msg_div").html('');
  }

  function set_msg(tag, msg) {
    msg_string = '<div style="display:none;"  class="' + tag + ' message"><h3>' + msg + '</h3></div>';
    $j(".notify_msg_div").append(msg_string);
  }

  function show_msg() {
    hideAllMessages();
    to = 0;
    for (var i = 0; i < myMessages.length; i++) {
      if ($j('.' + myMessages[i]).length > 0) {
        $j('.' + myMessages[i]).show();
        $j('.' + myMessages[i]).animate({top: to}, 1200);
        to += $j('.' + myMessages[i]).outerHeight();
      }
      showMessage(myMessages[i]);
    }

    // When message is clicked, hide it
    $j('.message').click(function () {
      $j(this).animate({top: -$j(this).outerHeight()}, 500);
    });
    setTimeout(function () {
      hidemsg();
    }, 12000)
  }

  function hidemsg() {
    to = 0;
    for (var i = 0; i < myMessages.length; i++) {
      if ($j('.' + myMessages[i]).length > 0) {
        to += $j('.' + myMessages[i]).outerHeight();
        $j('.' + myMessages[i]).animate({top: -to}, 1200);
      }
      showMessage(myMessages[i]);
    }
  }

  function hideAllMessages() {
    var messagesHeights = []; // this array will store height for each
    for (var i = 0; i < myMessages.length; i++) {
      messagesHeights[i] = $j('.' + myMessages[i]).outerHeight();
      $j('.' + myMessages[i]).css('top', '-' + messagesHeights[i]); //move element outside viewport
    }
  }

  function showMessage(type) {
    $j('.' + type + '-trigger').click(function () {
      hideAllMessages();
      $j('.' + type).animate({top: "0"}, 500);
    });
  }

  function logo_imgURL(input) {
    if (input.files && input.files[0]) {
      var reader = new FileReader();
      reader.onload = function (e) {
        $j('#logo_img')
            .attr('src', e.target.result);
      };
      reader.readAsDataURL(input.files[0]);
    }
  }

  function profile_imgURL(input) {
    if (input.files && input.files[0]) {
      var reader = new FileReader();
      reader.onload = function (e) {
        $j('#user_profile_image')
            .attr('src', e.target.result);
      };
      reader.readAsDataURL(input.files[0]);
    }
  }

  function password_reset_email_check() {

    var id_email = $j('#id_email').val().trim();
    var is_error = false
    //var is_success = false
    var msg = "Please Wait..";

    if (id_email && !is_empty(id_email)) {
      $j.ajax({
        url: "/email_exits_check/", // the endpoint
        type: "POST", // http method
        data: {'email': id_email}, // data sent with the delete request
        success: function (response) {
          if (response) {
            if (response.is_success) {
              is_error = false;
              msg = response.message;
            }
            else {
              is_error = true;
              msg = response.message;
            }
          }
          else {
            is_error = true;
            msg = "<span style='font-size:20px;'><i class='glyphicon glyphicon-remove-circle' style='top: 5px !important;' /></span> Oops! Server encountered an error.";
          }
        },
        error: function (xhr, errmsg, err) {
          is_error = true;
          msg = "<span style='font-size:20px;'><i class='glyphicon glyphicon-remove-circle' style='top: 5px !important;' /></span> Oops! We have encountered an error." + xhr.status + ": " + xhr.responseText;
        }
      });
    }
    else {
      is_error = true
      msg = "<span style='font-size:20px;'><i class='glyphicon glyphicon-remove-circle' style='top: 5px !important;' /></span> Please Enter The Valid Email Address"
    }

    setTimeout(function () {
      if (is_error) {
        $j("#password_reset_error").html("<p class='error_msg'>" + msg + "</p>");
        return is_error
      }
      else {
        $j("#password_reset_error").html("<p class='success_msg'>" + msg + "</p>");
        return is_error
      }
    }, 800);
  }

  var forceSubmitForm = false;

  $j("img.img2").hide();
  show_msg();
  $j("#header .navbar-nav li a").hover(function () {
    var $jimg1 = $j(this).children('.img1');
    var $jimg2 = $j(this).children('.img2');
    if ($jimg1 && $jimg1.length === 1 && $jimg2 && $jimg2.length === 1) {
      img1.src = $jimg1.attr('src');
      img2.src = $jimg2.attr('src');
      $jimg2.attr('src', img1.src);
      $jimg1.attr('src', img2.src);
    }
  }, function () {
    var $jimg1 = $j(this).children('.img2');
    var $jimg2 = $j(this).children('.img1');
    if ($jimg1 && $jimg1.length === 1 && $jimg2 && $jimg2.length === 1) {
      img1.src = $jimg1.attr('src');
      img2.src = $jimg2.attr('src');
      $jimg2.attr('src', img1.src);
      $jimg1.attr('src', img2.src);
    }
  });
  $j('.dropdown-menu').click(function (event) {
    event.stopPropagation();
  });
  $j.ajaxSetup({
    beforeSend: function (xhr, settings) {
      if (!(/^http:.*/.test(settings.url) || /^https:.*/.test(settings.url))) {
        xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
      }
    }
  });

  // $j("form#form_login").submit(function (e) {
  //   e.preventDefault()
  //   $j("#chat_msg_submit").attr('disabled', 'disabled');
  //   var form_data = $j(this).serialize();
  //   var user_login = $j('#user_login').val().trim();
  //   var user_pass = $j("#user_pass").val().trim();
  //   var is_error = false
  //   var is_success = false
  //   var $jsubmit = $j("form#form_login").children().find("input[type='submit']");
  //   $jsubmit.attr('disabled', 'disabled');
  //   var msg = "";
  //   if (user_login && !is_empty(user_login.trim())) {
  //     if (user_pass && !is_empty(user_pass.trim())) {
  //       $j.ajax({
  //         url: "/login_ajax/", // the endpoint
  //         type: "POST", // http method
  //         data: form_data, // data sent with the delete request
  //         success: function (response) {
  //           // hide the post
  //           if (response) {
  //             if (response.is_success) {
  //               is_success = true
  //               msg = response.message
  //               setTimeout(function () {
  //                 window.location = response.base_location;
  //               }, 500);
  //             }//message send
  //             else {
  //               is_success = false
  //               msg = response.message
  //             }
  //           }
  //           else {
  //             is_success = false
  //             msg = "<span style='font-size:20px;'><i class='glyphicon glyphicon-remove-circle' style='top: 5px !important;' /></span> Oops! Server encountered an error.";
  //           }
  //           if (is_success) {
  //             $j("#login_ingo_msg").html('<p class="success_msg" >' + msg + '</p>');
  //           }
  //           else {
  //             $j("#login_ingo_msg").html('<p class="error_msg" >' + msg + '</p>');
  //           }
  //           setTimeout(function () {
  //             $j("#login_ingo_msg > * ").fadeOut('slow');
  //             $j("#login_ingo_msg").empty();
  //           }, 6000);
  //           $jsubmit.removeAttr('disabled');
  //         },
  //         error: function (xhr, errmsg, err) {
  //           // Show an error
  //           is_error = true;
  //           msg = "<span style='font-size:20px;'><i class='glyphicon glyphicon-remove-circle' style='top: 5px !important;' /></span> Oops! We have encountered an error." + xhr.status + ": " + xhr.responseText;
  //           $j("#smallModal").hide();
  //           $jsubmit.removeAttr('disabled');
  //           if (is_error) {
  //             rem_msg();
  //             set_msg('error', msg);
  //             show_msg();
  //           }
  //         }
  //       });
  //     }
  //     else {
  //       is_error = true;
  //       msg = "<span class='sign-error'><i class='glyphicon glyphicon-remove-circle' /></span><span class='text-error'>Your username and/or password are incorrect. Please try again.</span>";
  //     }
  //   }
  //   else {
  //     is_error = true;
  //     msg = "<span class='sign-error'><i class='glyphicon glyphicon-remove-circle' /></span><span class='text-error'>Your username and/or password are incorrect. Please try again.</span>";
  //   }
  //
  //   if (is_error) {
  //     $j("#login_ingo_msg").html('<p class="error_msg" >' + msg + '</p>');
  //   }
  //
  //   setTimeout(function () {
  //     $j("#login_ingo_msg > * ").fadeOut('slow');
  //     $j("#login_ingo_msg").empty();
  //   }, 5000);
  //   $jsubmit.removeAttr('disabled');
  // });
  $j('.img-zoom').hover(function () {
    $j(this).addClass('transition');
  }, function () {
    $j(this).removeClass('transition');
  });

  if ($j("#id_logo_img").length === 1) {
    $j("#id_logo_img").attr("onchange", "logo_imgURL(this);");
  }
  if ($j("#id_profile_img").length === 1) {
    $j("#id_profile_img").attr("onchange", "profile_imgURL(this);");
  }

  $j("#password_reset_form").submit(function () {

    if (forceSubmitForm) return true;
    var id_email = $j('#id_email').val().trim();
    var is_error = false;
    var msg = "Please Wait..";

    if (id_email && !is_empty(id_email)) {
      $j.ajax({
        url: "/email_exits_check/", // the endpoint
        type: "POST", // http method
        data: {'email': id_email}, // data sent with the delete request
        success: function (response) {
          // hide the post
          if (response) {
            if (response.is_success) {
              forceSubmitForm = true;
              is_error = false;
              msg = response.message;
            }//message send
            else {
              is_error = true;
              msg = response.message;
            }
          }
          else {
            is_error = true;
            msg = "Oops! Server encountered an error.";
          }
          if (is_error) {
            $j("#password_reset_error").html("<p class='error_msg'>" + msg + "</p>");
            return false;
          }
          else {
            $j("#password_reset_error").html("<p class='success_msg'>" + msg + "</p>");
            $j("#password_reset_form").submit();
          }
        },
        error: function (xhr, errmsg, err) {
          // Show an error
          is_error = true;
          msg = "Oops! We have encountered an error." + xhr.status + ": " + xhr.responseText;
        }
      });
    }
    else {
      is_error = true
      msg = "<span style='font-size:20px;'><i class='glyphicon glyphicon-remove-circle' style='top: 5px !important;' /></span> Please Enter The Valid Email Address"
    }

    if (is_error) {
      $j("#password_reset_error").html("<p class='error_msg'>" + msg + "</p>");
    }
    return false;
  });

  viewCount = function (video_id) {
    var skigit_id = video_id
    $j.ajax({
      url: "/view_count_update/",
      type: "POST",
      data: {
        'skigit_id': skigit_id, csrfmiddlewaretoken: getCookie('csrftoken')
      },
      success: function (response) {
        if (response.is_success) {
          $j('#view_count' + skigit_id).text(parseInt(response.view_count))
        }
      }
    });
  }

  $j('#user_action #general_notify').click(function () {
    $j.post("/notification/get/",
        {},
        function (data, status) {
          if (data.is_success) {
            msg = data.message;
            $j('#gen_notification').fadeToggle('slow').html(msg);
          }
        });
  });

  $j('.dropdown').hover(function () {
        $j(this).addClass('show');
        $j(this).children('.dropdown-menu').addClass('show');
      },
      function () {
        $j(this).removeClass('show');
        $j(this).children('.dropdown-menu').removeClass('show');
      });

  $j('.image-business').hover(function () {
    var vid = $j(this).data('vid');
    var id = '#business_enlarge' + vid;
    $j(id).fadeIn();
  }, function () {
    var vid = $j(this).data('vid');
    var id = '#business_enlarge' + vid;
    $j(id).fadeOut();
  });


  $j("#friendPopover").popover({
    html: true,
    title: "Friends and Invite Notifications",
    placement: "bottom",
    content: $j("#friendContent").html(),
  });

  $j('body').mouseup(function (e) {
    $j('[data-original-title]').each(function () {
      //the 'is' for buttons that trigger popups
      //the 'has' for icons within a button that triggers a popup

      if (!$j(this).is(e.target) && $j(this).has(e.target).length === 0 &&
          $j('.popover').has(e.target).length === 0) {
        var popoverElement = $j(this).data('bs.popover').tip();
        var popoverWasVisible = popoverElement.is(':visible');

        if (popoverWasVisible) {
          $j(this).popover('hide');
          $j(this).click();
        }
      }
    });

    shareClose = function (video_id) {

      $j('[data-original-title]').each(function (e) {
        //the 'is' for buttons that trigger popups
        //the 'has' for icons within a button that triggers a popup
        if (!$j(this).is(e.target) && $j(this).has(e.target).length === 0 && $j('.popover').has(e.target).length === 0) {
          var popoverElement = $j(this).data('bs.popover').tip();
          var popoverWasVisible = popoverElement.is(':visible');

          if (popoverWasVisible) {
            $j("#share_overlay" + video_id).removeClass("popupdisplay");
            $j(".overlayview").css("display", "none");
            $j(".skigit_play img").css("display", "block")
            $j(this).popover('hide');
            $j(this).click();
          }
        }
      });
    }

    logoclick = function (logo_id, url) {
      var message;
      $j.ajax({
        url: "/invoice/business-logo/",
        type: "POST",
        data: {'logo_id': logo_id},
        success: function (data) {
          if (data.is_success) {
            window.location.href = url
          }
          else {
            message = data.message;
          }
        }
      });
    }

    plugInClick = function (skigit_id, url) {
      var message;
      $j.ajax({
        url: "/invoice/plugin-click/",
        type: "POST",
        data: {'skigit_id': skigit_id},
        success: function (data) {
          if (data.is_success) {
            window.location.href = url
          }
          else {
            message = data.message;
          }
        }
      });
    }

    $j("#generalNPopover").popover({
      html: true,
      title: "Skigit Notifications",
      placement: "bottom",
      content: $j('#notifyContaint').html(),
    });

    $j('#bug_report').on("click", function () {
      $j('#bugModal').modal('show');
    });

    $j('#id_bug_submit').click(function () {

      if ($j('#bug_description').val() != '' && $j("input[type='radio'][name=repeat]:checked").val() != undefined) {
        var data = {
          'skigit_id': $j('#id_bug_skigit').val(),
          'skigit_title': $j('#id_bug_skigit_title').val(),
          'bug_url': $j('#id_bug_page_url').val(),
          'bug_title': $j('#id_bug_title').val(),
          'bug_desc': $j('#bug_description').val(),
          'bug_repeated': $j("input[type='radio'][name=repeat]:checked").val()
        }
        $j('#id_bug_submit').attr("disabled", "disabled");
        $j('#id_bug_close').attr("disabled", "disabled");
        $j("#bug_msg").html('Please Wait...').css('color', 'orange');
        $j.ajax({
          url: "/bug-management/",
          type: "POST",
          data: data,
          success: function (responce_data) {
            $j('#bug_report_form')[0].reset()
            $j("#bug_msg").html(responce_data.message).css('color', 'green');
            $j('#id_bug_submit').removeAttr('disabled');
            $j('#id_bug_close').removeAttr('disabled');
          }
        });
      }
      else {
        $j('#id_bug_submit').removeAttr('disabled');
        $j('#id_bug_close').removeAttr('disabled');
        if (($j("input[type='radio'][name=repeat]:checked").val() == '' ||
            $j("input[type='radio'][name=repeat]:checked").val() == undefined ) && $j('#bug_description').val() == '') {
          $j("#bug_msg").html("<span style='font-size:19px;'><i class='glyphicon glyphicon-remove-circle' style='top: 5px !important;' /></span><span style='font-size:13px;'> Please enter a bug description and select an option</span>").css('color', 'red');
        }
        else if ($j("#bug_description").val() == '') {
          $j("#bug_msg").html("<span style='font-size:19px;'><i class='glyphicon glyphicon-remove-circle' style='top: 5px !important;' /></span><span style='font-size:13px;'> Please enter a bug description</span>").css('color', 'red');
        }
        else if (($j("input[type='radio'][name=repeat]:checked").val() == '' ||
            $j("input[type='radio'][name=repeat]:checked").val() == undefined )) {
          $j("#bug_msg").html("<span style='font-size:19px;'><i class='glyphicon glyphicon-remove-circle' style='top: 5px !important;' /></span><span style='font-size:13px;'> Please select an option</span>").css('color', 'red');
        }
        else {
          $j("#bug_msg").html("<span style='font-size:19px;'><i class='glyphicon glyphicon-remove-circle' style='top: 5px !important;' /></span><span style='font-size:13px;'> Please select an option</span>").css('color', 'red');
        }
      }

      setTimeout(function () {
        $j("#bug_msg > * ").fadeOut('slow');
        $j("#bug_msg").empty();
      }, 5000);
    });

    bugSubmit = function (skigit) {
      if ($j.trim($j('#id_bug_description' + skigit).val()).length > 0 &&
          $j("input[type='radio'][name=repeat]:checked").val() != undefined) {
        var data = {
          'skigit_id': $j('#id_bug_skigit').val(),
          'bug_url': window.location.origin + '/?id=' + $j('#id_bug_skigit').val(),
          'bug_title': $j('#id_bug_title').val(),
          'bug_desc': $j('#id_bug_description' + skigit).val(),
          'bug_repeated': $j("input[type='radio'][name=repeat]:checked").val()
        }
        $j('#id_bug_submit1').attr("disabled", "disabled");
        $j('#inapp_form_can').attr("disabled", "disabled");
        $j("#bug_msg" + skigit).html('Please Wait...').css('color', 'orange');
        $j.ajax({
          url: "/bug-management/",
          type: "POST",
          data: data,
          success: function (responce_data) {
            if (responce_data.is_success) {
              $j('#bug_report_form' + skigit)[0].reset()
              $j("#bug_msg" + skigit).empty()
              /* $j('.msg_success').html('Thanks for making Skigit better!')
               $j('#id_bug_submit1').removeAttr('disabled')
               $j('#inapp_form_can').removeAttr('disabled')
               $j(".dropdown").removeClass('open');
               $j('.msg_success').show()
               setTimeout(openPopup, 2500);*/

              $j('#id_bug_submit1').removeAttr('disabled')
              $j('#inapp_form_can').removeAttr('disabled')
              $j("#bug_msg" + skigit).html("<span class='sign-error' style='padding: 0 !important;'><i class='glyphicon glyphicon-ok-circle ok-pos'/></span><span class='text-error' style='padding: 0 !important; margin-top: 4px;'> Thanks for making Skigit better!</span>").css('color', 'green');
              setTimeout(function () {
                $j('#id_bug_submit1').removeAttr('disabled');
                $j('#inapp_form_can').removeAttr('disabled');
                $j('#bug_report_form' + skigit)[0].reset()
                $j("#bug_msg" + skigit).empty()
                $j('.dropdown').removeClass('open');
              }, 2500);
            }
          }
        });
      }
      else {
        $j('#id_bug_submit1').removeAttr('disabled');
        $j('#inapp_form_can').removeAttr('disabled');
        if ($j.trim($j('#id_bug_description' + skigit).val()).length <= 0) {
          $j("#bug_msg" + skigit).html("<span class='sign-error' style='padding: 0 !important;'><i class='glyphicon glyphicon-remove-circle cross-pos'/></span><span class='text-error' style='padding: 0 !important; margin-top: 4px;'> Please enter a bug description and select an option</span>").css('color', 'red');
        }
        else {
          $j("#bug_msg" + skigit).html("<span class='sign-error' style='padding: 0 !important;'><i class='glyphicon glyphicon-remove-circle cross-pos'/></span><span class='text-error' style='padding: 0 !important; margin-top: 4px;'> Please select an option</span>").css('color', 'red');
        }
        setTimeout(function () {
          $j('#id_bug_submit1').removeAttr('disabled');
          $j('#inapp_form_can').removeAttr('disabled');
          //$j('#bug_report_form'+skigit)[0].reset()
          $j("#bug_msg" + skigit).empty()
        }, 2000);
      }
    }

    bugCancel = function (skigit) {
      $j(".dropdown").removeClass('open');
      $j('#id_bug_submit1').removeAttr('disabled');
      $j('#inapp_form_can').removeAttr('disabled');
      $j('#bug_report_form' + skigit)[0].reset()
      $j("#bug_msg" + skigit).empty()
    }

    flagSubmit = function (skigit) {
      input_tag = $j("input:radio[name=skigit_reasons]:checked")
      skigit_reasons = input_tag.attr("skigit_reasons")
      skigit_id = input_tag.attr("skigit_id")
      data = $j("#inapp_form").serialize()

      if ($j("input[name='skigit_reasons']:checked").val()) {
        $j('#flag_msg' + skigit).empty()
        $j('#flag_msg' + skigit).html('Please Wait').css('color', 'orange');
        $j('#inapp_form_sub').attr("disabled", "disabled");
        $j('#inapp_flag_can').attr("disabled", "disabled");
        $j.post("/skigit_inapp_reason/", {
          skigit_reasons: skigit_reasons,
          skigit_id: skigit_id
        }, function (data, status) {
          if (data.is_success) {
            /*$j('#inapp_form'+skigit)[0].reset()
             $j(".dropdown").removeClass('open');
             $j('#inapp_form_sub').removeAttr('disabled');
             $j('#inapp_flag_can').removeAttr('disabled');
             $j('#flag_msg'+skigit).empty()
             $j('.msg_success').html("<span class='sign1-error'><i class='glyphicon glyphicon-ok-circle ok1-pos'/></span><span class='text1-error'> Your request will be reviewed!</span>").css('color','green');
             $j('.msg_success').show()
             setTimeout(openPopup, 2500);*/

            $j('#inapp_form_sub').removeAttr('disabled')
            $j('#inapp_flag_can').removeAttr('disabled')
            $j('#flag_msg' + skigit).empty()
            $j('#flag_msg' + skigit).html("<span class='sign1-error'><i class='glyphicon glyphicon-ok-circle ok1-pos'/></span><span class='text1-error'> Your request will be reviewed!</span>").css('color', 'green');

            setTimeout(function () {
              $j('#inapp_form' + skigit)[0].reset()
              $j("#flag_msg" + skigit).empty()
              $j('.dropdown').removeClass('open');
            }, 2000);
          }
          else {
            $j('#inapp_form_sub').removeAttr('disabled')
            $j('#inapp_flag_can').removeAttr('disabled')
            $j('#flag_msg' + skigit).empty()
          }
        });
      }
      else {
        $j('#inapp_form_sub').removeAttr('disabled')
        $j('#inapp_flag_can').removeAttr('disabled')
        $j('#flag_msg' + skigit).empty()
        $j('#flag_msg' + skigit).html("<span class='sign1-error'><i class='glyphicon glyphicon-remove-circle cross1-pos'/></span><span class='text1-error'> Please mark appropriate reason.</span>").css('color', 'red');

        setTimeout(function () {
          $j('#inapp_form' + skigit)[0].reset()
          $j("#flag_msg" + skigit).empty()
        }, 2000);
      }
    }


    flagCancel = function (skigit) {
      $j(".dropdown").removeClass('open');
      $j('#inapp_form' + skigit)[0].reset()
      $j("#flag_msg" + skigit).empty()
    }

    $j('#bug_description').on('keydown', function () {
      $j("#bug_msg").empty();
    });

    $j('#id_bug_close').click(function () {
      $j('#bug_report_form')[0].reset()
    });

    $j('#bugModal').on('hidden.bs.modal', function () {
      $j('#bug_report_form')[0].reset()
    });

    openMessage = function () {
      $j('#smallModal').css('top', '35')
      $j('.modal').css('top', '35')
      $j('.modal-content').css('border', 'none')
      $j('.notify_msg_div').append("<div style='top: 0px; z-index:99999;'  class='info message f_type'>" +
          "<h3 style='font-family:segoe_print !important;'>" +
          "You must be a Skigit member to access this feature. <a href='#' style='color:#fff !important; text-decoration:underline !important' data-target='#smallModal' data-toggle='modal' >Join Today!</a></h3></div>")
      $j('.notify_msg_div').find('div').css('top', '0 !important;')
      setTimeout(function () {
        $j('.notify_msg_div').find('div').animate({'top': "-=52px"}, 1200);
      }, 5000);
    }

    get_date = function (video_id) {
      var currentTimezone = jstz.determine();
      var timezone = currentTimezone.name();
      $j.ajax({
        url: "/friends/share-skigit-date/",
        type: "POST",
        data: {
          'video_id': video_id, 'time_zone': timezone,
          csrfmiddlewaretoken: '{{ csrf_token }}'
        },
        success: function (result) {
          if (result.is_success) {
            for (var i = 0; i < (result.share_data).length; i++) {
              $j('#id_date_label' + video_id + result.share_data[i]['id']).text(result.share_data[i]['share_date'])
            }
          }
        }
      });
    }

    function acceptFrNotofication(user_id) {
      var user = user_id
      $j.ajax({
        url: "/friends/friends-request-approve/",
        type: "POST",
        data: {
          'to_user': user_id,
          csrfmiddlewaretoken: '{{ csrf_token }}'
        },
        success: function (data) {
          $j('#friend_li' + user).remove()
          if (data.result) {
            $j('#friend_li' + user).remove()
            $j('li').find('#friend_li' + user).remove()
            $j('#id_internal_friens' + user).attr('style', 'color:gray; font-size:large');
            $j('button[id^="id_invite_btn' + user + '"]').attr('disabled', true, 'title', 'Friend Request Accepted');

            var friend_box = '<div class="box_friend" data-skigt="' + user_id + '"><div class="box_imgcontain">' +
                '<div class="name_friend"><span class="heade_friend">' + data.username + '</span>' +
                '<span class="sub_namefriend">' + data.name + '</span><span class="friend_followers">' +
                'Followers :&nbsp;' + data.count + '</span></div><a href="/profile/' + data.username + '"><div class="img_friend">' +
                '<img alt="skigit" src="' + data.image + '"></div></a><div class="icon_friend">' +
                '<a onclick="un_follow_follow(' + user_id + ')" id="follow_' + user_id + '"class = "unfollow"' +
                'data-cuid = "' + user_id + '" title = "Follow" style = "color: #58D68D; font-weight: 400;">' +
                '<span class="box_footer" id ="follow_btn' + user_id + '" style = "color: #58D68D; font-weight: 400;"> Follow </span></a>' +
                '<img width="20" height="20" src="/static/skigit/images/new_icons/close(32x32).png" onclick="removeFriend(' + user_id + ')" class="close-friend"></div></div></div>'

            $j('#friendcontent').append(friend_box)

            if ($j('#friend_badge').text() > 1) {

              $j('#friend_badge').html($j('#friend_badge').text() - 1)

            }
            else {
              $j('#friend_badge').hide()
              var li = '<li class="f_type" style="color:#bbb9b9; font-size: smaller; text-align: center;">There is no pending Notifications.</li>'
              $j('#frnd_notification').append(li)
            }
          }
        }
      });
    }

    function rejectFrNotofication(user_id) {
      $j.ajax({
        url: "/friends/friends-request-rejected/",
        type: "POST",
        data: {
          'to_user': user_id,
          csrfmiddlewaretoken: '{{ csrf_token }}'
        },
        success: function (data) {
          if (data.result) {
            $j('#friend_li' + user_id).remove()
            $j('li').find('#friend_li' + user_id).remove()
            $j('button[id^="id_accept_btn' + user_id + '"]').remove()
            $j('button[id^="id_declain_btn' + user_id + '"]').remove()
            var html = '<button id="id_invite_btn' + user_id + '" style="float:right" onclick="inviteFriends(' + user_id + ')"><span style="font-size:large;" title="invite" id="id_internal_friens' + user_id + '" class="glyphicon glyphicon-user">&#43;</span></button>'
            $j('#button_sapn' + user_id).html(html)

            if ($j('#friend_badge').text() > 1) {
              $j('#friend_badge').html($j('#friend_badge').text() - 1)
            }
            else {
              $j('#friend_badge').hide()
              var li = '<li class="f_type" style="color:#bbb9b9; font-size: smaller; text-align: center;">There is no pending Notifications.</li>'
              $j('#frnd_notification').append(li)
            }
          }

        }
      });
    }

    notificationCount = function () {
      $j.ajax({
        url: "/friends/friend-count-notification/",
        type: "GET",
        success: function (data) {
          if (data.result) {
            if (data.count > 0) {
              $j('#friend_badge').show()
              $j('#friend_badge').html(data.count)
            }
            else {
              $j('#friend_badge').hide()
            }
          }
        }
      });
    }

    rmNotify = function (msg_typ, to_user, from_user, skigit_id) {

      $j.ajax({
        url: "/friends/notification-delete/",
        type: "POST",
        data: {
          'msg_type': msg_typ, 'to_user': to_user, 'from_user': from_user, 'skigit_id': skigit_id,
          csrfmiddlewaretoken: '{{ csrf_token }}'
        },
        success: function (data) {

          if (data.is_success) {
            $j('#notify_li_' + msg_typ + '_' + to_user + '_' + from_user + '_' + skigit_id).slideUp('slow')
          }
        }
      })
    }

    get_notify = function () {
      var currentTimezone = jstz.determine();
      var timezone = currentTimezone.name();
      $j.ajax({
        url: "/friends/notification-ski/",
        type: "POST",
        data: {'time_zone': timezone, csrfmiddlewaretoken: '{{ csrf_token }}'},
        success: function (data) {

          if (data.is_success) {
            if (data.notify_list.length > 0) {
              $j('#notify_ul').empty()
              for (var n = 0; n < data.notify_list.length; n++) {
                var li = ''

                if (data.notify_list[n].msg_type == 'like') {

                  $j('#nf_loader').show()

                  li += '<li  class="list-group-item f_type notifylist_li comefromtop" style="border:none !important;" id="notify_li_' + data.notify_list[n].msg_type + '_' + data.notify_list[n].user + '_' + data.notify_list[n].from_user + '_' + data.notify_list[n].skigit_id + '" >'
                  li += '<p class="content_notificationheaderfont"><img src="/static/images/notify_like.png" style="margin-top:15px;margin-right:4px;"> Congratulations!</p>'
                  li += '<div class="content_notificationnewpost"> <a href="{{ request.scheme }}://{{ request.META.HTTP_HOST }}/profile/'
                  li += data.notify_list[n].from_username
                  li += '" target="_blank" style="color:#0386b4">'
                  li += data.notify_list[n].from_username
                  li += '</a>'
                  li += ' likes your skigit</label> '
                  li += ' <p class="f_type" style="color:#0386b4"> '
                  li += '<a style="color:#0386b4" target="_blank" href="{{ request.scheme }}://{{ request.META.HTTP_HOST }}/?id=' + data.notify_list[n].play_back_id + '">'
                  li += data.notify_list[n].vid_title
                  li += '</a></p></div>'
                  li += '<span class="notify_date" style="float:right; margin-top: -60;">'
                  li += data.notify_list[n].date
                  li += '<img src="/static/images/close(32x32).png" class="notify_remove" onclick="rmNotify(\'' + data.notify_list[n].msg_type + '\',' + data.notify_list[n].user + ',' + data.notify_list[n].from_user + ',' + data.notify_list[n].skigit_id + ')"  width="20" height="20">'
                  li += '</span>'
                  li += '</li>'

                }
                else if (data.notify_list[n].msg_type == 'plug') {

                  $j('#nf_loader').show()

                  li += '<li  class="list-group-item f_type notifylist_li comefromtop" style="border:none !important;" id="notify_li_' + data.notify_list[n].msg_type + '_' + data.notify_list[n].user + '_' + data.notify_list[n].from_user + '_' + data.notify_list[n].skigit_id + '" >'
                  li += '<p class="content_notificationheaderfont"><img src="/static/images/notify_plugin.png" style="margin-top:15px;margin-right:4px;" /> Congratulations!</p>'
                  li += '<div class="content_notificationnewpost"><a href="{{ request.scheme }}://{{ request.META.HTTP_HOST }}/profile/'
                  li += data.notify_list[n].from_username
                  li += '" target="_blank" style="color:#0386b4 ">'
                  li += data.notify_list[n].from_username
                  li += '</a>'
                  li += ' has plugged into your skigit '
                  li += ' <p class="f_type" style="color:#0386b4"> '
                  li += '<a style="color:#0386b4" target="_blank" href="{{ request.scheme }}://{{ request.META.HTTP_HOST }}/?id=' + data.notify_list[n].play_back_id + '">'
                  li += data.notify_list[n].vid_title
                  li += '</a></p></div>'
                  li += '<span class="notify_date" style="float:right; margin-top: -20%;">'
                  li += data.notify_list[n].date
                  li += '<img src="/static/images/close(32x32).png" class="notify_remove" onclick="rmNotify(\'' + data.notify_list[n].msg_type + '\',' + data.notify_list[n].user + ',' + data.notify_list[n].from_user + ',' + data.notify_list[n].skigit_id + ')"  width="20" height="20">'
                  li += '</span>'
                  li += '</li>'

                }
                else if (data.notify_list[n].msg_type == 'plug-plug') {

                  $j('#nf_loader').show()

                  li += '<li  class="list-group-item f_type notifylist_li comefromtop" style="border:none !important;" id="notify_li_' + data.notify_list[n].msg_type + '_' + data.notify_list[n].user + '_' + data.notify_list[n].from_user + '_' + data.notify_list[n].skigit_id + '" >'
                  li += '<p class="content_notificationheaderfont"><img src="/static/images/notify_pluginplus.png" style="margin-top:15px;margin-right:4px;" /> Coincidence? I think not!</p>'
                  li += '<div class="content_notificationnewpost"><a href="{{ request.scheme }}://{{ request.META.HTTP_HOST }}/profile/'
                  li += data.notify_list[n].from_username
                  li += '" target="_blank" style="color:#0386b4 ">'
                  li += data.notify_list[n].from_username
                  li += '</a>'
                  li += ' has plugged into a Skigit that you plugged into'
                  li += ' <span class="f_type" style="color:#0386b4"> '
                  li += '<a style="color:#0386b4" target="_blank" href="{{ request.scheme }}://{{ request.META.HTTP_HOST }}/?id=' + data.notify_list[n].play_back_id + '">'
                  li += data.notify_list[n].vid_title
                  li += '</a></span></div>'
                  li += '<span class="notify_date" style="float:right; margin-top: -100;">'
                  li += data.notify_list[n].date
                  li += '<img src="/static/images/close(32x32).png" class="notify_remove" onclick="rmNotify(\'' + data.notify_list[n].msg_type + '\',' + data.notify_list[n].user + ',' + data.notify_list[n].from_user + ',' + data.notify_list[n].skigit_id + ')"  width="20" height="20">'
                  li += '</span>'
                  li += '</li>'

                }
                else if (data.notify_list[n].msg_type == 'friends') {

                  $j('#nf_loader').show()

                  li += '<li  class="list-group-item f_type notifylist_li comefromtop" style="border:none !important;" id="notify_li_' + data.notify_list[n].msg_type + '_' + data.notify_list[n].user + '_' + data.notify_list[n].from_user + '_' + data.notify_list[n].skigit_id + '" >'
                  li += '<p class="content_notificationheaderfont"><img src="/static/images/notify_follow_img.png" style="margin-top:15px;margin-right:4px;" /> Wanna new friend?</p>'
                  li += '<div class="content_notificationnewpost"><a href="{{ request.scheme }}://{{ request.META.HTTP_HOST }}/profile/'
                  li += data.notify_list[n].from_username
                  li += '" target="_blank" style="color:#0386b4 ">'
                  li += data.notify_list[n].from_username
                  li += '</a>'
                  li += ' wants to be friends with you.</div>'
                  li += '<span class="notify_date" class="notify_date" style="float:right; margin-top: -54px;">'
                  li += data.notify_list[n].date
                  li += '<img src="/static/images/close(32x32).png" class="notify_remove" onclick="rmNotify(\'' + data.notify_list[n].msg_type + '\',' + data.notify_list[n].user + ',' + data.notify_list[n].from_user + ',' + data.notify_list[n].skigit_id + ')"  width="20" height="20">'
                  li += '</span>'
                  li += '</li>'

                }
                else if (data.notify_list[n].msg_type == 'friends_accepted') {

                  $j('#nf_loader').show()

                  li += '<li  class="list-group-item f_type notifylist_li comefromtop" style="border:none !important;" id="notify_li_' + data.notify_list[n].msg_type + '_' + data.notify_list[n].user + '_' + data.notify_list[n].from_user + '_' + data.notify_list[n].skigit_id + '" >'
                  li += '<p class="content_notificationheaderfont"><img src="/static/images/friends_accept.png" style="margin-top:15px; margin-right:4px;"/> Sure, let’s be friends!</p>'
                  li += '<div class="content_notificationnewpost"><a href="{{ request.scheme }}://{{ request.META.HTTP_HOST }}/profile/'
                  li += data.notify_list[n].from_username
                  li += '" target="_blank" style="color:#0386b4 ">'
                  li += data.notify_list[n].from_username
                  li += '</a>'
                  li += ' has accepted your friendship.</div>'
                  li += '<span class="notify_date" style="float:right; margin-top: -35;">'
                  li += data.notify_list[n].date
                  li += '<img src="/static/images/close(32x32).png" class="notify_remove" onclick="rmNotify(\'' + data.notify_list[n].msg_type + '\',' + data.notify_list[n].user + ',' + data.notify_list[n].from_user + ',' + data.notify_list[n].skigit_id + ')"  width="20" height="20">'
                  li += '</span>'
                  li += '</li>'

                }
                else if (data.notify_list[n].msg_type == 'un_plug') {

                  $j('#nf_loader').show()

                  li += '<li  class="list-group-item f_type notifylist_li comefromtop" style="border:none !important;" id="notify_li_' + data.notify_list[n].msg_type + '_' + data.notify_list[n].user + '_' + data.notify_list[n].from_user + '_' + data.notify_list[n].skigit_id + '" >'
                  li += '<p class="content_notificationheaderfont"><img src="/static/images/unplug_notify.png" style="margin-top:15px;margin-right: 4px;" /> We’re sorry.. your got  unplugged.</p>'
                  li += '<div class="content_notificationnewpost"><a href="{{ request.scheme }}://{{ request.META.HTTP_HOST }}/profile/'
                  li += data.notify_list[n].from_username
                  li += '" target="_blank" style="color:#0386b4 ">'
                  li += data.notify_list[n].from_username
                  li += '</a> unplugged from your skigit'
                  li += ' <span class="f_type" style="color:#0386b4"> '
                  li += '<a style="color:#0386b4" target="_blank" href="{{ request.scheme }}://{{ request.META.HTTP_HOST }}/?id=' + data.notify_list[n].play_back_id + '">'
                  li += data.notify_list[n].vid_title
                  li += '</a></span></div>'
                  li += '<span class="notify_date" style="float:right; margin-top: -86px;">'
                  li += data.notify_list[n].date
                  li += '<img src="/static/images/close(32x32).png" class="notify_remove" onclick="rmNotify(\'' + data.notify_list[n].msg_type + '\',' + data.notify_list[n].user + ',' + data.notify_list[n].from_user + ',' + data.notify_list[n].skigit_id + ')"  width="17" height="17">'
                  li += '</span>'
                  li += '</li>'

                }
                else if (data.notify_list[n].msg_type == 'new_post') {

                  $j('#nf_loader').show()

                  li += '<li  class="list-group-item f_type notifylist_li comefromtop" style="border:none !important;" id="notify_li_' + data.notify_list[n].msg_type + '_' + data.notify_list[n].user + '_' + data.notify_list[n].from_user + '_' + data.notify_list[n].skigit_id + '" >'
                  li += '<p class="content_notificationheaderfont"><img src="/static/images/notify_new.png" style="margin-top:15px;margin-right:4px;" /> Congratulations!</p>'
                  li += '<span class="content_notificationnewpost" > Your Skigit '
                  li += ' <a style="color:#0386b4" target="_blank" href="{{ request.scheme }}://{{ request.META.HTTP_HOST }}/?id=' + data.notify_list[n].play_back_id + '">'
                  li += data.notify_list[n].vid_title
                  li += '</a>  has been posted to Skigit!</span> '
                  li += '<span class="notify_date" style="float:right; margin-top: -56px;">'
                  li += data.notify_list[n].date
                  li += '<img src="/static/images/close(32x32).png" class="notify_remove" onclick="rmNotify(\'' + data.notify_list[n].msg_type + '\',' + data.notify_list[n].user + ',' + data.notify_list[n].from_user + ',' + data.notify_list[n].skigit_id + ')"  width="17" height="17">'
                  li += '</span>'
                  li += '</li>'

                }
                else if (data.notify_list[n].msg_type == 'new_post_follow') {

                  $j('#nf_loader').show()

                  li += '<li  class="list-group-item f_type notifylist_li comefromtop" style="border:none !important;" id="notify_li_' + data.notify_list[n].msg_type + '_' + data.notify_list[n].user + '_' + data.notify_list[n].from_user + '_' + data.notify_list[n].skigit_id + '" >'
                  li += '<p class="content_notificationheaderfont"><img src="/static/images/notify_follow_new_post.png" style="margin-top:15px;margin-right:4px;" /> Following Post! </p>'
                  li += '<div class="content_notificationnewpost"><a href="{{ request.scheme }}://{{ request.META.HTTP_HOST }}/profile/'
                  li += data.notify_list[n].from_username
                  li += '" target="_blank" style="color:#0386b4 ">'
                  li += data.notify_list[n].from_username
                  li += '</a> has  posted a new skigit '
                  li += ' <a style="color:#0386b4" target="_blank" href="{{ request.scheme }}://{{ request.META.HTTP_HOST }}/?id=' + data.notify_list[n].play_back_id + '">'
                  li += data.notify_list[n].vid_title
                  li += '</a>'
                  li += '<span class="notify_date" style="float:right; margin-top: -56px;">'
                  li += data.notify_list[n].date
                  li += '<img src="/static/images/close(32x32).png" class="notify_remove" onclick="rmNotify(\'' + data.notify_list[n].msg_type + '\',' + data.notify_list[n].user + ',' + data.notify_list[n].from_user + ',' + data.notify_list[n].skigit_id + ')"  width="17" height="17">'
                  li += '</span>'
                  li += '</li>'

                }
                else if (data.notify_list[n].msg_type == 'follow') {

                  $j('#nf_loader').show()

                  li += '<li  class="list-group-item f_type notifylist_li comefromtop" style="border:none !important;" id="notify_li_' + data.notify_list[n].msg_type + '_' + data.notify_list[n].user + '_' + data.notify_list[n].from_user + '_' + data.notify_list[n].skigit_id + '" >'
                  li += '<p class="content_notificationheaderfont"><img src="/static/images/notify_follow_img.png" style="margin-top:15px;margin-right:4px;" /> Congratulations!</p>'
                  li += '<div class="content_notificationnewpost"> User <a href="{{ request.scheme }}://{{ request.META.HTTP_HOST }}/profile/'
                  li += data.notify_list[n].from_username
                  li += '" target="_blank" style="color:#0386b4 ">'
                  li += data.notify_list[n].from_username
                  li += '</a>'
                  li += ' started following you. </div>'
                  li += '<span class="notify_date" style="float:right; margin-top: -60;">'
                  li += data.notify_list[n].date
                  li += '<img src="/static/images/close(32x32).png" class="notify_remove" onclick="rmNotify(\'' + data.notify_list[n].msg_type + '\',' + data.notify_list[n].user + ',' + data.notify_list[n].from_user + ',' + data.notify_list[n].skigit_id + ')"  width="20" height="20">'
                  li += '</span>'
                  li += '</li>'

                }
                else if (data.notify_list[n].msg_type == 'share') {

                  $j('#nf_loader').show()

                  li += '<li class="list-group-item f_type notifylist_li comefromtop" style="border:none !important;" id="notify_li_' + data.notify_list[n].msg_type + '_' + data.notify_list[n].user + '_' + data.notify_list[n].from_user + '_' + data.notify_list[n].skigit_id + '" >'
                  li += '<p class="content_notificationheaderfont"><img src="/static/images/notify_radar.png" style="margin-top:15px;margin-right:4px;" /> You are on the Radar!</p>'
                  li += '<div class="content_notificationnewpost"><a href="{{ request.scheme }}://{{ request.META.HTTP_HOST }}/profile/'
                  li += data.notify_list[n].from_username
                  li += '" target="_blank" style="color:#0386b4 ">'
                  li += data.notify_list[n].from_username
                  li += '</a>'
                  li += ' has shared the awesome Skigit</br> '
                  li += '<p> <span class="f_type" style="color:#0386b4"> '
                  li += '<a style="color:#0386b4" target="_blank" href="{{ request.scheme }}://{{ request.META.HTTP_HOST }}/?id=' + data.notify_list[n].play_back_id + '">'
                  li += data.notify_list[n].vid_title
                  li += '</a></span>  with you !</p></div>'
                  li += '<span class="notify_date" style="float:right; margin-top: -100;">'
                  li += data.notify_list[n].date
                  li += '<img src="/static/images/close(32x32).png" class="notify_remove" onclick="rmNotify(\'' + data.notify_list[n].msg_type + '\',' + data.notify_list[n].user + ',' + data.notify_list[n].from_user + ',' + data.notify_list[n].skigit_id + ')"  width="20" height="20">'
                  li += '</span>'
                  li += '</li>'

                }
                else if (data.notify_list[n].msg_type == 'plug_primary') {

                  $j('#nf_loader').show()
                  if (data.notify_list[n].parent_title) {

                    li += '<li class="list-group-item f_type notifylist_li comefromtop" style="border:none !important;" id="notify_li_' + data.notify_list[n].msg_type + '_' + data.notify_list[n].user + '_' + data.notify_list[n].from_user + '_' + data.notify_list[n].skigit_id + '" >'
                    li += '<p class="content_notificationheaderfont"><img src="/static/images/notify_primary_delete.png" style="margin-top:15px;margin-right:4px;" /> The Primary skigit</p>'
                    li += '<div class="content_notificationewpost"><span class="f_type" style="color:#0386b4"> '
                    li += data.notify_list[n].vid_title
                    li += '</span> was deleted. You are now connected to the next Plug-in in line '
                    li += '<span class="f_type" style="color:#0386b4">'
                    li += '<a style="color:#0386b4" target="_blank" href="{{ request.scheme }}://{{ request.META.HTTP_HOST }}/?id=' + data.notify_list[n].parent_skigi_id + '">'
                    li += data.notify_list[n].parent_title
                    li += '</a></span> .</div>'
                    li += '<span class="notify_date" style="float:right; margin-top: -100;">'
                    li += data.notify_list[n].date
                    li += '<img src="/static/images/close(32x32).png" class="notify_remove" onclick="rmNotify(\'' + data.notify_list[n].msg_type + '\',' + data.notify_list[n].user + ',' + data.notify_list[n].from_user + ',' + data.notify_list[n].skigit_id + ')"  width="20" height="20">'
                    li += '</span>'
                    li += '</li>'
                  }
                  else if (data.notify_list[n].child_title) {
                    li += '<li class="list-group-item f_type notifylist_li comefromtop" style="border:none !important;" id="notify_li_' + data.notify_list[n].msg_type + '_' + data.notify_list[n].user + '_' + data.notify_list[n].from_user + '_' + data.notify_list[n].skigit_id + '" >'
                    li += '<p class="content_notificationheaderfont"><img src="/static/images/notify_primary_delete.png" style="margin-top:15px;margin-right:4px;" /> The Primary skigit</p>'
                    li += '<div class="content_notificationnewpost"><span class="f_type" style="color:#0386b4">'
                    li += '<a style="color:#0386b4" target="_blank" href="{{ request.scheme }}://{{ request.META.HTTP_HOST }}/?id=' + data.notify_list[n].play_back_id + '">'
                    li += data.notify_list[n].vid_title
                    li += '</a></span> was deleted. You are now connected to the next Plug- in in line'
                    li += '<span class="f_type" style="color:#0386b4">'
                    li += '<a style="color:#0386b4" target="_blank" href="{{ request.scheme }}://{{ request.META.HTTP_HOST }}/?id=' + data.notify_list[n].child_skigi_id + '">'
                    li += data.notify_list[n].child_title
                    li += '</a></span>.</div>'
                    li += '<span class="notify_date" style="float:right; margin-top: -100;">'
                    li += data.notify_list[n].date
                    li += '<img src="/static/images/close(32x32).png" class="notify_remove" onclick="rmNotify(\'' + data.notify_list[n].msg_type + '\',' + data.notify_list[n].user + ',' + data.notify_list[n].from_user + ',' + data.notify_list[n].skigit_id + ')"  width="20" height="20">'
                    li += '</span>'
                    li += '</li>'
                  }
                }

                $j('#nf_loader').hide()
                $j('#notify_ul').prepend($j('#notify_ul').append(li)).addClass('pushdown');
                setTimeout(function () {
                  $j('#Trees').removeClass('pushdown');
                }, 600);
              }

            }
          }
          $j('#general_badge').hide()
          $j('#general_badge').text(0)
        }
      });
    }

    function refresh_global_notification() {
      $j.ajax({
        url: "/get_notification_count/",
        success: function (data) {
          if (data.count > 0) {
            $j('#general_badge').show();
            $j('#general_badge').text(data.count);
          }
          else {
            $j('#general_badge').hide();
            $j('#general_badge').text(0);
          }
        }
      });
      setTimeout(refresh_global_notification, 10000);
    }

    function refresh_friend_notification() {
      $j.ajax({
        url: "/friends/friend-count-notification/",
        type: "GET",
        success: function (data) {
          if (data.result) {
            if (data.count > 0) {
              $j('#friend_badge').show()
              $j('#friend_badge').text(data.count)
            }
            else {
              $j('#friend_badge').hide()
            }
          }
        }

      });
      setTimeout(refresh_friend_notification, 10000);
    }


    refresh_global_notification();
    refresh_friend_notification();

    friendsNotificaton = function (e) {

      $j.ajax({
        url: "/friends/friend-notification/",
        type: "GET",
        success: function (data) {
          $j('#frnd_notification').empty()

          if (data.result) {
            if (data.friend_list.length > 0) {

              $j('#friend_badge').show()
              $j('#friend_badge').html(data.friend_list.length)

              for (var f = 0; f < data.friend_list.length; f++) {
                if (data.friend_list[f].profile_img) {
                  var l_img = data.friend_list[f].profile_img
                }
                else {
                  l_img = '/static/images/noimage_user.jpg'
                }
                var li = '<li class="list-group-item comefromtop" id="friend_li' + data.friend_list[f].to_user + '" >' +
                    '<img class="avatar" style="top: 0px; margin-top: -10%; !important;" src="' + l_img + '"/>' +
                    '<label class="f_type" style="margin-left: 10px; margin-top: 2%;"> Wanna new friend? </br> ' + data.friend_list[f].name + ' wants to be friends with you </label> ' +
                    '<span class="btn_span" id="button_sapn' + data.friend_list[f].to_user + '">' +
                    '<button id="id_accept_btn' + data.friend_list[f].to_user + '" data-friend="" style="float:right; background: none !important; width: auto !important; height: auto !important;" onclick="acceptFrNotofication(' + data.friend_list[f].to_user + ')" > ' +
                    '<span title="Accept Request" id="id_accept_friens" class="glyphicon glyphicon-ok-circle"></span></button>' +
                    '<button id="id_declain_btn' + data.friend_list[f].to_user + '" style="float:right; background: none !important; width: auto !important; height: auto !important;" onclick="rejectFrNotofication(' + data.friend_list[f].to_user + ')">' +
                    '<span  title="Reject Request" id="id_reject_friens" class="glyphicon glyphicon-remove-circle">' +
                    '</span></button></span></li>'
                $j('#frnd_notification').append(li)
              }
            }
            else {
              var li = '<li class="f_type" style="color:#bbb9b9; font-size: smaller; text-align: center;">There is no pending Notifications.</li>'
              $j('#frnd_notification').empty();
              $j('#frnd_notification').append(li);
              $j('#friend_badge').hide()
            }
          }
        }
      });
    };

    like_unlike_entry = function (like_class, like_id) {
      var skigit_id = like_id;
      var post_clas = $j("#" + like_class).attr('class');
      var post_id = like_class;
      var like_count = $j.trim($j('#like_count' + like_id).text())

      if (post_clas == 'unlike') {
        $j.ajax({
          type: "POST",
          url: "/skigit_i_like/",
          data: {
            'skigit_id': skigit_id,
            'csrfmiddlewaretoken': '{{csrf_token}}'
          },
          success: function (response) {
            if (response.is_success) {
              if (response.like == 1 || response.like == '1') {
                $j("#" + post_id).attr("title", "Unlike");
                $j("#" + post_id).removeClass("unlike");
                $j("#" + post_id).addClass("like");
                $j("#" + post_id + "> img").attr("src", "/static/images/heart_liked(22x22).png");
                $j('#like_count' + like_id).text(parseInt(like_count) + 1)
              }
            }
          },
          error: function (rs, e) {
            $j("#popup_msg").text("Error into like the Skigit...! Please try again");
            $j("#popScreen").show();
          }
        });
      }
      else if (post_clas == 'like') {
        $j.ajax({
          type: "POST",
          url: "/skigit_i_unlike/",
          data: {
            'skigit_id': skigit_id,
            'csrfmiddlewaretoken': '{{csrf_token}}'
          },
          success: function (response) {
            if (response.is_success) {
              if (response.unlike == 1 || response.unlike == '1') {
                $j("#" + post_id).attr("title", "Like");
                $j("#" + post_id).removeClass("like");
                $j("#" + post_id).addClass("unlike");
                $j("#" + post_id + "> img").attr("src", "/static/images/heart(22x22).png");
                $j('#like_count' + like_id).text(parseInt(like_count) - 1)
              }
            }
          },
          error: function (rs, e) {
            $j("#popup_msg").text("Error into like the Skigit...! Please try again");
            $j("#popScreen").show();
          }
        });
      }
    };

    shareToFriends = function (skigit_id) {

      var share_value = [];
      var plug_count = $j.trim($j('#share_count' + skigit_id).text())

      $j("input[type=checkbox]:checked").each(function () {
        if ($j('#sharebox' + skigit_id + $j(this).val()).is(':checked')) {
          share_value.push(parseInt($j(this).val()));
        }
      });

      if (share_value.length > 0) {
        $j('#button_share' + skigit_id).prop('disabled', true);
        $j('#msg' + skigit_id).html('Please Wait...').css('color', 'orange', 'text-aling', 'center')
        var currentTimezone = jstz.determine();
        var timezone = currentTimezone.name();
        $j.ajax({
          type: "POST",
          url: "/share-skigits/",
          data: {
            'vid_id': skigit_id,
            'friend_list[]': unique(share_value),
            'time_zone': timezone,
            'csrfmiddlewaretoken': '{{csrf_token}}'
          },
          success: function (data) {
            if (data.is_success) {
              $j(':checkbox').each(function () {
                this.checked = false;
              });
              $j('#msg' + skigit_id).html('Sharing with friends successful').css('color', 'green')
              $j('#button_share' + skigit_id).prop('disabled', false);
              $j('#share_count' + skigit_id).text(parseInt(plug_count) + parseInt(unique(share_value).length))
              for (var k = 0; k < unique(share_value).length; k++) {
                $j('#id_date_label' + skigit_id + unique(share_value)[k]).text(data.date)
              }
              setTimeout(function () {
                $j('#msg' + skigit_id).empty()
              }, 2500)
            }
          },
          error: function (rs, e) {
            $j("#popup_msg").text("Error into Share Skigit Index Page Please try again");
            $j("#popScreen").show();
            $j('#button_share' + skigit_id).prop('disabled', false);
          }
        });
      }
      else {
        $j('#msg' + skigit_id).html('Mark options to share a skigit with friends').css('color', 'red')
        setTimeout(function () {
          $j('#msg' + skigit_id).empty()
        }, 2500)
        $j('#button_share' + skigit_id).prop('disabled', false);
      }
    };

    sharebox = function (friend_id, video_id) {
      var share_id = $j('#sharebox' + video_id + friend_id).attr('id');
      var skigit_id = video_id

      if ($j('#select_all' + video_id).is(':checked')) {
        $j('#select_all' + video_id).prop('checked', false)
      }
    };
  });

});

// modal
$j('#skigit-modal').on('show.bs.modal', function (event) {
  var address = $j(event.relatedTarget);
  $j('.modal-content').load(address.attr('href'), function () {
  });
});

$j("#skigit-modal").on("hidden.bs.modal", function(){
    $j(".modal-content").html("");
});


