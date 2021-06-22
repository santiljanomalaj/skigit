import random
from heapq import merge
from itertools import chain
from user.models import Profile
import logging

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import logout, login, authenticate
from django.contrib.auth.models import Group, User
from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, render_to_response
from django.template.context import RequestContext
from django.template.context_processors import csrf
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.generic import TemplateView
from django.views.generic.base import RedirectView
from django.urls import reverse
from el_pagination.decorators import page_template
from social.models import Share
from sorl.thumbnail import get_thumbnail
from meta.views import Meta
from rest_framework import generics
from rest_framework.response import Response

from core.utils import is_user_general, get_all_logged_in_users, get_video_share_url
from friends.models import Friend
from invoices.models import Invoice
from skigit.models import Like, VideoDetail
from core.models import Category, SubjectCategory
from core.serializers import CategorySerializer, SubjectCategorySerializer

logger = logging.getLogger('Core')


# @method_decorator(ensure_csrf_cookie, name="dispatch")
class SkigitBaseView(TemplateView):

    description = "You gotta check out Skigit! Live, Share...Make the Difference!"

    def get_context_data(self, **kwargs):
        meta = Meta()

        DEFAULT_META_TITLE = og_title = 'Skigit'
        DEFAULT_META_LOGO = og_image = "{0}/static/{1}".format(settings.HOST, 'static/images/logo_glow_2.png')
        DEFAULT_META_DESCRIPTION = og_description = self.description
        DEFAULT_META_URL = og_url = '{0}://{1}/'.format(self.request.scheme, self.request.META['HTTP_HOST'])
        DEFAULT_META_DOMAIN = self.request.META['HTTP_HOST']
        og_type = 'website'

        """setattr(meta, 'DEFAULT_META_TITLE', DEFAULT_META_TITLE)
        setattr(meta, 'DEFAULT_META_LOGO', DEFAULT_META_LOGO)
        setattr(meta, 'DEFAULT_META_DESCRIPTION', DEFAULT_META_DESCRIPTION)
        setattr(meta, 'DEFAULT_META_DOMAIN', DEFAULT_META_DOMAIN)"""

        if 'skigit_id' in kwargs:
            if VideoDetail.objects.filter(id=kwargs['skigit_id']):
                skigit = get_object_or_404(VideoDetail, pk=kwargs['skigit_id'])
                u_profile = Profile.objects.get(user=skigit.skigit_id.user)
                company_logo_url = get_thumbnail(u_profile.profile_img, '100x100', quality=99).url
                try:
                    og_image = get_video_share_url(self.request, skigit, company_logo_url)
                except Exception as exc:
                    logger.error("The skigit share image throws error:", exc)
                    og_image = "{0}/static/{1}".format(settings.HOST, 'static/images/logo_glow_2.png')
                #print(og_image, "og_image")
                #og_image = "{0}/{1}".format(self.request.META['HTTP_HOST'], image_url)
                og_url = reverse('skigit_data', kwargs={'pk': skigit.id})
                og_description = skigit.why_rocks
                og_title = skigit.title
        #logger.error(meta)
        """setattr(meta, 'use_googleplus', True)
        setattr(meta, 'use_og', True)
        setattr(meta, 'use_twitter', True)
        setattr(meta, 'use_facebook', True)
        setattr(meta, 'facebook_app_id', '384777612248112')
        setattr(meta, 'title', og_title)
        setattr(meta, 'description', og_description)
        setattr(meta, 'image', og_image)
        setattr(meta, 'image_width', 400)
        setattr(meta, 'image_height', 400)
        setattr(meta, 'url', og_url)"""

        meta = Meta(
            title=og_title,
            description=og_description,
            image=og_image,
            image_width=600,
            image_height=600,
            url=og_url,
            use_og=True,
            object_type=og_type,
            use_facebook=True,
            use_twitter=True,
            facebook_app_id='384777612248112'
        )

        context = super(SkigitBaseView, self).get_context_data(**kwargs)
        context['meta'] = meta
        context.update(mobile_api_request=kwargs.get('mobile_api_request', False))
        return context

@method_decorator(ensure_csrf_cookie, name="dispatch")
class Home(SkigitBaseView):
    """ view for home
    """

    template_name = 'index.html'

    def get(self, request, extra_context=None, *args, **kwargs):
        id = request.GET.get('id', None)
        if id:
            kwargs.update(skigit_id=id)
        context = self.get_context_data(**kwargs)
        page_template = 'includes/entry_index_page.html'
        context.update({'page_template': page_template})
        like_dict = []
        share_dict = []
        plug_dict = []
        vid_random = None
        # random video
        ids = [item.id for item in VideoDetail.objects.filter(status=1, is_active=True)]
        vid = True
        while vid is True and ids:
            random_id = random.choice(ids)
            vid_random = VideoDetail.objects.filter(id=random_id, status=1, is_active=True)

            if vid_random:
                vid_random = vid_random[0]
                vid = False

        # vid_latest_uploaded = VideoDetail.objects.select_related('skigit_id')
        if id:
            if VideoDetail.objects.filter(id=int(id), status=1, is_active=True).exists():
                vid_latest_uploaded1 = VideoDetail.objects.filter(id=int(id), status=1, is_active=True).order_by(
                    '-updated_date')
                vid_latest_uploaded = VideoDetail.objects.exclude(id=int(id)).filter(status=1, is_active=True).order_by(
                    '-updated_date')
                vid_latest_uploaded = list(chain(vid_latest_uploaded1, vid_latest_uploaded))
            else:
                vid_latest_uploaded = vid_random
        else:
            vid_latest_uploaded = vid_random

        videos_latest = VideoDetail.objects.select_related('skigit_id')
        if id:
            if videos_latest.filter(id=int(id), status=1, is_active=True).exists():
                videos_latest1 = videos_latest.filter(id=int(id), status=1, is_active=True).order_by('-updated_date')
                videos_latest = videos_latest.exclude(id=int(id)).filter(status=1, is_active=True).order_by(
                    '-updated_date')
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
            video_plug = VideoDetail.objects.filter(plugged_skigit=vid_profile.skigit_id, is_plugged=True,
                                                    status=1).count()
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
            sharObj = Share.objects.filter(
                skigit_id=vid_data, is_active=True, user=request.user.id
            ).order_by(
                'to_user',
                '-pk'
            ).distinct(
                'to_user'
            )
            for sh in sharObj:
                ski_share_list.append(
                    {'share_date': sh.created_date, 'username': sh.to_user.username, 'vid': sh.skigit_id_id})
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
                    l_img = '/static/images/noimage_user.jpg'
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
            'users': get_all_logged_in_users(),
            'show_modal_skigit': True if id else False
        })

        if request.user.is_authenticated():
            try:
                user = User.objects.get(pk=request.user.id)
                user_profile = Profile.objects.get(user=user)

                if not user.groups.all():
                    # Remove this in FUTURE
                    # gen_obj = Group.objects.get_or_create(name="General User")
                    # user.groups.add(gen_obj[0])
                    return HttpResponseRedirect(reverse('manage-register-type'))

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
                    elif not Invoice.objects.filter(user=request.user, type='CreditCard',
                                                    is_deleted=False).exists() and not \
                            Invoice.objects.filter(user=request.user, type='PayPalAccount', is_deleted=False).exists():
                        messages.error(request, 'Payment information is not verified. Please verify payment method by '
                                                'filling PayPal or Credit/Debit card details.')
                        raise ObjectDoesNotExist
                    elif request.user.profile.payment_method == '1' \
                            and not Invoice.objects.filter(user=request.user, type='CreditCard',
                                                           is_deleted=False).exists():
                        messages.error(request, 'Payment information is not verified. Please verify payment method by '
                                                'filling PayPal or Credit/Debit card details.')
                        raise ObjectDoesNotExist
                    elif request.user.profile.payment_method == '0' \
                            and not Invoice.objects.filter(user=request.user, type='PayPalAccount',
                                                           is_deleted=False).exists():
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
            if request.is_ajax():
                self.template_name = page_template
            return render(request, self.template_name, context)
        else:
            if extra_context is not None:
                context.update(extra_context)
            if request.is_ajax():
                self.template_name = page_template
            return render(request, self.template_name, context)


@ensure_csrf_cookie
@page_template('includes/entry_index_page.html')
def index(request, template='index.html', extra_context=None):

    # request.META['CSRF_COOKIE_USED'] = True
    id = request.GET.get('id', None)
    context = {}
    like_dict = []
    share_dict = []
    plug_dict = []
    vid_all = None
    vid_random = None
    # random video
    max_id = VideoDetail.objects.filter(status=1, is_active=True).order_by('-id')[0].id
    vid = True
    while vid is True:
        random_id = random.randint(1, max_id + 1)
        vid_random = VideoDetail.objects.filter(id__gte=random_id, status=1, is_active=True)

        if vid_random:
            vid_random = vid_random[0]
            vid = False
    # vid_latest_uploaded = VideoDetail.objects.select_related('skigit_id')
    if id:
        if VideoDetail.objects.filter(id=int(id), status=1, is_active=True).exists():
            vid_latest_uploaded1 = VideoDetail.objects.filter(id=int(id), status=1, is_active=True).order_by(
                '-updated_date')
            vid_latest_uploaded = VideoDetail.objects.exclude(id=int(id)).filter(status=1, is_active=True).order_by(
                '-updated_date')
            vid_latest_uploaded = list(chain(vid_latest_uploaded1, vid_latest_uploaded))
        else:
            vid_latest_uploaded = vid_random
    else:
        vid_latest_uploaded = vid_random

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
                l_img = '/static/images/noimage_user.jpg'
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
                # Remove this in FUTURE
                # gen_obj = Group.objects.get_or_create(name="General User")
                # user.groups.add(gen_obj[0])
                return HttpResponseRedirect(reverse('manage-register-type'))

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
        return render(request, template, context)

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
            return render(request, template, context)

    else:

        if extra_context is not None:
            context.update(extra_context)
        return render(request, template, context)

class CategoryAPIView(generics.ListAPIView):
    serializer_class = CategorySerializer

    def list(self, request):
        result = {'status': '',
                  'message': ''}

        try:
            category = Category.objects.all()
            serializer = self.get_serializer(category, many=True)
            result.update(status='success',
                          message='',
                          data=serializer.data)
        except Exception as exc:
            result.update(status='error',
                          message='Category list not found!')
        return Response(result)

class SubjectCategoryAPIView(generics.ListAPIView):
    serializer_class = SubjectCategorySerializer

    def list(self, request):
        result = {'status': '',
                  'message': ''}

        try:
            category = SubjectCategory.objects.all()
            serializer = self.get_serializer(category, many=True)
            result.update(status='success',
                          message='',
                          data=serializer.data)
        except Exception as exc:
            result.update(status='error',
                          message='Subject Category list not found!')
        return Response(result)

class ShareManageDeeplinkView(RedirectView):
    permanent = True

    def get_redirect_url(self, *ar, **kwargs):
        query_params = self.request.GET
        category = query_params.get('category', '')
        video_id = query_params.get('contentid', '')
        url_name = reverse('index')

        if category == 'SKIGIT':
            if video_id:
                url_name = reverse('skigit_data', kwargs={'pk': video_id})
        return url_name
