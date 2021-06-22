
import json
import uuid
import logging
import braintree
from PIL import Image, ImageDraw, ImageFilter
from PIL import ImageOps
from urllib.request import urlopen
from urllib.parse import urlencode
import re
import requests

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
from django.shortcuts import _get_queryset
from django.urls import reverse
from sorl.thumbnail import get_thumbnail
from rest_framework import permissions
from rest_framework.views import exception_handler

from skigit_project.settings import EMAIL_HOST_USER
from django.db.models import Q
from active_users.api import get_active_users
from invoices.models import Invoice
from django.contrib.auth.models import User

from friends.models import SocialShareThumbnail, FriendInvitation, Friend
from user.models import Profile

from mailpost.models import EmailTemplate
from allauth.socialaccount.models import SocialApp


logger = logging.getLogger('Utils')


def get_user_type(user):
    """ Get Type of User Business/General
    """
    if user.groups.filter(name=settings.GENERAL_USER).exists():
        return 'general'
    elif user.groups.filter(name=settings.BUSINESS_USER).exists():
        return 'business'
    else:
        return ''

def is_user_general(user):
    """
        Checks whether user is General User
    """
    return user.groups.filter(name=settings.GENERAL_USER).exists()


def is_user_business(user):
    """
        Checks whether user is Business User
    """
    return user.groups.filter(name=settings.BUSINESS_USER).exists()


def json_response(data):
    """
        Http Response Call for returning Json formatted data
    """
    return HttpResponse(json.dumps(data, cls=DjangoJSONEncoder), content_type="application/json")

def get_profile_status(user):
    '''
        Get profile status
    '''

    message = ''
    result = {}

    try:
        user_profile = Profile.objects.get(user=user)
        if is_user_business(user):
            is_business = True
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
                message = 'Please Fill The Complete Profile Detail'
            elif not user_profile.profile_img:
                message = 'Please Upload Your Profile Picture'
        elif user.groups.filter(name=settings.BUSINESS_USER).exists():
            if not all(fields):
                message = 'Please Fill The Complete Profile Detail'
            elif not user_profile.profile_img:
                message = 'Please Upload Your Profile Picture'
            elif not user_profile.logo_img.filter(is_deleted=False).all():
                message = 'Please Upload Your Business Logo'
            elif user_profile.logo_img.filter(is_deleted=False).all().count() > 5:
                message = 'Max 5 Business Logo allowed.'
                for i in range(1, user_profile.logo_img.filter(is_deleted=False).all().count()):
                    if (user_profile.logo_img.filter(is_deleted=False).all().count() > 5):
                        user_profile.logo_img.filter(is_deleted=False).all().last().delete()
            elif user_profile.extra_profile_img.all().count() > 5:
                message = 'Max 5 Profile Images allowed.'
                for i in range(1, user_profile.extra_profile_img.all().count()):
                    if (user_profile.extra_profile_img.all().count() > 5):
                        user_profile.extra_profile_img.all().last().delete()

            elif is_business and not Invoice.objects.filter(user=user, type='CreditCard',
                                                            is_deleted=False).exists() and not \
                    Invoice.objects.filter(user=user, type='PayPalAccount', is_deleted=False).exists():
                message = 'Payment information is not verified. Please verify payment method by '\
                                        'filling PayPal or Credit/Debit card details.'
            elif is_business and user.profile.payment_method == '1' \
                    and not Invoice.objects.filter(user=user, type='CreditCard', is_deleted=False).exists():
                message = 'Payment information is not verified. Please verify payment method by '\
                                        'filling PayPal or Credit/Debit card details.'
            elif is_business and user.profile.payment_method == '0' \
                    and not Invoice.objects.filter(user=user, type='PayPalAccount', is_deleted=False).exists():
                message = 'Payment information is not verified. Please verify payment method by '\
                                        'filling PayPal or Credit/Debit card details.'
        else:
            message = "Please complete profile detail!"
            result.update(redirect_to='home')
    except Exception as exc:
        message = "Please complete profile detail!"
        result.update(error=True)
    result.update(message=message)
    return result

def register_type_required(func):
    """
     User registration type is required to fill profile data!
    """
    @wraps(func, assigned=available_attrs(func))
    def inner(request, *args, **kwargs):
        if request.user.is_authenticated():
            try:
                user = request.user
                if not user.groups.filter(name__in=[settings.GENERAL_USER,
                                                    settings.BUSINESS_USER,
                                                    settings.SKIGIT_ADMIN]).exists():
                    return HttpResponseRedirect(reverse('manage-register-type'))
            except Exception as exc:
                return HttpResponseRedirect('/')
        return func(request, *args, **kwargs)
    return inner

def require_filled_profile(func):
    """
        Required field Profile page
    """

    @wraps(func, assigned=available_attrs(func))
    def inner(request, *args, **kwargs):
        if request.user.is_authenticated():
            try:
                user = request.user
                result = get_profile_status(user)
                message = result['message']
                if message:
                    messages.error(request, message)
                    return HttpResponseRedirect('/profile')
                if 'redirect_to' in result and result['redirect_to'] == 'home':
                    logout(request)
                    return HttpResponseRedirect('/')
                if 'error' in result:
                    return HttpResponseRedirect('/profile')
            except ObjectDoesNotExist:
                return HttpResponseRedirect('/profile')
        return func(request, *args, **kwargs)
    return inner


def notify_password_change(email):
    try:
        EmailTemplate.send(
                template_key="password_change",
                emails=email,
                context={"host_email": EMAIL_HOST_USER} # TODO: use email from db
            )
    except:
        msg = 'Exception'
    return ()

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

                if user.groups.filter(name=settings.BUSINESS_USER).exists():
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


def crop_center(pil_img, crop_width, crop_height):
    """

    :param pil_img:
    :param crop_width:
    :param crop_height:
    :return: Crop centered image
    """
    img_width, img_height = pil_img.size
    return pil_img.crop(((img_width - crop_width) // 2,
                         (img_height - crop_height) // 2,
                         (img_width + crop_width) // 2,
                         (img_height + crop_height) // 2))


def crop_max_square(pil_img):
    """

    :param pil_img:
    :return: Crop the square image
    """
    return crop_center(pil_img, min(pil_img.size), min(pil_img.size))


def mask_circle_transparent(pil_img, blur_radius, offset=0):
    """

    :param pil_img:
    :param blur_radius:
    :param offset:
    :return: The Masked image
    """
    offset = blur_radius * 2 + offset
    mask = Image.new("L", pil_img.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((offset, offset, pil_img.size[0] - offset, pil_img.size[1] - offset), fill=255)
    # If we want the transparent with blur effect, uncomment next one
    #mask = mask.filter(ImageFilter.GaussianBlur(blur_radius))

    result = pil_img.copy()
    result.putalpha(mask)
    return result


def create_share_thumbnails(skigit=None, back_image=None, business_image=None, company_logo_url=None):
    """

    :param skigit:
    :param back_image:
    :param business_image:
    :return:
    """

    try:
        quality_val = 100
        BUSINESS_LOGO_SET_SIZE = (100, 100)
        ORIGINAL_IMAGE_SIZE = (600, 600)
        # New Image Canvas Size of 800x470
        #canvas = Image.new("RGB", (480, 360), (255, 0, 0, 0))
        canvas = Image.new("RGB", (600, 600), (0, 0, 0, 0))
        # Get Files from base location
        image1 = urlopen(back_image)
        # Play back image url path '/skigit/images/play_back.png'
        image2 = open(settings.STATIC_ROOT + '/images/Skigit_Logo_Glow.png', "rb")
        # Open Images for edit Creating Image objects
        background = Image.open(image1)

        (X, Y) = canvas.size
        (X1, Y1) = background.size
        is_big_image = True if X1 > X or Y1 > Y else False

        if is_big_image:
            crop_box = crop_social_share_image((X1, Y1), crop_size=ORIGINAL_IMAGE_SIZE)
            background = background.crop(crop_box)
            (X1, Y1) = background.size

        X2 = 0 if X1 > X else int((X - X1) / 2)
        Y2 = 0 if Y1 > Y else int((Y - Y1) / 2)

        if business_image:
            image3 = urlopen(business_image)
            business_logo = Image.open(image3)

            business_logo = ImageOps.fit(business_logo, BUSINESS_LOGO_SET_SIZE, Image.ANTIALIAS)
            (lx, ly) = business_logo.size
            im_square = crop_max_square(business_logo).resize(BUSINESS_LOGO_SET_SIZE,
                                                              Image.ANTIALIAS)
            im_thumb = mask_circle_transparent(im_square, 4)
            if is_big_image:
                background.paste(business_logo, (X1 - lx - 10, Y1 - BUSINESS_LOGO_SET_SIZE[1] - 150), im_thumb)
            else:
                background.paste(business_logo, (X1 - lx, Y1 - BUSINESS_LOGO_SET_SIZE[1] - 30), im_thumb)
        background.thumbnail((600, 600), Image.ANTIALIAS)

        play_back = Image.open(image2)

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
        canvas.paste(play_back, (240, 250), play_back)

        new_image_name = '%s.png' % uuid.uuid4().hex.lower()
        new_full_path = settings.MEDIA_ROOT + 'video_thumbnails/%s' % new_image_name
        media_path = settings.MEDIA_URL + 'video_thumbnails/%s' % new_image_name
        image_url = None

        if not SocialShareThumbnail.objects.filter(video=skigit.skigit_id).exists():
            canvas.save(new_full_path, 'PNG', quality=quality_val)
            new_image = SocialShareThumbnail.objects.create(video=skigit.skigit_id, url=media_path)
            image_url = "{}?{}".format(new_image.url, datetime.now().timestamp())
        else:
            canvas.save(new_full_path, 'PNG', quality=quality_val)
            SocialShareThumbnail.objects.filter(video=skigit.skigit_id).update(url=media_path)
            new_image = SocialShareThumbnail.objects.get(video=skigit.skigit_id)
            image_url = "{}?{}".format(new_image.url, datetime.now().timestamp())
        return image_url
    except Exception as exc:
        logger.error("Thumbnail Image URL throws error: %s", exc)
        return None


def crop_social_share_image(image_size, crop_size):
    left = (image_size[0] - crop_size[0]) / 2
    top = (image_size[1] - crop_size[1]) / 2
    right = (image_size[0] + crop_size[0]) / 2
    bottom = (image_size[1] + crop_size[1]) / 2
    box = (left, top, right, bottom)
    return box


def age_calculator(birth_date):
    """
        Age Calculator.
    """
    age = (datetime.today().date() - birth_date).days/365
    return age


def get_related_users(current_user_id, skigit_user_id, *argv):
    """
        Returns the Relative Skigits on the basis of category,
         subcategory, gender, and Age.
    """
    user_list = []

    if Profile.objects.filter(user__id=current_user_id).exists():
        profile_dic = Profile.objects.get(user__id=current_user_id)
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


def get_client_token(user):
    '''

    :param user:
    :return: Get client token of the customer.
    '''

    if Invoice.objects.filter(user=user, type='CreditCard', is_deleted=False).exists():
        invoice_obj = Invoice.objects.filter(user=user, type='CreditCard', is_deleted=False).first()
        token = braintree.ClientToken.generate({'customer_id': invoice_obj.customer_id})
    elif Invoice.objects.filter(user=user, type='PayPalAccount', is_deleted=False).exists():
        invoice_obj = Invoice.objects.filter(user=user, type='CreditCard', is_deleted=False).first()
        token = braintree.ClientToken.generate({'customer_id': invoice_obj.customer_id})
    else:
        token = braintree.ClientToken.generate()
    return token

def client_token(request, user=None):
    """
        Generate a client Token for client!
    """
    user = user if user else request.user
    if not Invoice.objects.filter(user=user, type='CreditCard', is_deleted=False).exists():
        token = braintree.ClientToken.generate()
    else:
        invoice_obj = Invoice.objects.filter(user=user, type='CreditCard', is_deleted=False).first()
        token = braintree.ClientToken.generate({'customer_id': invoice_obj.customer_id})
    return token


def client_paypal_token(request, user=None):
    """
        Generate a client Token for client

    Args:
        request: requested data
    """
    user = user if user else request.user
    if not Invoice.objects.filter(user=user, type='PayPalAccount', is_deleted=False).exists():
        token = braintree.ClientToken.generate()
    else:
        invoice_obj = Invoice.objects.filter(user=user, type='PayPalAccount', is_deleted=False).first()
        token = braintree.ClientToken.generate({'customer_id': invoice_obj.customer_id})
    return token


def get_all_logged_in_users():
    """
        Logged in users list view
    """
    loggedin_users = [int(user.get('user_id', 0)) for user in get_active_users()]
    return loggedin_users


def get_video_share_url(request, skigit, company_logo_url):
    video_share_url = ""

    if skigit.business_logo and skigit.made_by:
        if skigit.business_logo.is_deleted is False:
            skigit_b_logo = get_thumbnail(skigit.business_logo.logo, '{}x{}'.format(skigit.business_logo.logo.width,
                                                                                    skigit.business_logo.logo.height), quality=100).url
            video_share_url = create_share_thumbnails(skigit, skigit.skigit_id.thumbnails.all()[0].url(),
                                                      request.build_absolute_uri(skigit_b_logo),
                                                      request.build_absolute_uri(company_logo_url))
        elif skigit.business_logo.is_deleted is True:
            u_profile = Profile.objects.get(user=skigit.made_by)
            if u_profile.logo_img.filter(is_deleted=False).all().count() > 0:
                blogo = u_profile.logo_img.filter(is_deleted=False).all()[0]
                skigit_b_logo = get_thumbnail(blogo.logo, '{}x{}'.format(blogo.logo.width,
                                                                         blogo.logo.height), quality=100).url
                video_share_url = create_share_thumbnails(skigit, skigit.skigit_id.thumbnails.all()[0].url(),
                                                          request.build_absolute_uri(skigit_b_logo),
                                                          request.build_absolute_uri(company_logo_url))
    else:
        video_share_url = create_share_thumbnails(skigit, skigit.skigit_id.thumbnails.all()[0].url())
    return video_share_url


def get_object_or_None(klass,
                       *ar,
                       **kw):
    '''
    Returns object if it exists or None.

    kclass may be Model, Manager, Object.
    '''
    queryset = _get_queryset(klass)
    try:
        return queryset.get(*ar,
                            **kw)
    except queryset.model.DoesNotExist:
        return None

class CustomIsAuthenticated(permissions.IsAuthenticated):
    """
        Custom authentication
    """

    def __init__(self):
        super(CustomIsAuthenticated, self).__init__()

    @property
    def message(self):
        return {'status': 'error',
                'message': 'Please login.'}

################### Use it in future to have permission based views in API #####################
class IsProfileCompleted(permissions.BasePermission):
    """
    Object-level permission to only allow owners of an object to edit it.
    Assumes the model instance has an `owner` attribute.
    """

    def __init__(self):
        super(IsProfileCompleted, self).__init__()
        self.error_message = ''

    def has_permission(self, request, view):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        is_filled = False

        if request.method in permissions.SAFE_METHODS:
            result = get_profile_status(request.user)
            is_filled = False if result['message'] else True
            self.error_message = result['message']

        return is_filled

    @property
    def message(self):
        return {'status': 'error',
                'message': self.error_message,
                'data': {'redirect_to': 'profile'}}


def custom_exception_handler(exc, context):
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response = exception_handler(exc, context)

    # Now add the HTTP status code to the response.
    if response is not None:
        #response.data['status_code'] = response.status_code
        if response.status_code not in [200, 201, 301]:
            message = 'Please login.'
            if 'detail' in response.data:
                message = response.data['detail']
            elif 'message' in response.data:
                message = response.data['message']
            result = {'status': 'error',
                      'message': message}
            response.data = result

    return response


def mobile_deep_link_data(request, url_name, view_kwargs):
    """
        Mobile deep link data.
        return [android_fallback_url, ios_fallback_url]
    """

    url_name_list = [
        "index", 
        "register_confirm", 
        "sperk_profile", 
        "acceptable_use_policy_view", 
        "skigit_data", 
        "share_deeplink_view",
        "user_profile_display",
        "password_reset_confirm"
    ]

    ios_fallback_url = ""
    
    if url_name in url_name_list:

        if(url_name == url_name_list[0]): # index
            # deeplink url =  http://www.skigit.com/referal?category=HOME
            android_url = {
                "category": "HOME"
            }
        elif(url_name == url_name_list[1]): # register_confirm
            # deeplink url =  http://www.skigit.com/referal?category=HOME
            activation_key = view_kwargs.get("activation_key")
            android_url = {
                "category": "REGISTER_CONFIRM",
                "contentid": activation_key
            }
        elif(url_name == url_name_list[2]): # sperk_profile
            # deeplink url =  http://www.skigit.com/referal?category=SPERK&contentid={{user}}
            user = view_kwargs.get("user")
            android_url = {
                "category": "SPERK",
                "contentid": user
            }
        elif(url_name == url_name_list[3]): # acceptable_use_policy_view
            # deeplink url =  http://www.skigit.com/referal?category=ABOUTUS&contentid=acceptable-use-policy
            android_url = {
                "category": "ABOUTUS",
                "contentid": "acceptable-use-policy"
            }
        elif(url_name == url_name_list[4]): # skigit_data
            # deeplink url =  http://www.skigit.com/referal?category=SKIGIT&contentid={{skigit_id}}
            skigit_id = view_kwargs.get("pk")
            android_url = {
                "category": "SKIGIT",
                "contentid": skigit_id
            }
        elif(url_name == url_name_list[5]): # share_deeplink_view
            # deeplink url =  http://www.skigit.com/referal?category={{category}}&contentid={{contentid}}
            category = request.GET.get("category", "SKIGIT")
            contentid = request.GET.get("contentid")
            android_url = {
                "category": category,
                "contentid": contentid
            }
            if(contentid is None):
                android_url["category"] = "HOME"
                del android_url['contentid']
        elif(url_name == url_name_list[6]): # user_profile_display
            # deeplink url = http://www.skigit.com/referal?category=USER&contentid={{user_id}}
            userstring = view_kwargs.get("username")
            android_url = {
                "category": "HOME"
            }
            if userstring is not None:
                try:
                    # get user info
                    user = User.objects.get(username=userstring)
                    android_url = {
                        "category": "USER",
                        "contentid": user.id
                    }
                except ObjectDoesNotExist:
                    pass
        elif (url_name == url_name_list[7]):  #
            uid = view_kwargs.get("uidb64")
            token = view_kwargs.get("token")
            android_url = {
                "category": "PASSWORD_RESET_CONFIRM",
                "contentid": uid,
                "token": token
            }

        # for ios

        if (url_name == url_name_list[7]):  #
            uid = view_kwargs.get("uidb64")
            token = view_kwargs.get("token")
            ios_fallback_url = {
                "category": "PASSWORD_RESET_CONFIRM",
                "contentid": uid,
                "token": token
            }
                
        """
            return app fallback_url
        """
        if "category" in android_url:
            android_fallback_url = settings.ANDROID_APP_PATH_PREFIX + urlencode(android_url)
            
            if ios_fallback_url != "":
                ios_fallback_url = settings.ANDROID_APP_PATH_PREFIX + urlencode(ios_fallback_url)

            return [
                android_fallback_url, 
                ios_fallback_url
            ]

    return


def check_url_realtime(url):
    '''

    :param url:
    :return: Check the url in realtime!
    '''

    url_valid = False

    try:
        res = requests.get(url)
        if isinstance(res.status_code, int):
            url_valid = True
    except Exception as exc:
        url_valid = False
    return url_valid


def check_valid_url(url):
    '''
        Get the url status!
    '''

    url_valid = False
    url_pattern_compile = re.compile(
        r'(https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|www\.[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9]+\.[^\s]{2,}|www\.[a-zA-Z0-9]+\.[^\s]{2,})?$')
    if url and not url.startswith('http'):
        url = "http://{}".format(url)
    try:
        if url_pattern_compile.search(url):
            url_valid = check_url_realtime(url)
            if not url_valid:
                url = "http://{}".format(url.split('https://', 1)[1]) if url.startswith(
                    'https://') else "https://{}".format(url.split('http://', 1)[1])
                url_valid = check_url_realtime(url)
    except Exception:
        url_valid = False
    return url_valid


def register_confirm(activation_key):
    """

    :param activation_key:
    :return: activation key!
    The user activation by using the activation_key!
    """

    result = {}

    try:
        user_profile = Profile.objects.get(activation_key=activation_key)
    except ObjectDoesNotExist:
        result.update(status='error',
                      message='Invalid Account Activation Link.',
                      redirect_to='/')
        return result
    if user_profile:
        if FriendInvitation.objects.filter(to_user_email=user_profile.user.email).exists():
            invite_obj = FriendInvitation.objects.filter(to_user_email=user_profile.user.email).order_by('-id')[0]
            friend = Friend()
            friend.to_user = user_profile.user
            friend.from_user = invite_obj.from_user
            friend.status = "1"
            FriendInvitation.objects.filter(to_user_email=user_profile.user.email).update(status='1',
                                                                                          is_member=True)
            friend.save()

        user_profile.activation_key = None
        user_profile.save()
        user = user_profile.user
        user.is_active = True
        user.save()
        result.update(status='success',
                      message='Account activated successfully. Please login with your credentials.',
                      redirect_to='/login')
        return result
    else:
        result.update(status='error',
                      message='Invalid account activation link. User account not found',
                      redirect_to='/')
        return result

def generateTokenFromCode(provider, code):
    print('inside generateTokenFromCode')
    logger.info("inside generateTokenFromCode" )

    app = SocialApp.objects.get(provider=provider)
    response = requests.post('https://api.instagram.com/oauth/access_token', data={
        "client_id": app.client_id,
        "client_secret": app.secret,
        "code":code,
        "grant_type":"authorization_code",
        "redirect_uri":"{}/accounts/instagram/login/callback/".format(settings.WWW_HOST)
    })
    
    logger.info("before response decode", extra=response)

    response = json.loads(response.content.decode('utf-8'))

    logger.info("after response decode", extra=response)

    if 'access_token' in response:
        return response['access_token']
    else:
        return False


def trigger_send_email(email_template_key, to_email, context):
    """

    Sends the email based on the params!

    :param email_template_key: email tempalte name
    :param to_email: receiver_address in a list
    :param context: dynamic values for the email attributes
    """

    EmailTemplate.send(
        template_key=email_template_key,
        emails=to_email,
        context=context
    )

def deleteDisabled(vdo_detail_obj):
    from django.utils import timezone
    if vdo_detail_obj.made_by and vdo_detail_obj.business_logo is not None and vdo_detail_obj.business_logo.id \
    and vdo_detail_obj.receive_donate_sperk and \
    (vdo_detail_obj.published_at is None or (timezone.now() - vdo_detail_obj.published_at).days <= 30):
        us_profile = Profile.objects.get(user__id=vdo_detail_obj.made_by.id)
        if (us_profile.incentive == 1 and
                us_profile.logo_img.filter(is_deleted=False).exists()):
            return True
    return False