import random
from heapq import merge
from itertools import chain
from user.models import Profile

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import logout, login, authenticate
from django.contrib.auth.models import Group, User
from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import render, render_to_response
from django.template.context import RequestContext
from django.template.context_processors import csrf
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.generic import TemplateView
from el_pagination.decorators import page_template
from social.models import Share
from sorl.thumbnail import get_thumbnail

from core.utils import is_user_general
from friends.models import Friend
from friends.views import get_all_logged_in_users
from invoices.models import Invoice
from skigit.models import Like, VideoDetail


@method_decorator(ensure_csrf_cookie, name="dispatch")
class SkigitBaseView(TemplateView):

    description=""

    def get_context_data(self, **kwargs):
        from meta.views import Meta
        meta = Meta()
        setattr(meta, 'use_googleplus', True)
        setattr(meta, 'use_og', True)
        setattr(meta, 'use_twitter', True)
        setattr(meta, 'use_facebook', True)
        setattr(meta, 'description', self.description)
        context = super(SkigitBaseView, self).get_context_data(**kwargs)
        context['meta'] = meta
        return context


# class Home(SkigitBaseView):
#     """ view for home
#     """
#
#     def get(self, request, extra_context=None):
#         id = request.GET.get('id', None)
#         context = {}
#         like_dict = []
#         share_dict = []
#         plug_dict = []
#         vid_random = None
#         # random video
#         max_id = VideoDetail.objects.filter(status=1, is_active=True).order_by('-id')[0].id
#         vid = True
#         while vid is True:
#             random_id = random.randint(1, max_id + 1)
#             vid_random = VideoDetail.objects.filter(id__gte=random_id, status=1, is_active=True)
#
#             if vid_random:
#                 vid_random = vid_random[0]
#                 vid = False
#
#         # vid_latest_uploaded = VideoDetail.objects.select_related('skigit_id')
#         if id:
#             if VideoDetail.objects.filter(id=int(id), status=1, is_active=True).exists():
#                 vid_latest_uploaded1 = VideoDetail.objects.filter(id=int(id), status=1, is_active=True).order_by(
#                     '-updated_date')
#                 vid_latest_uploaded = VideoDetail.objects.exclude(id=int(id)).filter(status=1, is_active=True).order_by(
#                     '-updated_date')
#                 vid_latest_uploaded = list(chain(vid_latest_uploaded1, vid_latest_uploaded))
#             else:
#                 vid_latest_uploaded = vid_random
#         else:
#             vid_latest_uploaded = vid_random
#
#         videos_latest = VideoDetail.objects.select_related('skigit_id')
#         if id:
#             if videos_latest.filter(id=int(id), status=1, is_active=True).exists():
#                 videos_latest1 = videos_latest.filter(id=int(id), status=1, is_active=True).order_by('-updated_date')
#                 videos_latest = videos_latest.exclude(id=int(id)).filter(status=1, is_active=True).order_by(
#                     '-updated_date')
#                 videos_latest = list(chain(videos_latest1, videos_latest))
#
#             else:
#                 videos_latest = videos_latest.filter(status=1, is_active=True).order_by('-updated_date')
#         else:
#             videos_latest = videos_latest.filter(status=1, is_active=True).order_by('-updated_date')
#
#         profile_dic = []
#         for vid_profile in videos_latest:
#
#             video_count = Like.objects.filter(skigit=vid_profile.skigit_id, status=True).count()
#             like_dict.append({'id': vid_profile.id, 'count': video_count})
#             video_share = Share.objects.filter(skigit_id=vid_profile, is_active=True).count()
#             share_dict.append({'id': vid_profile.id, 'count': video_share})
#             video_plug = VideoDetail.objects.filter(plugged_skigit=vid_profile.skigit_id, is_plugged=True,
#                                                     status=1).count()
#             plug_dict.append({'id': vid_profile.id, 'count': video_plug})
#             if vid_profile.made_by:
#                 us_profile = Profile.objects.get(user=vid_profile.made_by)
#                 if us_profile.logo_img.filter(is_deleted=False).all().count() > 0:
#                     us_profile.made_by = vid_profile.made_by.id
#                     us_profile.business_logo = us_profile.logo_img.filter(is_deleted=False).all()[0]
#                     profile_dic.append(us_profile)
#         profile_dic = list(set(profile_dic))
#         ski_share_list = []
#         for vid_data in videos_latest:
#             sharObj = Share.objects.filter(
#                 skigit_id=vid_data, is_active=True, user=request.user.id
#             ).order_by(
#                 'to_user',
#                 '-pk'
#             ).distinct(
#                 'to_user'
#             )
#             for sh in sharObj:
#                 ski_share_list.append(
#                     {'share_date': sh.created_date, 'username': sh.to_user.username, 'vid': sh.skigit_id_id})
#         video_likes = Like.objects.filter(user_id=request.user.id, status=1)
#         like_skigit = []
#         for likes in video_likes:
#             like_skigit.append(likes.skigit_id)
#
#         friend_list = []
#         if Friend.objects.filter(Q(to_user=request.user.id) | Q(from_user=request.user.id), status=1).exists():
#             f_list = Friend.objects.filter(Q(to_user=request.user.id) | Q(from_user=request.user.id), status=1)
#             from_user_list = f_list.exclude(from_user=request.user.id).values_list('from_user', flat=True).distinct()
#             to_user_list = f_list.exclude(to_user=request.user.id).values_list('to_user', flat=True).distinct()
#             fr_list = list(merge(from_user_list, to_user_list))
#             friends_detail = Profile.objects.filter(user__id__in=fr_list).order_by('user__username')
#
#             for friends in friends_detail:
#                 if friends.profile_img:
#                     l_img = get_thumbnail(friends.profile_img, '35x35', quality=99, format='PNG').url
#                 else:
#                     l_img = '/static/images/noimage_user.jpg'
#                 friend_list.append({'uid': friends.user.id, 'username': friends.user.username,
#                                     'name': friends.user.get_full_name(), 'image': l_img})
#         context.update({
#             'video_likes': like_skigit,
#             'like_count': like_dict,
#             'video_share': share_dict,
#             'video_plug': plug_dict,
#             'vid_latest_uploaded': vid_latest_uploaded,
#             'videos_latest': videos_latest,
#             'default_logo': profile_dic,
#             'friend_list': friend_list,
#             'skigit_list': ski_share_list,
#             'users': get_all_logged_in_users()
#         })
#
#         if request.user.is_authenticated():
#             try:
#                 user = User.objects.get(pk=request.user.id)
#                 user_profile = Profile.objects.get(user=user)
#
#                 if not user.groups.all():
#                     gen_obj = Group.objects.get_or_create(name="General User")
#                     user.groups.add(gen_obj[0])
#
#                 if user.is_staff and user.groups.all()[0].name == settings.SKIGIT_ADMIN:
#                     return HttpResponseRedirect("admin_tools/dashboard/skigit_admin")
#
#                 if user.is_superuser or (user.is_staff and is_user_general(user)) or is_user_general(user):
#                     fields = [
#                         user.username,
#                         user.first_name,
#                         user.last_name,
#                         user.email,
#                         user_profile.birthdate,
#                         user_profile.language,
#                         user_profile.country,
#                         user_profile.state,
#                         user_profile.city,
#                         user_profile.zip_code
#                     ]
#                     if not all(fields):
#                         messages.error(request,
#                                        'Please Fill The Complete Profile Detail')
#                         raise ObjectDoesNotExist
#                     elif not user_profile.profile_img:
#                         messages.error(request,
#                                        'Please Upload Your Profile Picture')
#                         raise ObjectDoesNotExist
#                 elif user.groups.all()[0].name == settings.BUSINESS_USER:
#                     fields = [
#                         user.username,
#                         user.first_name,
#                         user.last_name,
#                         user.email,
#                         user_profile.birthdate,
#                         user_profile.language,
#                         user_profile.country,
#                         user_profile.state,
#                         user_profile.city,
#                         user_profile.zip_code
#                     ]
#                     if not all(fields):
#                         messages.error(request,
#                                        'Please Fill The Complete Profile Detail')
#                         raise ObjectDoesNotExist
#                     elif not user_profile.profile_img:
#                         messages.error(request,
#                                        'Please Upload Your Profile Picture')
#                         raise ObjectDoesNotExist
#                     elif not user_profile.logo_img.filter(is_deleted=False).all():
#                         messages.error(request, 'Please Upload Your Business Logo')
#                         raise ObjectDoesNotExist
#                     elif not Invoice.objects.filter(user=request.user, type='CreditCard',
#                                                     is_deleted=False).exists() and not \
#                             Invoice.objects.filter(user=request.user, type='PayPalAccount', is_deleted=False).exists():
#                         messages.error(request, 'Payment information is not verified. Please verify payment method by '
#                                                 'filling PayPal or Credit/Debit card details.')
#                         raise ObjectDoesNotExist
#                     elif request.user.profile.payment_method == '1' \
#                             and not Invoice.objects.filter(user=request.user, type='CreditCard',
#                                                            is_deleted=False).exists():
#                         messages.error(request, 'Payment information is not verified. Please verify payment method by '
#                                                 'filling PayPal or Credit/Debit card details.')
#                         raise ObjectDoesNotExist
#                     elif request.user.profile.payment_method == '0' \
#                             and not Invoice.objects.filter(user=request.user, type='PayPalAccount',
#                                                            is_deleted=False).exists():
#                         messages.error(request, 'Payment information is not verified. Please verify payment method by '
#                                                 'filling PayPal or Credit/Debit card details.')
#                         raise ObjectDoesNotExist
#                 else:
#                     logout(request)
#                     return HttpResponseRedirect('/')
#
#             except ObjectDoesNotExist:
#                 return HttpResponseRedirect('/profile')
#
#             user_profile = Profile.objects.get(user=user)
#             context.update({'user': user, 'user_profile': user_profile})
#
#             if extra_context is not None:
#                 context.update(extra_context)
#             return render(request, 'index.html', context)
#         else:
#
#             if extra_context is not None:
#                 context.update(extra_context)
#             return render(request, 'index.html', context)


@page_template('includes/entry_index_page.html')
def index(request, template='index.html', extra_context=None):

    request.META['CSRF_COOKIE_USED'] = True
    id = request.GET.get('id', None)
    context = {'request': request}
    like_dict = []
    share_dict = []
    plug_dict = []
    vid_all = None
    vid_latest_uploaded = VideoDetail.objects.select_related('skigit_id')
    if id:
        if vid_latest_uploaded.filter(id=int(id), status=1, is_active=True).exists():
            vid_latest_uploaded1 = vid_latest_uploaded.filter(id=int(id), status=1, is_active=True).order_by('-updated_date')
            vid_latest_uploaded = vid_latest_uploaded.exclude(id=int(id)).filter(status=1, is_active=True).order_by('-updated_date')
            vid_latest_uploaded = list(chain(vid_latest_uploaded1, vid_latest_uploaded))
        else:
            vid_latest_uploaded = vid_latest_uploaded.filter(status=1, is_active=True).order_by('-updated_date')
    else:
        vid_latest_uploaded = vid_latest_uploaded.filter(status=1, is_active=True).order_by('-updated_date')

    if vid_latest_uploaded:
        vid_latest_uploaded = vid_latest_uploaded[0]

    videos_latest = VideoDetail.objects.select_related('skigit_id')
    if id:
        if videos_latest.filter(id=int(id), status=1, is_active=True).exists():
            videos_latest1 = videos_latest.filter(id=int(id), status=1, is_active=True).order_by('-updated_date')
            videos_latest = videos_latest.exclude(id=int(id)).filter(status=1, is_active=True).order_by('-updated_date')
            videos_latest = list(chain(videos_latest1, videos_latest))

        else:
            videos_latest = videos_latest.filter(status=1, is_active=True).order_by('-updated_date')
    else:
        videos_latest = videos_latest.filter(status=1, is_active=True).order_by('-updated_date')

    profile_dic = []
    for vid_profile in videos_latest:

        video_count = Like.objects.filter(skigit=vid_profile.skigit_id, status=True).count()
        like_dict.append({'id': vid_profile.id, 'count': video_count})
        video_share = Share.objects.filter(skigit_id=vid_profile, is_active=True).count()
        share_dict.append({'id': vid_profile.id, 'count': video_share})
        video_plug = VideoDetail.objects.filter(plugged_skigit=vid_profile.skigit_id, is_plugged=True, status=1).count()
        plug_dict.append({'id': vid_profile.id, 'count': video_plug})
        if vid_profile.made_by:
            us_profile = Profile.objects.get(user=vid_profile.made_by)
            if us_profile.logo_img.filter(is_deleted=False).all().count() > 0:
                us_profile.made_by = vid_profile.made_by.id
                us_profile.business_logo = us_profile.logo_img.filter(is_deleted=False).all()[0]
                profile_dic.append(us_profile)
    profile_dic = list(set(profile_dic))
    ski_share_list = []
    for vid_data in videos_latest:
        sharObj = Share.objects.filter(skigit_id=vid_data, is_active=True, user=request.user.id).order_by('to_user', '-pk').distinct('to_user')
        for sh in sharObj:
            ski_share_list.append({'share_date': sh.created_date, 'username': sh.to_user.username, 'vid': sh.skigit_id_id})
    video_likes = Like.objects.filter(user_id=request.user.id, status=1)
    like_skigit = []
    for likes in video_likes:
        like_skigit.append(likes.skigit_id)

    friend_list = []
    if Friend.objects.filter(Q(to_user=request.user.id) | Q(from_user=request.user.id), status=1).exists():
        f_list = Friend.objects.filter(Q(to_user=request.user.id) | Q(from_user=request.user.id), status=1)
        from_user_list = f_list.exclude(from_user=request.user.id).values_list('from_user', flat=True).distinct()
        to_user_list = f_list.exclude(to_user=request.user.id).values_list('to_user', flat=True).distinct()
        fr_list = list(merge(from_user_list, to_user_list))
        friends_detail = Profile.objects.filter(user__id__in=fr_list).order_by('user__username')

        for friends in friends_detail:
            if friends.profile_img:
                l_img = get_thumbnail(friends.profile_img, '35x35', quality=99, format='PNG').url
            else:
                l_img = '/static/skigit/detube/images/noimage_user.jpg'
            friend_list.append({'uid': friends.user.id, 'username': friends.user.username,
                                'name': friends.user.get_full_name(), 'image': l_img})
    context.update({
        'video_likes': like_skigit,
        'like_count': like_dict,
        'video_share': share_dict,
        'video_plug': plug_dict,
        'vid_latest_uploaded': vid_latest_uploaded,
        'videos_latest': videos_latest,
        'default_logo': profile_dic,
        'friend_list': friend_list,
        'skigit_list': ski_share_list,
        'users': get_all_logged_in_users()
    })

    if request.user.is_authenticated():
        try:
            user = User.objects.get(pk=request.user.id)
            user_profile = Profile.objects.get(user=user)

            if not user.groups.all():
                gen_obj = Group.objects.get_or_create(name="General User")
                user.groups.add(gen_obj[0])

            if user.is_staff and user.groups.all()[0].name == settings.SKIGIT_ADMIN:
                return HttpResponseRedirect("admin_tools/dashboard/skigit_admin")

            if user.is_superuser or (user.is_staff and is_user_general(user)) or is_user_general(user):
                fields = [
                    user.username,
                    user.first_name,
                    user.last_name,
                    user.email,
                    user_profile.birthdate,
                    user_profile.language,
                    user_profile.country,
                    user_profile.state,
                    user_profile.city,
                    user_profile.zip_code
                ]
                if not all(fields):
                    messages.error(request,
                                   'Please Fill The Complete Profile Detail')
                    raise ObjectDoesNotExist
                elif not user_profile.profile_img:
                    messages.error(request,
                                   'Please Upload Your Profile Picture')
                    raise ObjectDoesNotExist
            elif user.groups.all()[0].name == settings.BUSINESS_USER:
                fields = [
                    user.username,
                    user.first_name,
                    user.last_name,
                    user.email,
                    user_profile.birthdate,
                    user_profile.language,
                    user_profile.country,
                    user_profile.state,
                    user_profile.city,
                    user_profile.zip_code
                ]
                if not all(fields):
                    messages.error(request,
                                   'Please Fill The Complete Profile Detail')
                    raise ObjectDoesNotExist
                elif not user_profile.profile_img:
                    messages.error(request,
                                   'Please Upload Your Profile Picture')
                    raise ObjectDoesNotExist
                elif not user_profile.logo_img.filter(is_deleted=False).all():
                    messages.error(request, 'Please Upload Your Business Logo')
                    raise ObjectDoesNotExist
                elif not Invoice.objects.filter(user=request.user, type='CreditCard', is_deleted=False).exists() and not \
                        Invoice.objects.filter(user=request.user, type='PayPalAccount', is_deleted=False).exists():
                    messages.error(request, 'Payment information is not verified. Please verify payment method by '
                                            'filling PayPal or Credit/Debit card details.')
                    raise ObjectDoesNotExist
                elif request.user.profile.payment_method == '1' \
                        and not Invoice.objects.filter(user=request.user, type='CreditCard', is_deleted=False).exists():
                    messages.error(request, 'Payment information is not verified. Please verify payment method by '
                                            'filling PayPal or Credit/Debit card details.')
                    raise ObjectDoesNotExist
                elif request.user.profile.payment_method == '0' \
                        and not Invoice.objects.filter(user=request.user, type='PayPalAccount', is_deleted=False).exists():
                    messages.error(request, 'Payment information is not verified. Please verify payment method by '
                                            'filling PayPal or Credit/Debit card details.')
                    raise ObjectDoesNotExist
            else:
                logout(request)
                return HttpResponseRedirect('/')

        except ObjectDoesNotExist:
            return HttpResponseRedirect('/profile')

        user_profile = Profile.objects.get(user=user)
        context.update({'user': user, 'user_profile': user_profile})

        if extra_context is not None:
            context.update(extra_context)
        return render_to_response(template, context)

    elif request.method == 'POST' and 'login_submit' in request.POST:
        username = request.POST.get('log', None)
        password = request.POST.get('pwd', None)
        user = authenticate(username=username, password=password)
        if user:
            # Is the account active? It could have been disabled.
            if user.is_active:
                # If the account is valid and active, we can log the user in.
                # We'll send the user back to the homepage.
                login(request, user)
                return HttpResponseRedirect('/')
            else:
                # An inactive account was used - no logging in!
                context = RequestContext(request)
                context.update(csrf(request))
                context.update({'vid_latest_uploaded': vid_latest_uploaded,
                                'vid_all': vid_all,
                                'videos_latest': videos_latest,
                                'video_likes': like_skigit,
                                'like_count': like_dict,
                                'video_share': share_dict,
                                'video_plug': plug_dict,
                                'default_logo': profile_dic})
                context.update({
                    'login_error': 'Your Skigit account is disabled.'
                })

                if extra_context is not None:
                    context.update(extra_context)
                return render_to_response(template, context)

        else:
            # Bad login details were provided. So we can't log the user in.
            context.update(csrf(request))
            msg = "Invalid login details: {0}, {1}".format(username, password)
            context.update({'login_error': msg})
            context.update({'vid_latest_uploaded': vid_latest_uploaded,
                            'videos_latest': videos_latest,
                            'video_likes': like_skigit,
                            'like_count': like_dict,
                            'video_share': share_dict,
                            'video_plug': plug_dict,
                            'default_logo': profile_dic
                            })
            if extra_context is not None:
                context.update(extra_context)
            return render_to_response(template, context)

    else:

        if extra_context is not None:
            context.update(extra_context)
        return render_to_response(template, context)
