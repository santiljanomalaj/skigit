import random
import json
import hashlib
from datetime import datetime, timedelta
from django.conf import settings
from django.contrib import messages
from django.core.cache import cache
from django.http import JsonResponse
from django.shortcuts import render
from django.contrib.auth.models import User, Group
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.views import password_reset, password_reset_confirm
from django.core.urlresolvers import reverse
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.views.generic import TemplateView
from django.utils.decorators import method_decorator
from itertools import chain
from heapq import merge
from sorl.thumbnail import get_thumbnail
from django.template.context_processors import csrf

from rest_framework import permissions, viewsets
from rest_framework.response import Response
from rest_framework import status, views

from core.emails import send_email
from core.utils import is_user_general, is_user_business, client_paypal_token, client_token
from core.utils import payment_required, require_filled_profile
from friends.models import Friend, Embed, FriendInvitation
from friends.views import get_all_logged_in_users
from invoices.models import Invoice
from skigit.models import VideoDetail, Like
from skigit.serializer import VideoDetailSerializer
from social.models import Share
from user.models import Profile, ProfileUrl
from user.forms import RegistrationForm, UserForm, ProfileForm, BusinessUserProfileForm
from user.serializers import UserSerializer


@method_decorator(login_required(login_url='/'), name='dispatch')
@method_decorator(payment_required, name='dispatch')
@method_decorator(require_filled_profile, name='dispatch')
class UserProfileDisplay(TemplateView):
    def get(self, request, username):
        context = {}
        try:
            request_user = User.objects.get(username=username, is_active=True)
        except ObjectDoesNotExist:
            messages.error(request, 'Sorry, Your Request User Not Found.')
            return HttpResponseRedirect('/')  # HttpResponseRedirect
        busniess_logo = []
        like_dict = []
        friend_list = []
        ski_share_list = []
        company_url = None
        if Profile.objects.filter(user=request_user).exists():
            request_user_profile = Profile.objects.get(user=request_user)
            extra_profile_img = request_user_profile.extra_profile_img.all()
            extra_profile_img_url = [get_thumbnail(profile_img.profile_img, '300x120', quality=99, format='PNG').url
                                     for profile_img in extra_profile_img]

        if request_user.is_superuser or (
                    request_user.is_staff and is_user_general(request_user)) or is_user_general(request_user):
            user_template = 'profile/general_user_profile.html'
        elif request_user.groups.all()[0].name == settings.BUSINESS_USER:
            user_template = 'profile/business_user_profile.html'
        else:
            messages.error(request,
                           'Sorry, Your Request User Account Group Type Not Found.')
            return HttpResponseRedirect('/')

        if request.user.is_authenticated():
            user = request.user
            if is_user_business(request_user):
                for bb_logo in request_user_profile.logo_img.filter(is_deleted=False).all():
                    bb_logo.img_id = bb_logo.id
                    bb_logo.l_img = get_thumbnail(bb_logo.logo, '300x120', quality=99, format='PNG').url
                    busniess_logo.append(bb_logo)
                    company_url = ProfileUrl.objects.filter(user=request_user_profile.user)
                context.update({'company_url': company_url})

            user_profile = Profile.objects.get(user=request_user)

            if Embed.objects.filter(to_user=request_user_profile.user,
                                    is_embed=True).exists():
                embed_skigit_list = Embed.objects.filter(
                    to_user=request_user_profile.user,
                    is_embed=True).values_list('skigit_id', flat=True)

                if request.user.is_authenticated():
                    if Friend.objects.filter(Q(to_user=request.user.id) | Q(from_user=request.user.id),
                                             status=1).exists():
                        f_list = Friend.objects.filter(Q(to_user=request.user.id) | Q(from_user=request.user.id),
                                                       status=1)
                        from_user_list = f_list.exclude(from_user=request.user.id).values_list('from_user',
                                                                                               flat=True).distinct()
                        to_user_list = f_list.exclude(to_user=request.user.id).values_list('to_user',
                                                                                           flat=True).distinct()
                        fr_list = list(merge(from_user_list, to_user_list))
                        friends_detail = Profile.objects.filter(user__id__in=fr_list).order_by('user__username')
                        for friends in friends_detail:
                            if friends.profile_img:
                                l_img = get_thumbnail(friends.profile_img, '35x35', quality=99, format='PNG').url
                            else:
                                l_img = '/static/skigit/detube/images/noimage_user.jpg'
                            friend_list.append({'uid': friends.user.id, 'username': friends.user.username,
                                                'name': friends.user.get_full_name(), 'image': l_img})
                    video_likes = Like.objects.filter(user_id=request.user.id, status=True)
                    for likes in video_likes:
                        like_dict.append(likes.skigit_id)
                vid = VideoDetail.objects.select_related('skigit_id').filter(skigit_id__id__in=embed_skigit_list,
                                                                             status=1)
                serializer = VideoDetailSerializer(vid, many=True)
                for vid_data in vid:
                    sharObj = Share.objects.filter(skigit_id=vid_data,
                                                   is_active=True,
                                                   user=request_user_profile.user).order_by(
                        'to_user', '-pk').distinct('to_user')
                    for sh in sharObj:
                        ski_share_list.append(
                            {'share_date': sh.created_date, 'username': sh.to_user.username,
                             'vid': sh.skigit_id_id})
                context.update({'video_detail': serializer.data,
                                'video_likes': like_dict,
                                'friend_list': friend_list,
                                'order_value': '1',
                                'togal_val': '1',
                                'skigit_list': ski_share_list,
                                'users': get_all_logged_in_users()})
            context.update({'user': user, 'user_profile': user_profile})
            context.update({
                'request_user': request_user,
                'request_user_profile': request_user_profile,
                'extra_profile_img_url': extra_profile_img_url,
                'all_logo_url': busniess_logo,

            })
            return render(request, user_template, context)

        else:
            context.update({
                'request_user': request_user,
                'request_user_profile': request_user_profile,
            })

        return render(request, user_template, context)


class LoginViewAPI(views.APIView):
    def post(self, request, format=None):
        import pdb;pdb.set_trace()
        data = json.loads(request.body.decode())

        email = data.get('email', None)
        password = data.get('password', None)

        account = authenticate(email=email, password=password)

        if account is not None:
            if account.is_active:
                login(request, account)

                serialized = UserSerializer(account)

                return Response(serialized.data)
            else:
                return Response({
                    'status': 'Unauthorized',
                    'message': 'This account has been disabled.'
                }, status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response({
                'status': 'Unauthorized',
                'message': 'Username/password combination invalid.'
            }, status=status.HTTP_401_UNAUTHORIZED)


class LoginView(TemplateView):

    def get(self, request):
        # import pdb;pdb.set_trace()
        return render(request, 'user/login.html', {})

    def post(self, request, extra_context=None):
        username = request.POST.get('email', None)
        password = request.POST.get('password', None)
        if User.objects.filter(email=username).exists():
            user_name = User.objects.get(email=username).username
            user = authenticate(username=user_name, password=password)
        else:
            user = None
        if user is not None:
            if user.is_active:
                request.session['user_id'] = user.id
                login(request, user)

                return JsonResponse({
                    'is_success': True,
                    'status': 'Authorized',
                    'message': 'Your login was successful!'
                })
            else:
                return JsonResponse({
                    'is_success': False,
                    'status': 'Unauthorized',
                    'message': 'Your account is inactivate. Please activate first then try to login.'
                })
        else:
            return JsonResponse({
                'is_success': False,
                'status': 'Unauthorized',
                'message': 'Your username and/or password are incorrect. Please try again.'
            })


class RegisterType(TemplateView):
    def get(self, request):
        context = {}
        if request.user.is_authenticated():
            return HttpResponseRedirect('/')
        else:
            context.update(csrf(request))
            return render(request, 'registration/registration_type.html', context)

    def post(self, request):
        context = {}
        if 'register_type' in request.POST:
            form = request.POST.get('acc_type', None)
            if form is not None and form == 'general':
                form = RegistrationForm()
                context.update({'form': form})
                return render(request,
                              'registration/register_as_general_user.html',
                              context
                              )
            elif form is not None and form == 'business':
                form = RegistrationForm()
                context.update({'form': form})
                return render(request,
                              'registration/register_as_business_user.html', context
                              )
            else:
                context.update(csrf(request))
                return render(request,
                              'registration/registration_type.html', context
                              )
        elif 'register_as_general_user' in request.POST:
            form = RegistrationForm(request.POST)
            if form.is_valid():
                user = User.objects.create_user(
                    username=form.cleaned_data['username'],
                    password=form.cleaned_data['password1'],
                    email=form.cleaned_data['email'],
                )

                user.is_active = False
                user.save()
                g = Group.objects.get(name=str(settings.GENERAL_USER))
                g.user_set.add(user)

                username = form.cleaned_data['username']
                email = form.cleaned_data['email']
                random_string = str(random.random()).encode('utf8')
                salt = hashlib.sha1(random_string).hexdigest()[:5]
                salted = (salt + email).encode('utf8')
                activation_key = hashlib.sha1(salted).hexdigest()
                key_expires = datetime.today() + timedelta(6)

                # Save The Hash to user Profile
                new_profile = Profile(user=user, activation_key=activation_key, key_expires=key_expires)
                new_profile.save()

                email_subject = 'Welcome to Skigit!'
                confirm_path = "/register/confirm/%s" % activation_key
                confirm = request.build_absolute_uri(confirm_path)
                email_body = "<table style='width:100%;' cellpadding='0' cellspacing='0'>" \
                             "<tr><td style='text-align:center;'><h3 style='color:#0386B8; " \
                             "margin-bottom:0;font-family: " + "Proza Libre" + ", sans-serif;'>" \
                             "Welcome to Skigit!</h3></td></tr>" \
                             "<tr><td style='text-align:center;'><h5 style='color:#1C913F; margin-top:10px; " \
                             "font-family: " + "Proza Libre" + ", sans-serif;'>" \
                             "We're so glad you joined us!</h5></td></tr>" \
                             "<tr><td style='color:#222;'><p style='text-align:justify;'>" \
                             "Please click the link below so that we can confirm your email address. Without verification, you won't be able to establish an accounts and create Skigits.</p>" \
                             "<p>Thank you,<br/>Skigit</p></td></tr>" \
                             "<tr><td style='text-align:center;'><a href='" + confirm + "' " \
                             "style='text-decoration:none; color:#0386B8;margin: 20px auto;display: " \
                             "table;font-weight: 700;font-size: 15px; font-family: " + "Proza Libre" + ", " \
                             "sans-serif;'> Click to verify your Email </a></td></tr>" \
                             "<tr><td style='text-align:center;width:165px;'><img " \
                             "src='http://skigit.com/static/skigit/images/shair.png' " \
                             "style='width:165px;'/></td></tr>" \
                             "</table>"
                header_text = ""
                send_email(email_subject, email_body, email, header_text, settings.EMAIL_HOST_USER)

                context.update({'user': user})
                return render(request,
                              'registration/register_success.html',
                              context
                              )
            else:
                context.update({'form': form})
                return render(request,
                              'registration/register_as_general_user.html',
                              context
                              )
        elif 'register_as_business_user' in request.POST:
            form = RegistrationForm(request.POST)
            if form.is_valid():
                user = User.objects.create_user(
                    username=form.cleaned_data['username'],
                    password=form.cleaned_data['password1'],
                    email=form.cleaned_data['email'],
                )
                user.is_active = False
                user.save()
                g = Group.objects.get(name=settings.BUSINESS_USER)
                g.user_set.add(user)

                username = form.cleaned_data['username']
                email = form.cleaned_data['email']
                random_string = str(random.random()).encode('utf8')
                salt = hashlib.sha1(random_string).hexdigest()[:5]
                salted = (salt + email).encode('utf8')
                activation_key = hashlib.sha1(salted).hexdigest()
                key_expires = datetime.today() + timedelta(6)

                # Save The Hash to user Profile
                new_profile = Profile(user=user, activation_key=activation_key,
                                      key_expires=key_expires)
                new_profile.save()

                email_subject = 'Welcome to Skigit | Skigit'
                confirm_path = "/register/confirm/%s" % activation_key
                confirm = request.build_absolute_uri(confirm_path)
                # TODO: move the email to some template file
                email_body = "<table style='width:100%;' cellpadding='0' cellspacing='0'>" \
                             "<tr><td style='text-align:center;'><h3 style='color:#0386B8; " \
                             "margin-bottom:0;font-family: " + "Proza Libre" + ", sans-serif;'>" \
                                                                                                                                            "Welcome to Skigit!</h3></td></tr>" \
                                                                                                                                            "<tr><td style='text-align:center;'><h5 style='color:#1C913F; margin-top:10px; font-family: " + "Proza Libre" + ", sans-serif;'>" \
                                                                                                                                                                                                                                                            "We're so glad you joined us!</h5></td></tr>" \
                                                                                                                                                                                                                                                            "<tr><td style='color: #222;'><p style='text-align:justify;'>" \
                                                                                                                                                                                                                                                            "Please click the link below so that we can confirm your email address. Without verification, you won't be able to establish an accounts and create Skigits.</p>" \
                                                                                                                                                                                                                                                            "<p>Thank you,<br/>Skigit</p></td></tr>" \
                                                                                                                                                                                                                                                            "<tr><td style='text-align:center;'><a href='" + confirm + "' style='text-decoration:none;color:#0386B8;margin: 20px auto;display: table;font-weight: 700;font-size: 15px; font-family: " + "Proza Libre" + ", sans-serif;'> Click to verify your Email </a></td></tr>" \
                                                                                                                                                                                                                                                                                                                                                                                                                                                                        "<tr><td style='text-align:center;width:165px;'><img src='http://skigit.com/static/skigit/images/shair.png' style='width:165px;'/></td></tr>" \
                                                                                                                                                                                                                                                                                                                                                                                                                                                                        "</table>"
                email_body = email_body
                header_text = ""
                send_email(email_subject, email_body, email, header_text, settings.EMAIL_HOST_USER)

                context.update({'user': user})

                return render(request,
                              'registration/register_success.html',
                              context
                              )
            else:
                context.update({'form': form})
                return render(request,
                              'registration/register_as_business_user.html',
                              context
                              )
        else:
            context.update(csrf(request))
            return render(request,
                          'registration/registration_type.html',
                          context
                          )


class RegisterConfirm(TemplateView):

    def get(self, request, activation_key=None):
        context = {}

        if request.user.is_authenticated():
            HttpResponseRedirect('/')

        try:
            user_profile = Profile.objects.get(activation_key=activation_key)
        except ObjectDoesNotExist:
            messages.error(request, 'Invalid Account Activation Link.')
            return HttpResponseRedirect('/')
        if user_profile:
            if FriendInvitation.objects.filter(to_user_email=user_profile.user.email).exists():
                invite_obj = FriendInvitation.objects.get(to_user_email=user_profile.user.email)
                friend = Friend()
                friend.to_user = user_profile.user
                friend.from_user = invite_obj.from_user
                friend.status = "1"
                FriendInvitation.objects.filter(to_user_email=user_profile.user.email).update(status='1', is_member=True)
                friend.save()

            user_profile.activation_key = None
            user_profile.save()
            user = user_profile.user
            user.is_active = True
            user.save()
            confirm_path = '/admin/auth/user/%s/' % user.id
            confirm = request.build_absolute_uri(confirm_path)
            subject = "Account Verification Task"
            message = "<table style='width:100%;' cellpadding='0' cellspacing='0'>"\
                             "<tr><td style='text-align:center;'><h3 style='color:#d22b2b;' margin-bottom:0;font-family: "+"Proza Libre"+", sans-serif;'>"\
                             "Account Verification Task - Admin </h3></td></tr>"\
                             "<tr><td><p style='text-align:justify;font-family: "+"Proza Libre"+", sans-serif;'>"\
                             "<span style='color:#1C913F;font-family: "+"Proza Libre"+", sans-serif;'>"+user.username+"</span>has joined skigit. please verify account information by clicking the link below.</p>"\
                             "<p><br/></p></td></tr>"\
                             "<tr><td style='text-align:center;'><a href='"+confirm+"' style='text-decoration:none;color:#0386B8;margin: 20px auto;display: table;font-family: "+"Proza Libre"+", sans-serif;'>"\
                             "User Account Verification </a></td></tr>"\
                             "<tr><td style='text-align:center; width:165px;'><img src='http://skigit.com/static/skigit/images/shair.png' style='width:200px;'/></td></tr>"\
                             "</table>"
            admin_user = User.objects.filter(is_superuser=True).first()

            messages.success(request, 'Account activated successfully. '
                                      'Please login with your credentials')
            return HttpResponseRedirect('/loginpopup')
        else:
            messages.error(request, 'Invalid account activation link. '
                                    'User account not found')
            return HttpResponseRedirect('/')


class Reset(TemplateView):

    def get(self, request):
        return password_reset(
            request, template_name='registration/password_reset_form.html',
            html_email_template_name='registration/password_reset_email.html',
            subject_template_name='registration/recovery_email_subject.txt',
            post_reset_redirect=reverse('reset_success')
    )


class ResetConfirm(TemplateView):

    def get(self, request, uidb64=None, token=None):
        return password_reset_confirm(
            request, template_name='registration/password_reset_confirm.html',
            uidb64=uidb64, token=token, post_reset_redirect=reverse('reset_done'))


@method_decorator(login_required(login_url='/'), name="dispatch")
class UserProfile(TemplateView):
    """ User Profile View
    """
    def get(self, request):
        context = {}
        user = request.user

        try:
            is_business = is_user_business(user)
            context['is_business'] = is_user_business(user)
        except:
            is_business = False
            context['is_business'] = False
        try:
            is_general = is_user_general(user)
            context['is_general'] = is_user_general(user)
        except:
            is_general = False
            context['is_general'] = False

        context['backend_name'] = cache.get('backend')
        context['backend_name'] = cache.get('backend')
        Profile.objects.get_or_create(user=user)
        if is_business:
            if Invoice.objects.filter(user=request.user, type='CreditCard', is_deleted=False).exists():
                inv_obj = Invoice.objects.filter(user=request.user, type='CreditCard', is_deleted=False)
                context['card_found'] = True
                context['card'] = str('%06d*****%04d') % (int(inv_obj[0].first_6), int(inv_obj[0].last_4))
                context['invoice_data'] = inv_obj
            else:
                context['card_found'] = False
            if Invoice.objects.filter(user=request.user, type='PayPalAccount', is_deleted=False).exists():
                paypal_obj = Invoice.objects.filter(user=request.user, type='PayPalAccount', is_deleted=False)
                context['pay_pal_account_found'] = True
                context['paypal_invoice_data'] = paypal_obj
            else:
                context['pay_pal_account_found'] = False
            cc_token = client_token(request)
            pay_pal_token = client_paypal_token(request)
            context['client_token'] = cc_token
            context['pay_pal_client_token'] = pay_pal_token
            fields = [
                user.username,
                user.first_name,
                user.last_name,
                user.email,
                user.profile.birthdate,
                user.profile.language,
                user.profile.country,
                user.profile.state,
                user.profile.city,
                user.profile.zip_code
            ]
            if not all(fields):
                messages.error(request,
                               'Please Fill The Complete Profile Detail')
            elif not user.profile.profile_img and is_business:
                messages.error(request,
                               'Please Upload Your Profile Picture')
            elif not user.profile.logo_img.filter(is_deleted=False).all() and is_business:
                messages.error(request, 'Please Upload Your Business Logo')

            elif is_business and not Invoice.objects.filter(user=request.user, type='CreditCard',
                                                            is_deleted=False).exists() and not \
                    Invoice.objects.filter(user=request.user, type='PayPalAccount',
                                           is_deleted=False).exists() and is_business:
                messages.error(request, 'Payment information is not verified. Please verify payment method by '
                                        'filling PayPal or Credit/Debit card details.')
            elif is_business and request.user.profile.payment_method == '1' \
                    and not Invoice.objects.filter(user=request.user, type='CreditCard',
                                                   is_deleted=False).exists() and is_business:
                messages.error(request, 'Payment information is not verified. Please verify payment method by '
                                        'filling PayPal or Credit/Debit card details.')
            elif is_business and request.user.profile.payment_method == '0' \
                    and not Invoice.objects.filter(user=request.user, type='PayPalAccount',
                                                   is_deleted=False).exists() and is_business:
                messages.error(request, 'Payment information is not verified. Please verify payment method by '
                                        'filling PayPal or Credit/Debit card details.')
            form1 = UserForm(instance=user)
            form2 = BusinessUserProfileForm(instance=user.profile)

            profile_url = ProfileUrl.objects.get_or_create(user=user)
            profile_url = profile_url[0]

            disc1 = profile_url.disc1
            url1 = profile_url.url1
            disc2 = profile_url.disc2
            url2 = profile_url.url2
            disc3 = profile_url.disc3
            url3 = profile_url.url3
            disc4 = profile_url.disc4
            url4 = profile_url.url4
            disc5 = profile_url.disc5
            url5 = profile_url.url5
        elif user.is_superuser or (user.is_staff and is_general) or is_general:
            form1 = UserForm(instance=user)
            form2 = ProfileForm(instance=user.profile)
        else:
            logout(request)
            return HttpResponseRedirect('/')

        context['backend_name'] = cache.get('backend')
        user_profile = Profile.objects.get(user=user)

        context.update(csrf(request))
        context['form1'] = form1
        context['form'] = form2
        context['user'] = user
        context['user_profile'] = user_profile
        context['is_business'] = is_business
        if user_profile.profile_img:
            profile_url = request.build_absolute_uri(user_profile.profile_img.url)
            context['profile_image'] = profile_url

        if is_business:
            context['disc1'] = disc1
            context['url1'] = url1
            context['disc2'] = disc2
            context['url2'] = url2
            context['disc3'] = disc3
            context['url3'] = url3
            context['disc4'] = disc4
            context['url4'] = url4
            context['disc5'] = disc5
            context['url5'] = url5

        return render(request, 'profile/basic_profile.html', context)

    def post(self, request):
        context = {}
        user = request.user

        try:
            is_business = is_user_business(user)
            context['is_business'] = is_user_business(user)
        except:
            is_business = False
            context['is_business'] = False
        try:
            is_general = is_user_general(user)
            context['is_general'] = is_user_general(user)
        except:
            is_general = False
            context['is_general'] = False
        context['backend_name'] = cache.get('backend')
        if is_business:
            form1 = UserForm(request.POST, instance=request.user)
            form2 = BusinessUserProfileForm(request.POST, request.FILES, instance=request.user.profile)
            disc1 = request.POST.get('disc1', None)
            url1 = request.POST.get('url1', None)
            disc2 = request.POST.get('disc2', None)
            url2 = request.POST.get('url2', None)
            disc3 = request.POST.get('disc3', None)
            url3 = request.POST.get('url3', None)
            disc4 = request.POST.get('disc4', None)
            url4 = request.POST.get('url4', None)
            disc5 = request.POST.get('disc5', None)
            url5 = request.POST.get('url5', None)
        elif user.is_superuser or (user.is_staff and is_general) or is_general:
            form1 = UserForm(request.POST, instance=request.user)
            form2 = ProfileForm(request.POST, request.FILES, instance=request.user.profile)

        else:
            logout(request)
            return HttpResponseRedirect('/')

        if form1.is_valid() and form2.is_valid():
            form1.save()
            form2.save()
            if is_business:
                profile_url = ProfileUrl.objects.get_or_create(user=user)
                profile_url = profile_url[0]
                profile_url.disc1 = disc1
                profile_url.url1 = url1
                profile_url.disc2 = disc2
                profile_url.url2 = url2
                profile_url.disc3 = disc3
                profile_url.url3 = url3
                profile_url.disc4 = disc4
                profile_url.url4 = url4
                profile_url.disc5 = disc5
                profile_url.url5 = url5
                profile_url.save()
                # result = create_customer(request, '789', '4012888888881881', '10/2017')

            if Profile.objects.filter(user=request.user.id, email_sent=False).exists():
                Profile.objects.filter(user=request.user.id).update(email_sent=True)
                confirm_path = '/admin/auth/user/%s/' % user.id
                confirm = request.build_absolute_uri(confirm_path)
                subject = "Account Verification Task"

                message = "<table style='width:100%;' cellpadding='0' cellspacing='0'>" \
                          "<tr><td style='text-align:center;'><h3 style='color:#d22b2b;' margin-bottom:0;font-family: " \
                          "" + "Proza Libre" + ", sans-serif;'>" \
                          "Account Verification Task - Admin </h3></td></tr>" \
                          "<tr><td><p style='text-align:justify;font-family: " + "Proza Libre" + ", sans-serif;'>" \
                          "<span style='color:#1C913F;font-family: " + "Proza Libre" + ", sans-serif;'>" + user.username + "</span> has joined skigit. please verify account information by clicking the link below.</p>" \
                          "<p><br/></p></td></tr>" \
                          "<tr><td style='text-align:center;'><a href='" + confirm + "' style='text-decoration:none;color:#0386B8;margin: 20px auto;display: table;font-weight: 700;font-size: 15px;font-family: " + "Proza Libre" + ", sans-serif;'>" \
                          " User Account Verification </a></td></tr>" \
                          "<tr><td style='text-align:center; width:168px;'><img src='http://skigit.com/static/skigit/images/shair.png' style='width:165px;'/></td></tr>" \
                          "</table>"
                admin_user = User.objects.filter(is_superuser=True).first()
                send_email(subject, message, settings.EMAIL_HOST_USER, '', settings.EMAIL_HOST_USER)
            user_profile = Profile.objects.get(user=request.user)
            # user_profile.get_online
            if (not user_profile.logo_img.filter(is_deleted=False).all()) and is_business:
                messages.error(request, 'Please Upload Your Business Logo')
            elif user_profile.logo_img.filter(is_deleted=False).all().count() > 5:
                messages.error(request, 'Max 5 Business Logo allowed.')
                for i in range(1, user_profile.logo_img.filter(is_deleted=False).all().count()):
                    if user_profile.logo_img.filter(is_deleted=False).all().count() > 5:
                        user_profile.logo_img.filter(is_deleted=False).all().last().delete()
            elif user_profile.extra_profile_img.all().count() > 5:
                messages.error(request, 'Max 5 Profile Images allowed.')
                for i in range(1, user_profile.extra_profile_img.all().count()):
                    if user_profile.extra_profile_img.all().count() > 5:
                        user_profile.extra_profile_img.all().last().delete()
            elif is_business and not Invoice.objects.filter(user=request.user, type='CreditCard',
                                                            is_deleted=False).exists() and not \
                    Invoice.objects.filter(user=request.user, type='PayPalAccount', is_deleted=False).exists():
                messages.error(request, 'Payment information is not verified. Please verify payment method by '
                                        'filling PayPal or Credit/Debit card details.')
            elif is_business and request.user.profile.payment_method == '1' \
                    and not Invoice.objects.filter(user=request.user, type='CreditCard', is_deleted=False).exists():
                messages.error(request, 'Payment information is not verified. Please verify payment method by '
                                        'filling PayPal or Credit/Debit card details.')
            elif is_business and request.user.profile.payment_method == '0' \
                    and not Invoice.objects.filter(user=request.user, type='PayPalAccount', is_deleted=False).exists():
                messages.error(request, 'Payment information is not verified. Please verify payment method by '
                                        'filling PayPal or Credit/Debit card details.')
            else:
                messages.success(request, 'Profile updated successfully!')

            if user.is_superuser or (user.is_staff and is_general) or is_general:
                form1 = UserForm(instance=user)
                form2 = ProfileForm(instance=user.profile)

            elif user.groups.all()[0].name == settings.BUSINESS_USER:
                form1 = UserForm(instance=user)
                form2 = BusinessUserProfileForm(instance=user.profile)
            else:
                logout(request)
                return HttpResponseRedirect('/')

        context['backend_name'] = cache.get('backend')
        user_profile = Profile.objects.get(user=user)

        context.update(csrf(request))
        context['form1'] = form1
        context['form'] = form2
        context['user'] = user
        context['user_profile'] = user_profile
        context['is_business'] = is_business
        if user_profile.profile_img:
            profile_url = request.build_absolute_uri(user_profile.profile_img.url)
            context['profile_image'] = profile_url

        if is_business:
            context['disc1'] = disc1
            context['url1'] = url1
            context['disc2'] = disc2
            context['url2'] = url2
            context['disc3'] = disc3
            context['url3'] = url3
            context['disc4'] = disc4
            context['url4'] = url4
            context['disc5'] = disc5
            context['url5'] = url5

        return render(request, 'profile/basic_profile.html', context)


class LogoutUser(TemplateView):

    def get(self, request, *args, **kwargs):
        logout(request)
        messages.info(request, 'You have successfully logged out')
        return render(request, 'user/logout.html', {'logout_message': 'You have successfully logged out'})