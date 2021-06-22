
/*const togglePassword = document.querySelector('#togglePassword');
const password = document.querySelector('#password');

togglePassword.addEventListener('click', function (e) {
    // toggle the type attribute
    const type = password.getAttribute('type') === 'password' ? 'text' : 'password';
    password.setAttribute('type', type);
    // toggle the eye slash icon
    this.classList.toggle('fa-eye-slash');
});*/


jQuery(document).ready(function($){
    var img1 = new Image();
    var img2 = new Image();
    var myMessages = ['info', 'warning', 'error', 'success']; // define the messages types
    var DELETE_ICON = '/static/skigit/wp-content/themes/detube/images/deleteIcon.png';
    var RIGHT_ICON = '/static/skigit/wp-content/themes/detube/images/success_icon.png';
    var DELETE_ICON_IMG = '<img width="17" height="17" src="' + DELETE_ICON + '">';
    var RIGHT_ICON_IMG = '<img width="17" height="17" src="' + RIGHT_ICON + '">';
    var BASE_URL = '/';


    function getCookie(name)
    {
        var cookieValue = null;
        if (document.cookie && document.cookie !== '')
        {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++)
            {
                var cookie = jQuery.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) === (name + '='))
                {
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
        $(".notify_msg_div").html('');
    }

    // function set_msg(tag, msg) {
    //     msg_string = '<div style="display:none;"  class="' + tag + ' message"><h3>' + msg + '</h3></div>';
    //     $(".notify_msg_div").append(msg_string);
    // }

    function show_msg() {
        hideAllMessages();
        to = 0;
        for (var i = 0; i < myMessages.length; i++)
        {
            if ($('.' + myMessages[i]).length > 0)
            {
                $('.' + myMessages[i]).show();
                $('.' + myMessages[i]).animate({top: to}, 1200);
                to += $('.' + myMessages[i]).outerHeight();
            }
            showMessage(myMessages[i]);
        }

        // When message is clicked, hide it
        $('.message').click(function () {
            $(this).animate({top: -$(this).outerHeight()}, 500);
        });
        setTimeout(function () {
            hidemsg();
        }, 12000)
    }

    function hidemsg() {
        to = 0;
        for (var i = 0; i < myMessages.length; i++)
        {
            if ($('.' + myMessages[i]).length > 0)
            {
                to += $('.' + myMessages[i]).outerHeight();
                $('.' + myMessages[i]).animate({top: -to}, 1200);
            }
            showMessage(myMessages[i]);
        }
    }
    function hideAllMessages()
    {
        var messagesHeights = []; // this array will store height for each
        for (var i = 0; i < myMessages.length; i++)
        {
            messagesHeights[i] = $('.' + myMessages[i]).outerHeight();
            $('.' + myMessages[i]).css('top', '-'+messagesHeights[i]); //move element outside viewport
        }
    }

    function showMessage(type)
    {
        $('.' + type + '-trigger').click(function () {
            hideAllMessages();
            $('.' + type).animate({top: "0"}, 500);
        });
    }

    function logo_imgURL(input) {
        if (input.files && input.files[0]) {
            var reader = new FileReader();
            reader.onload = function (e) {
                $('#logo_img')
                    .attr('src', e.target.result);
            };
            reader.readAsDataURL(input.files[0]);
        }
    }

    function profile_imgURL(input) {
        if (input.files && input.files[0]) {
            var reader = new FileReader();
            reader.onload = function (e) {
                $('#user_profile_image')
                    .attr('src', e.target.result);
            };
            reader.readAsDataURL(input.files[0]);
        }
    }

    function password_reset_email_check() {

        var id_email = $('#id_email').val().trim();
        var is_error = false
        //var is_success = false
        var msg = "Please Wait..";

        if (id_email && !is_empty(id_email)) {
            $.ajax({
                url: "/email_exits_check/", // the endpoint
                type: "POST", // http method
                data: {'email': id_email}, // data sent with the delete request
                success: function (response) {
                    if (response)
                    {
                        if (response.is_success)
                        {
                            is_error = false;
                            msg = response.message;
                        }
                        else
                        {
                            is_error = true;
                            msg = response.message;
                        }
                    }
                    else
                    {
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
            if (is_error)
            {
                $("#password_reset_error").html("<p class='error_msg'>" + msg + "</p>");
                return is_error
            }
            else {
                $("#password_reset_error").html("<p class='success_msg'>" + msg + "</p>");
                return is_error
            }
        }, 800);
    }

    var forceSubmitForm = false;

    $("img.img2").hide();
    show_msg();
    $("#navbar .nav li a").hover(function () {
        var $img1 = $(this).children('.img1');
        var $img2 = $(this).children('.img2');
        if ($img1 && $img1.length === 1 && $img2 && $img2.length === 1)
        {
            img1.src = $img1.attr('src');
            img2.src = $img2.attr('src');
            $img2.attr('src', img1.src);
            $img1.attr('src', img2.src);
        }
    }, function () {
        var $img1 = $(this).children('.img2');
        var $img2 = $(this).children('.img1');
        if ($img1 && $img1.length === 1 && $img2 && $img2.length === 1)
        {
            img1.src = $img1.attr('src');
            img2.src = $img2.attr('src');
            $img2.attr('src', img1.src);
            $img1.attr('src', img2.src);
        }
    });
    $('.dropdown-menu').click(function (event) {
        event.stopPropagation();
    });
    $.ajaxSetup({
        beforeSend: function (xhr, settings) {
            if (!(/^http:.*/.test(settings.url) || /^https:.*/.test(settings.url))) {
                xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
            }
        }
    });

    $("form#form_login").submit(function (e) {
        e.preventDefault()
        $("#chat_msg_submit").attr('disabled', 'disabled');
        var form_data = $(this).serialize();
        var user_login = $('#user_login').val().trim();
        var user_pass = $("#user_pass").val().trim();
        var is_error = false
        var is_success = false
        var $submit = $("form#form_login").children().find("input[type='submit']");
        $submit.attr('disabled', 'disabled');
        var msg = "";
        if (user_login && !is_empty(user_login.trim())) {
            if (user_pass && !is_empty(user_pass.trim())) {
                $.ajax({
                    url: "/login_ajax/", // the endpoint
                    type: "POST", // http method
                    data: form_data, // data sent with the delete request
                    success: function (response) {
                        // hide the post
                        if (response)
                        {
                            if (response.is_success)
                            {
                                is_success = true
                                msg = response.message
                                setTimeout(function () {
                                    window.location = response.base_location;
                                }, 500);
                            }//message send
                            else
                            {
                                is_success = false
                                msg = response.message
                            }
                        }
                        else
                        {
                            is_success = false
                            msg = "<span style='font-size:20px;'><i class='glyphicon glyphicon-remove-circle' style='top: 5px !important;' /></span> Oops! Server encountered an error.";
                        }
                        if (is_success)
                        {
                            $("#login_ingo_msg").html('<p class="success_msg" >'+ msg+'</p>');
                        }
                        else {
                            $("#login_ingo_msg").html('<p class="error_msg" >'+msg+'</p>');
                        }
                        setTimeout(function () {
                            $("#login_ingo_msg > * ").fadeOut('slow');
                            $("#login_ingo_msg").empty();
                        }, 6000);
                        $submit.removeAttr('disabled');
                    },
                    error: function (xhr, errmsg, err) {
                        // Show an error
                        is_error = true;
                        msg = "<span style='font-size:20px;'><i class='glyphicon glyphicon-remove-circle' style='top: 5px !important;' /></span> Oops! We have encountered an error." + xhr.status + ": " + xhr.responseText;
                        $("#smallModal").hide();
                        $submit.removeAttr('disabled');
                        if (is_error)
                        {
                            rem_msg();
                            set_msg('error', msg);
                            show_msg();
                        }
                    }
                });
            }
            else
            {
                is_error = true;
                msg = "<span class='sign-error'><i class='glyphicon glyphicon-remove-circle' /></span><span class='text-error'>Your username and/or password are incorrect. Please try again.</span>";
            }
        }
        else
        {
            is_error = true;
            msg = "<span class='sign-error'><i class='glyphicon glyphicon-remove-circle' /></span><span class='text-error'>Your username and/or password are incorrect. Please try again.</span>";
       }

        if (is_error)
        {
            $("#login_ingo_msg").html('<p class="error_msg" >' + msg + '</p>');
        }

        setTimeout(function () {
            $("#login_ingo_msg > * ").fadeOut('slow');
            $("#login_ingo_msg").empty();
        }, 5000);
        $submit.removeAttr('disabled');
    });
    $('.img-zoom').hover(function () {
        $(this).addClass('transition');
    }, function () {
        $(this).removeClass('transition');
    });

    if ($("#id_logo_img").length === 1)
    {
        $("#id_logo_img").attr("onchange", "logo_imgURL(this);");
    }
    if ($("#id_profile_img").length === 1)
    {
        $("#id_profile_img").attr("onchange", "profile_imgURL(this);");
    }

    $("#password_reset_form").submit(function () {

        if(forceSubmitForm) return true;
        var id_email = $('#id_email').val().trim();
        var is_error = false;
        var msg = "Please Wait..";

        if (id_email && !is_empty(id_email)) {
            $.ajax({
                url: "/email_exits_check/", // the endpoint
                type: "POST", // http method
                data: {'email': id_email}, // data sent with the delete request
                success: function (response) {
                    // hide the post
                    if (response)
                    {
                        if (response.is_success)
                        {
                            forceSubmitForm = true;
                            is_error = false;
                            msg = response.message;
                        }//message send
                        else
                        {
                            is_error = true;
                            msg = response.message;
                        }
                    }
                    else
                    {
                        is_error = true;
                        msg = "Oops! Server encountered an error.";
                    }
                    if (is_error)
                    {
                        $("#password_reset_error").html("<p class='error_msg'>" + msg + "</p>");
                        return false;
                    }
                    else {
                        $("#password_reset_error").html("<p class='success_msg'>" + msg + "</p>");
                        $("#password_reset_form").submit();
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

        if (is_error)
        {
            $("#password_reset_error").html("<p class='error_msg'>" + msg + "</p>");
        }
        return false;
    });
});


$(document).ready(function()
{
    $('#user_action #general_notify').click(function()
    {
        $.post("/notification/get/",
            {},
            function(data,status){
                if(data.is_success ){
                    msg=data.message;
                    $('#gen_notification').fadeToggle('slow').html(msg);
                }
            });
    });
});
