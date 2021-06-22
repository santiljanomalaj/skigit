
import json
import uuid
import braintree
from PIL import Image
from urllib.request import urlopen

from datetime import datetime
from datetime import timedelta
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import logout
from django.core.exceptions import ObjectDoesNotExist
from django.core.serializers.json import DjangoJSONEncoder
from django.http import HttpResponse, HttpResponseRedirect
from django.utils.decorators import available_attrs
from django.utils.six import wraps
from skigit_project.settings import EMAIL_HOST_USER
from core.emails import send_email
from django.db.models import Q
from invoices.models import Invoice

from friends.models import SocialShareThumbnail
from user.models import Profile


def get_user_type(user):
    """
        Get Type of User Business/General
    """
    if user.groups.all()[0].name == settings.GENERAL_USER:
        return 'general'
    elif user.groups.all()[0].name == settings.BUSINESS_USER:
        return 'business'


def is_user_general(user):
    """
        Checks whether user is General User
    """
    return user.groups.all()[0].name == settings.GENERAL_USER


def is_user_business(user):
    """
        Checks whether user is Business User
    """
    return user.groups.all()[0].name == settings.BUSINESS_USER


def json_response(data):
    """
        Http Response Call for returning Json formatted data
    """
    return HttpResponse(json.dumps(data, cls=DjangoJSONEncoder), content_type="application/json")


def require_filled_profile(func):
    """
        Required field Profile page
    """

    @wraps(func, assigned=available_attrs(func))
    def inner(request, *args, **kwargs):
        if request.user.is_authenticated():
            try:
                user = request.user
                user_profile = Profile.objects.get(user=user)
                if is_user_business(user):
                    is_business =True
                else:
                    is_business = False

                fields = [
                    user.username,
                    user.first_name,
                    user.last_name,
                    user.email,
                    user_profile.logo_img,
                    user_profile.birthdate,
                    user_profile.language,
                    user_profile.country,
                    user_profile.state,
                    user_profile.city,
                    user_profile.zip_code,
                ]

                if user.is_superuser or user.is_staff or is_user_general(user):
                    if not all(fields):
                        messages.error(request,
                                       'Please Fill The Complete Profile Detail')
                        raise ObjectDoesNotExist
                    elif not user_profile.profile_img:
                        messages.error(request,
                                       'Please Upload Your Profile Picture')
                        raise ObjectDoesNotExist
                elif user.groups.all()[0].name == settings.BUSINESS_USER:
                    if not all(fields):
                        messages.error(request,
                                       'Please Fill The Complete Profile Detail')
                        raise ObjectDoesNotExist
                    elif not user_profile.profile_img:
                        messages.error(request, 'Please Upload Your Profile Picture')
                        raise ObjectDoesNotExist
                    elif not user_profile.logo_img.filter(is_deleted=False).all():
                        messages.error(request, 'Please Upload Your Business Logo')
                        raise ObjectDoesNotExist
                    elif user_profile.logo_img.filter(is_deleted=False).all().count() > 5:
                        messages.error(request, 'Max 5 Business Logo allowed.')
                        for i in range(1, user_profile.logo_img.filter(is_deleted=False).all().count()):
                            if(user_profile.logo_img.filter(is_deleted=False).all().count() > 5):
                                user_profile.logo_img.filter(is_deleted=False).all().last().delete()
                        raise ObjectDoesNotExist
                    elif user_profile.extra_profile_img.all().count() > 5:
                        messages.error(request, 'Max 5 Profile Images allowed.')
                        for i in range(1, user_profile.extra_profile_img.all().count()):
                            if(user_profile.extra_profile_img.all().count() > 5):
                                user_profile.extra_profile_img.all().last().delete()
                        raise ObjectDoesNotExist
                    elif is_business and not Invoice.objects.filter(user=request.user, type='CreditCard',
                                                                    is_deleted=False).exists() and not \
                        Invoice.objects.filter(user=request.user, type='PayPalAccount', is_deleted=False).exists():
                        messages.error(request, 'Payment information is not verified. Please verify payment method by '
                                        'filling PayPal or Credit/Debit card details.')
                        raise ObjectDoesNotExist
                    elif is_business and request.user.profile.payment_method == '1' \
                        and not Invoice.objects.filter(user=request.user, type='CreditCard', is_deleted=False).exists():
                        messages.error(request, 'Payment information is not verified. Please verify payment method by '
                                    'filling PayPal or Credit/Debit card details.')
                        raise ObjectDoesNotExist
                    elif is_business and request.user.profile.payment_method == '0' \
                        and not Invoice.objects.filter(user=request.user, type='PayPalAccount', is_deleted=False).exists():
                        messages.error(request, 'Payment information is not verified. Please verify payment method by '
                                    'filling PayPal or Credit/Debit card details.')
                        raise ObjectDoesNotExist

                else:
                    logout(request)
                    return HttpResponseRedirect('/')
            except ObjectDoesNotExist:
                return HttpResponseRedirect('/profile')
        return func(request, *args, **kwargs)
    return inner


def notify_admins(func):
    def wrapper(request, *args, **kwargs):
        try:
            message = "<table style='width:100%;' cellpadding='0' cellspacing='0'>"\
                        "<tr><td style='text-align:center;'><center><h3 style='color:#1C913F; margin-bottom:0;font-family: "+"Proza Libre"+", sans-serif;'>"\
                        "Password Change!</h3></center></td></tr>"\
                        "<tr><td style='color:#222;'><p style='text-align:justify;'>"\
                        "Hi! You recently asked Skigit to change your password. If you did not request a new password, let us know immediately by contacting use at "\
                        "<a href='mailto:"+EMAIL_HOST_USER+"' style='color:#0386B8;'><span style='color:#0386B8;'>"+EMAIL_HOST_USER+"</span></a></p>"\
                        "<p>Thank you,<br/>Skigit</p></td></tr>"\
                        "<tr><td style='text-align:center;width:165px;'><img src='http://skigit.com/static/skigit/images/shair.png' style='width:165px;'/></td></tr>"\
                        "</table>"
            subject = "Password Change"
            send_email(subject, message, request.user.email, '', EMAIL_HOST_USER)
        except:
            msg = 'Exception'
        return func(request, *args, **kwargs)
    return wrapper


def payment_required(func):
    @wraps(func, assigned=available_attrs(func))
    def inner(request, *args, **kwargs):
        if request.user.is_authenticated():
            try:
                user = request.user
                if is_user_business(user):
                    is_business = True
                else:
                    is_business = False

                if user.groups.all()[0].name == settings.BUSINESS_USER:
                    inv1 = Invoice.objects.filter(user=request.user, type='CreditCard', is_deleted=False).exists()
                    inv2 = Invoice.objects.filter(user=request.user, type='PayPalAccount', is_deleted=False).exists()
                    if is_business and request.user.profile.payment_method == '1' and not inv1:
                        messages.error(request, 'Payment information is not verified. Please verify payment method by '
                                                'filling PayPal or Credit/Debit card details.')
                        raise ObjectDoesNotExist
                    elif is_business and request.user.profile.payment_method == '0' and not inv2 :
                        messages.error(request, 'Payment information is not verified. Please verify payment method by '
                                                'filling PayPal or Credit/Debit card details.')
                        raise ObjectDoesNotExist
            except ObjectDoesNotExist:
                return HttpResponseRedirect('/profile')
        return func(request, *args, **kwargs)
    return inner


def create_share_thumbnails(skigit=None, back_image=None, business_image=None, company_logo_url=None):
    """

    :param skigit:
    :param back_image:
    :param business_image:
    :return:
    """

    try:
        quality_val = 90
        # New Image Canvas Size of 800x470
        #canvas = Image.new("RGB", (480, 360), (255, 0, 0, 0))
        canvas = Image.new("RGB", (600, 600), (0, 0, 0, 0))
        # Get Files from base location
        image1 = urlopen(back_image)
        # Play back image url path '/skigit/images/play_back.png'
        image2 = open(settings.STATIC_ROOT + '/skigit/images/Skigit_Logo_Glow.png', "rb")

        if business_image:
            image3 = urlopen(business_image)
            business_logo = Image.open(image3)
            business_logo.thumbnail((100, 100), Image.ANTIALIAS)
            (lx, ly) = business_logo.size

        # Open Images for edit Creating Image objects
        background = Image.open(image1)
        background.thumbnail((600,600), Image.ANTIALIAS)
        play_back = Image.open(image2)
        (X, Y) = canvas.size
        (X1, Y1) = background.size
        X2 = int((X - X1)/2)
        Y2 = int((Y - Y1)/2)

        # Converts Image Into PNG form (Creates transparent background)
        # play_back = play_back.convert("RGBA")
        # datas = play_back.getdata()
        # newData = []
        # for item in datas:
        #     if item[0] == 255 and item[1] == 255 and item[2] == 255:
        #         newData.append((255, 255, 255, 0))
        #     else:
        #         newData.append(item)
        # play_back.putdata(newData)
        play_back.thumbnail((120, 120), Image.ANTIALIAS)
        canvas.paste(background, (X2, Y2))
        canvas.paste(play_back, (240, 220), play_back)

        if business_image:
            # if lx >= 100:
            #     new_lx = (X - lx) - 60
            #     new_ly = (Y - ly) - 50
            # if ly >= 100:
            #     new_lx = (X - lx) - 60
            #     new_ly = (Y - ly) - 50
            new_lx = (X - lx) - 2
            new_ly = (Y - ly) - 2
            canvas.paste(business_logo, (new_lx, new_ly))

        new_image_name = '%s.jpg' % uuid.uuid4().hex.lower()
        new_full_path = settings.MEDIA_ROOT + 'video_thumbnails/%s' % new_image_name
        media_path = settings.MEDIA_URL + 'video_thumbnails/%s' % new_image_name
        image_url = None

        if not SocialShareThumbnail.objects.filter(video=skigit.skigit_id).exists():
            canvas.save(new_full_path, 'JPEG', quality=quality_val)
            new_image = SocialShareThumbnail.objects.create(video=skigit.skigit_id, url=media_path)
            image_url = new_image.url
        else:
            canvas.save(new_full_path, 'JPEG', quality=quality_val)
            SocialShareThumbnail.objects.filter(video=skigit.skigit_id).update(url=media_path)
            new_image = SocialShareThumbnail.objects.get(video=skigit.skigit_id)
            image_url = new_image.url
        return image_url
    except:
        return None


def age_calculator(birth_date):
    """
        Age Calculator.
    """
    age = (datetime.today().date() - birth_date).days/365
    return age


def get_related_users(request, skigit_user_id, *argv):
    """
        Returns the Relative Skigits on the basis of category,
         subcategory, gender, and Age.
    """
    user_list = []
    if Profile.objects.filter(user__id=request.user.id).exists():
        profile_dic = Profile.objects.get(user__id=request.user.id)
        user_gender = profile_dic.gender
        current_age = int(age_calculator(profile_dic.birthdate))
        user_profile = Profile.objects.filter(Q(gender=user_gender) | Q(user__id=int(skigit_user_id)))
        for profile in user_profile:
            if profile.birthdate and profile.birthdate.year <= datetime.now().year:
                age = int(age_calculator(profile.birthdate))
                if 1 <= age < 5 and 1 <= current_age < 5:
                    user_list.append(profile.user.id)
                elif 5 <= age <= 12 and 5 <= current_age <= 12:
                    user_list.append(profile.user.id)
                elif 13 <= age <= 18 and 13 <= current_age <= 18:
                    user_list.append(profile.user.id)
                elif 19 <= age <= 26 and 19 <= current_age <= 26:
                    user_list.append(profile.user.id)
                elif 27 <= age <= 35 and 27 <= current_age <= 35:
                    user_list.append(profile.user.id)
                elif 36 <= age <= 45 and 36 <= current_age <= 45:
                    user_list.append(profile.user.id)
                elif 46 <= age <= 55 and 46 <= current_age <= 55:
                    user_list.append(profile.user.id)
                elif 56 <= age <= 65 and 56 <= current_age <= 65:
                    user_list.append(profile.user.id)
                elif age > 65 and current_age > 65:
                    user_list.append(profile.user.id)

        if not user_list:
            years_ago_date = profile_dic.birthdate - timedelta(days=(65 * 365))
            user_list = Profile.objects.filter(gender=user_gender, birthdate__gt=years_ago_date,
                                               birthdate__lt=profile_dic.birthdate).values_list('user__id', flat=True)
    return user_list


def client_token(request):
    """
        Generate a client Token for client
    """
    if not Invoice.objects.filter(user=request.user, type='CreditCard', is_deleted=False).exists():
        token = braintree.ClientToken.generate()
    else:
        invoice_obj = Invoice.objects.filter(user=request.user, type='CreditCard', is_deleted=False).first()
        token = braintree.ClientToken.generate({'customer_id': invoice_obj.customer_id})
    return token


def client_paypal_token(request):
    """
        Generate a client Token for client

    Args:
        request: requested data
    """
    if not Invoice.objects.filter(user=request.user, type='PayPalAccount', is_deleted=False).exists():
        token = braintree.ClientToken.generate()
    else:
        invoice_obj = Invoice.objects.filter(user=request.user, type='PayPalAccount', is_deleted=False).first()
        token = braintree.ClientToken.generate({'customer_id': invoice_obj.customer_id})
    return token