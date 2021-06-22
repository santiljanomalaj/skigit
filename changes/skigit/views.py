from datetime import datetime
from heapq import merge
from user.forms import ProfileNotificationForm
from user.models import BusinessLogo, Profile, ProfileUrl
from allauth.account.signals import email_confirmed
from allauth.account.signals import user_signed_up
from el_pagination.decorators import page_template
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.dispatch import receiver
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, render, render_to_response
from django.template.context import RequestContext
from django.template.context_processors import csrf
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.views.generic import TemplateView, View
from social.models import Follow, Plugged, Share
from sorl.thumbnail import get_thumbnail
from django.views.decorators.clickjacking import xframe_options_exempt
from core.utils import (create_share_thumbnails, get_related_users, get_user_type, is_user_business, payment_required,
                        require_filled_profile)
from core.youtube_upload import upload_direct
from friends.models import Embed, Friend, Notification
from friends.views import get_all_logged_in_users, notification_settings
from invoices.models import EmbedInvoice
from skigit.forms import SkigitUploadForm, YoutubeDirectUploadForm, YoutubeLinkUploadForm, CopyrightInfringementForm
from skigit.models import (Category, Donation, Favorite, InappropriateSkigitReason, Incentive, Like, SubjectCategory,
                           Thumbnail, UploadedVideoLink, Video, VideoDetail)
from skigit.serializer import VideoDetailSerializer


@method_decorator(payment_required, name='dispatch')
@method_decorator(require_filled_profile, name='dispatch')
class CategoryDetail(TemplateView):
    def get(self, request, cat_slug=None, *args, **kwargs):

        page_template = 'category/category_body.html'

        video_detail = []
        like_dict = []
        share_dict = []
        plug_dict = []

        category_current = Category.objects.get(cat_slug=cat_slug)
        vid_latest_uploaded = VideoDetail.objects.select_related('skigit_id')
        vid_latest_uploaded = vid_latest_uploaded.filter(status=1, is_active=True)
        vid_latest_uploaded = vid_latest_uploaded.filter(category=category_current)

        if request.method == 'POST' and request.POST.get('sort', '') == '0':

            vid_latest_uploaded = vid_latest_uploaded.order_by('updated_date')

            if vid_latest_uploaded:
                vid_latest_uploaded = vid_latest_uploaded[0]
            videos = VideoDetail.objects.filter(category=category_current, status=1,
                                                is_active=True).order_by('updated_date')
            for vid in videos:
                like_count = Like.objects.filter(skigit=vid.skigit_id, status=True).count()
                like_dict.append({'id': vid.id, 'count': like_count})
                video_share = Share.objects.filter(skigit_id=vid, is_active=True).count()
                share_dict.append({'id': vid.id, 'count': video_share})
                video_plug = VideoDetail.objects.filter(plugged_skigit=vid.skigit_id, is_plugged=True, status=1).count()
                plug_dict.append({'id': vid.id, 'count': video_plug})
                video_detail.append(vid)
                if vid.made_by:
                    us_profile = Profile.objects.get(user=vid.made_by)
                    if us_profile.logo_img.filter(is_deleted=False).all().count() > 0:
                        vid.default_business_logo = us_profile.logo_img.filter(is_deleted=False).all()[0]
                    else:
                        vid.default_business_logo = ''
                else:
                    vid.default_business_logo = ''
                video_detail.append(vid)

            ski_share_list = []
            for vid_data in videos:
                sharObj = Share.objects.filter(skigit_id=vid_data, is_active=True,
                                               user=request.user.id).order_by('to_user', '-pk').distinct('to_user')
                for sh in sharObj:
                    ski_share_list.append({'share_date': sh.created_date, 'username': sh.to_user.username,
                                           'vid': sh.skigit_id_id})

            like_skigit = []
            video_likes = Like.objects.filter(user_id=request.user.id, status=True)
            for likes in video_likes:
                like_skigit.append(likes.skigit_id)
            context = {
                'page_template': page_template,
                'category_current': category_current,
                'video_detail': video_detail,
                'vid_latest_uploaded': vid_latest_uploaded,
                'video_share': share_dict,
                'video_plug': plug_dict,
                'video_likes': like_skigit,
                'like_count': like_dict,
                'skigit_list': ski_share_list,
                'order': 1,
                'order_title': 1,
                'order_views': 1,
                'order_random': 1,
                'order_likes': 1,
                'page_type': 'categorys',
                'users': get_all_logged_in_users()
            }
            if request.is_ajax():
                template = page_template
            return render(request, template, context)
        else:
            vid_latest_uploaded = vid_latest_uploaded.order_by('-updated_date')
            ski_share_list = []
            if vid_latest_uploaded:
                vid_latest_uploaded = vid_latest_uploaded[0]
            videos = VideoDetail.objects.filter(category=category_current, status=1, is_active=True).order_by(
                '-updated_date')
            for vid in videos:
                like_count = Like.objects.filter(skigit=vid.skigit_id, status=True).count()
                like_dict.append({'id': vid.id, 'count': like_count})
                video_share = Share.objects.filter(skigit_id=vid, is_active=True).count()
                share_dict.append({'id': vid.id, 'count': video_share})
                video_plug = VideoDetail.objects.filter(plugged_skigit=vid.skigit_id, is_plugged=True, status=1).count()
                plug_dict.append({'id': vid.id, 'count': video_plug})
                sharObj = Share.objects.filter(skigit_id=vid, is_active=True, user=request.user.id).order_by('to_user',
                                                                                                             '-pk').distinct(
                    'to_user')
                for sh in sharObj:
                    ski_share_list.append(
                        {'share_date': sh.created_date, 'username': sh.to_user.username, 'vid': sh.skigit_id_id})
                if vid.made_by:
                    us_profile = Profile.objects.get(user=vid.made_by)
                    if us_profile.logo_img.filter(is_deleted=False).all().count() > 0:
                        vid.default_business_logo = us_profile.logo_img.filter(is_deleted=False).all()[0]
                    else:
                        vid.default_business_logo = ''
                else:
                    vid.default_business_logo = ''
                video_detail.append(vid)
            like_skigit = []
            video_likes = Like.objects.filter(user_id=request.user.id, status=True)
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

        context = {
            'category_current': category_current,
            'video_detail': video_detail,
            'page_template': page_template,
            'vid_latest_uploaded': vid_latest_uploaded,
            'friend_list': friend_list,
            'video_share': share_dict,
            'video_plug': plug_dict,
            'video_likes': like_skigit,
            'like_count': like_dict,
            'skigit_list': ski_share_list,
            'order': 1,
            'order_views': 1,
            'order_title': 1,
            'order_random': 1,
            'order_likes': 1,
            'page_type': 'categorys',
            'users': get_all_logged_in_users()
        }
        if request.is_ajax():
            template = page_template
        return render(request, 'category/category_bash.html', context)


@method_decorator(payment_required, name='dispatch')
@method_decorator(require_filled_profile, name='dispatch')
class AwesomeThings(TemplateView):
    def get(self, request):
        context = {}

        awesome_cat = SubjectCategory.objects.filter(
            is_active=True
        ).order_by(
            'sub_cat_name'
        )
        if awesome_cat:
            context.update({'awesome_cat': awesome_cat})
        return render(request, "category/awesome_category.html", context)


# @login_required(login_url='/')
# @payment_required
# @require_filled_profile
class AwesomeThingsCategory(TemplateView):
    def get(self, request, sub_cat_slug=None):
        page_template = 'category/skigit_plugged_body.html'
        template = 'category/skigit_plugged_into.html'

        user = vid = category = user_profile = video_likes = category_current = None
        like_dict = []
        friend_list = []
        share_dict = []
        plug_dict = []
        ski_share_list = []

        try:
            category_current = SubjectCategory.objects.get(
                sub_cat_slug=sub_cat_slug)
            vid = VideoDetail.objects.select_related('skigit_id').filter(
                subject_category=category_current, status=1).order_by(
                '-updated_date')
            for vid_profile in vid:
                like_count = Like.objects.filter(skigit=vid_profile.skigit_id, status=True).count()
                like_dict.append({'id': vid_profile.id, 'count': like_count})
                video_share = Share.objects.filter(skigit_id=vid_profile, is_active=True).count()
                share_dict.append({'id': vid_profile.id, 'count': video_share})
                video_plug = VideoDetail.objects.filter(plugged_skigit=vid_profile.skigit_id, is_plugged=True,
                                                        status=1).count()
                plug_dict.append({'id': vid_profile.id, 'count': video_plug})

            for vid_data in vid:
                sharObj = Share.objects.filter(skigit_id=vid_data, is_active=True, user=request.user.id).order_by(
                    'to_user', '-pk').distinct('to_user')
                for sh in sharObj:
                    ski_share_list.append(
                        {'share_date': sh.created_date, 'username': sh.to_user.username, 'vid': sh.skigit_id_id})
        except ObjectDoesNotExist:
            messages.error(request, 'Your Requested Awesome things not found...!!!')
            return HttpResponseRedirect("/")

        like_skigit = []
        if request.user.is_authenticated():
            video_likes = Like.objects.filter(user_id=request.user.id, status=True)
            for likes in video_likes:
                like_skigit.append(likes.skigit_id)

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

        context = {
            'video_detail': vid,
            'category_current': category_current,
            'user': user,
            'user_profile': user_profile,
            'video_likes': like_skigit,
            'like_count': like_dict,
            'video_type': 'sub_cat',
            'friend_list': friend_list,
            'video_share': share_dict,
            'video_plug': plug_dict,
            'skigit_list': ski_share_list,
            'users': get_all_logged_in_users()
        }

        if request.is_ajax():
            template = page_template
        return render(request, template, context)


class SkigitData(TemplateView):
    def get(self, request, pk):
        video_likes = []
        all_reasion = []
        video_favorite = []
        video_follow = []
        ski_share_list = []

        if VideoDetail.objects.filter(id=pk):
            skigit = get_object_or_404(VideoDetail, pk=pk)

        else:
            return HttpResponseRedirect("/?id=%s" % pk)
        context = {}

        current_date = datetime.now().date()
        user = request.user
        embed_skigit = EmbedInvoice.objects.filter(skigit_user__id=skigit.skigit_id.user.id, user__id=request.user.id,
                                                   billing_month=current_date, embed_ski=skigit).exists()
        if not user.is_anonymous():
            type = get_user_type(user)
            if type == 'general':
                is_business = False
            elif type == 'business':
                is_business = True
        else:
            is_business = False

        count_i_plugged_into = 0
        related_user_list = get_related_users(request, skigit.skigit_id.user.id)
        all_sub_cat_skigits = VideoDetail.objects.exclude(id=pk).filter(Q(subject_category=skigit.subject_category) |
                                                                        Q(skigit_id__user__in=related_user_list),
                                                                        status=1, is_active=True).order_by('?')
        if not request.user.is_anonymous():
            count_i_plugged_into = VideoDetail.objects.filter(plugged_skigit__user=request.user, status=1,
                                                              is_plugged=True).count()
        if request.user.is_authenticated():
            video_likes = Like.objects.filter(user_id=request.user.id, status=True).values_list("skigit_id__id",
                                                                                                flat=True)
            all_reasion = InappropriateSkigitReason.objects.values('id', 'reason_title')
            video_favorite = Favorite.objects.filter(user_id=request.user.id,
                                                     status=1).values_list("skigit_id__id", flat=True)
            video_follow = Follow.objects.filter(user=request.user.id, status=True).values_list("follow__id", flat=True)

        profile_dic = []
        for vid_profile in all_sub_cat_skigits:
            if vid_profile.made_by:
                us_profile = Profile.objects.get(user=vid_profile.made_by)
                us_profile.made_by = vid_profile.made_by.id
                if us_profile.logo_img.filter(is_deleted=False).all().count() > 0:
                    us_profile.business_logo = us_profile.logo_img.filter(is_deleted=False).all()[0]
                    profile_dic.append(us_profile)
        profile_dic = list(set(profile_dic))
        current_view_count = skigit.view_count
        video_share_url = None
        u_profile = Profile.objects.get(user=skigit.skigit_id.user)
        company_logo_url = get_thumbnail(u_profile.profile_img, '100x100', quality=99).url

        if skigit.business_logo:

            if skigit.made_by and skigit.business_logo.is_deleted is False:
                if skigit.business_logo:
                    skigit_b_logo = get_thumbnail(skigit.business_logo.logo, '100x100', quality=99).url
                    video_share_url = create_share_thumbnails(skigit, skigit.skigit_id.thumbnails.all()[0].url,
                                                              request.build_absolute_uri(skigit_b_logo),
                                                              request.build_absolute_uri(company_logo_url))
            else:
                if skigit.made_by and skigit.business_logo.is_deleted is True:
                    u_profile = Profile.objects.get(user=skigit.made_by)
                    if u_profile.logo_img.filter(is_deleted=False).all().count() > 0:
                        blogo = u_profile.logo_img.filter(is_deleted=False).all()[0]
                        skigit_b_logo = get_thumbnail(blogo.logo, '100x100', quality=99).url
                        video_share_url = create_share_thumbnails(skigit, skigit.skigit_id.thumbnails.all()[0].url,
                                                                  request.build_absolute_uri(skigit_b_logo),
                                                                  request.build_absolute_uri(company_logo_url))
        else:
            video_share_url = create_share_thumbnails(skigit, skigit.skigit_id.thumbnails.all()[0].url)

        share_obj = Share.objects.exclude(to_user=request.user.id).filter(skigit_id__id=skigit.id, is_active=True,
                                                                          user=request.user.id
                                                                          ).order_by('to_user', '-pk').distinct(
            'to_user')
        if share_obj:
            for sh in share_obj:
                share_date = datetime.strptime(str(sh.created_date.date()), '%Y-%m-%d').strftime('%d-%b-%Y')
                ski_share_list.append(
                    {'share_date': share_date, 'username': sh.to_user.username, 'vid': sh.skigit_id_id})

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
        context = {
            "skigit": skigit,
            "video_likes": video_likes,
            "embed_skigit_vid": embed_skigit,
            "all_reasion": all_reasion,
            "all_sub_cat_skigits": all_sub_cat_skigits,
            "video_favorite": video_favorite,
            "video_favorite_count": video_favorite,
            "count_i_plugged_into": count_i_plugged_into,
            "default_logo": profile_dic,
            "video_follow": video_follow,
            "friend_list": friend_list,
            "skigit_list": ski_share_list,
            "is_business": is_business,
            "users": get_all_logged_in_users(),
            "video_share_url": request.build_absolute_uri(video_share_url),
        }

        return render(request, "includes/skigit_popup.html", context)


# TODO:move to another file
def getSwfURL(video_id):
    url = 'https://www.youtube.com/embed/%s' \
          '?modestbranding=1&showinfo=0&autoplay=0&autohide=1&rel=0&wmode=transparent' % (video_id)
    return url


def getYoutubeURL(video_id):
    url = 'https://www.youtube.com/watch?v=%s' % video_id
    return url


@method_decorator(csrf_exempt, name="dispatch")
@method_decorator(login_required(login_url='/'), name="dispatch")
@method_decorator(payment_required, name="dispatch")
@method_decorator(require_filled_profile, name="dispatch")
class DirectUpload(TemplateView):
    """ PRIMARY SKIGIT: Direct video upload method
    """

    def get(self, request, *args, **kwargs):
        form = YoutubeDirectUploadForm()
        form1 = SkigitUploadForm()
        form2 = YoutubeLinkUploadForm()
        organization_list = Donation.objects.all()
        message = ''
        return render(request, "youtube/yt_direct_upload.html", locals())

    def post(self, request):
        response_data = {}
        try:
            form = YoutubeDirectUploadForm(request.POST, request.FILES)
            form2 = YoutubeLinkUploadForm(request.POST)

            if form.is_valid() and request.POST.get("title", '') and request.POST.get('category', ''):
                if VideoDetail.objects.filter(title=request.POST.get("title", '')).exists():
                    response_data['is_success'] = False
                    response_data['message'] = "Title already in used please enter diffrent one"
                    return JsonResponse(response_data)
                else:
                    uploaded_video = form.save()
                    title = request.POST.get("title", '')
                    description = request.POST.get('why_rocks', '')

                    # Youtube Video API Upload call
                    video_entry = upload_direct(
                        str(uploaded_video.file_on_server.path),
                        str(title),
                        str(description)
                    )

                    if video_entry['id']:
                        swf_url = getSwfURL(video_entry['id'])
                        youtube_url = getYoutubeURL(video_entry['id'])
                        video_id = video_entry['id']

                        # save video_id to video instance
                        video = Video()
                        video.user = request.user
                        video.video_id = video_id
                        video.title = title
                        video.description = description
                        video.youtube_url = youtube_url
                        video.swf_url = swf_url
                        video.save()

                        # Creating Thumbnail Entry for Uploaded Videos
                        thumbnail = []
                        thumbnail.append(video_entry.get('snippet', {}).get('thumbnails', {}).get('high').get('url'))
                        thumbnail.append(video_entry.get('snippet', {}).get('thumbnails', {}).get('medium').get('url'))
                        thumbnail.append(
                            video_entry.get('snippet', {}).get('thumbnails', {}).get('default', {}).get('url'))

                        for thumb in thumbnail:
                            Thumbnail.objects.create(video=video, url=thumb)

                        skigit_form = VideoDetail()
                        skigit_form.title = request.POST.get("title", '')
                        if request.POST.get('category', ''):
                            category = Category.objects.get(id=request.POST.get('category', ''))
                            skigit_form.category = category
                        if request.POST.get('subject_category', ''):
                            subject_category = SubjectCategory.objects.get(id=request.POST.get('subject_category', ''))
                            skigit_form.subject_category = subject_category
                        skigit_form.add_logo = request.POST.get('add_logo', '')
                        skigit_form.receive_donate_sperk = request.POST.get('receive_donate_sperk', '')
                        skigit_form.why_rocks = request.POST.get('why_rocks', '')

                        if request.POST.get('made_by', ''):
                            user = User.objects.get(id=request.POST.get("made_by", ''))
                            skigit_form.made_by = user
                            skigit_form.business_user = user
                        if request.POST.get('made_by_option', ''):
                            skigit_form.made_by_option = request.POST.get('made_by_option', '')

                        skigit_form.skigit_id = video
                        skigit_form.share_skigit = video

                        if request.POST.get("add_logo", '') == '1' and (
                                    not request.POST.get("select_logo", '') == 'undefined' and not request.POST.get(
                                    "select_logo",
                                    '') == '') and \
                                BusinessLogo.objects.filter(id=request.POST.get("select_logo", '')).exists():
                            busness_logo = BusinessLogo.objects.get(id=request.POST.get("select_logo", ''))
                            skigit_form.business_logo = busness_logo
                            skigit_form.is_sperk = True
                            if request.POST.get('receive_donate_sperk', '') == '1':
                                donate = Donation.objects.get(id=(request.POST.get('donate_sperk', '')))
                                skigit_form.donate_skigit = donate

                        skigit_form.bought_at = request.POST.get("bought_at", "")
                        skigit_form.why_rocks = request.POST.get("why_rocks", "")
                        skigit_form.view_count = 0
                        skigit_form.save()

                        # delete the uploaded video instance
                        uploaded_video.delete()

                        # form1 = SkigitUploadForm()
                        # form2 = YoutubeLinkUploadForm()
                        # organization_list = Donation.objects.all()
                        response_data['is_success'] = True
                        response_data[
                            'message'] = "<span style='font-size:20px;'><i class='glyphicon glyphicon-ok-circle' " \
                                         "style='top: 5px !important;' /></span> Your video was successfully " \
                                         "uploaded. Wait while video will be processed"

                        return JsonResponse(response_data)
                    else:
                        # form1 = SkigitUploadForm()
                        # form2 = YoutubeLinkUploadForm()
                        # organization_list = Donation.objects.all()
                        response_data['is_success'] = False
                        response_data['message'] = video_entry['message']
                    return JsonResponse(response_data)
        except:
            # form1 = SkigitUploadForm()
            # form2 = YoutubeLinkUploadForm()
            # organization_list = Donation.objects.all()
            response_data['is_success'] = False
            response_data['message'] = 'Error into Upload Skigit, Please try again later'
            return JsonResponse(response_data)


@method_decorator(csrf_exempt, name="dispatch")
@method_decorator(login_required(login_url='/'), name="dispatch")
@method_decorator(payment_required, name="dispatch")
@method_decorator(require_filled_profile, name="dispatch")
class LinkUpload(TemplateView):
    """ PRIMARY SKIGIT: link upload method
    """

    def post(self, request):
        response_data = {}
        if request.is_ajax():
            try:
                video_link = str(request.POST.get('video_link', ''))
                url_parts = video_link.split("/")
                url_parts.reverse()
                url_parts1 = url_parts[0].split("?v=")
                url_parts1.reverse()
                video_id = url_parts1[0]
                swf_url = 'http://www.youtube.com/embed/' + video_id + \
                          '?modestbranding=1&showinfo=0&autoplay=0&autohide=1&rel=0&wmode=transparent'

                if VideoDetail.objects.filter(title=request.POST.get("title", '')).exists():
                    response_data['is_success'] = False
                    response_data['message'] = "Title already in used please enter diffrent one"
                    return JsonResponse(response_data)

                if Video.objects.filter(video_id=video_id).exists():
                    form1 = SkigitUploadForm()
                    form2 = YoutubeLinkUploadForm()
                    organization_list = Donation.objects.all()
                    # messages.error(request, "We're sorry.. your video failed to load due to duplication of video
                    # link")
                    response_data['is_success'] = False
                    response_data[
                        'message'] = "&#x2718; we're sorry.. your video failed to upload due to duplication of video " \
                                     "link"
                    return JsonResponse(response_data)
                else:
                    video_link_obj = UploadedVideoLink.objects.create(video_link=request.POST.get('video_link', ''))
                    # api = Api()
                    # api.authenticate()

                    # save video_id to video instance
                    video = Video()
                    video_tumb = video
                    video.user = request.user
                    video.video_id = video_id
                    video.title = request.POST.get("title", '')
                    video.youtube_url = video_link
                    video.swf_url = swf_url
                    video.save1()

                    skigit_form = VideoDetail()
                    skigit_form.title = request.POST.get("title", '')
                    if request.POST.get('category', ''):
                        category = Category.objects.get(id=request.POST.get('category', ''))
                        skigit_form.category = category
                    if request.POST.get('subject_category', ''):
                        subject_category = SubjectCategory.objects.get(id=request.POST.get('subject_category', ''))
                        skigit_form.subject_category = subject_category
                    skigit_form.add_logo = request.POST.get('add_logo', '')
                    skigit_form.receive_donate_sperk = request.POST.get('receive_donate_sperk', '')
                    skigit_form.why_rocks = request.POST.get('why_rocks', '')

                    if request.POST.get('made_by', ''):
                        user = User.objects.get(id=request.POST.get("made_by", ''))
                        skigit_form.made_by = user
                        skigit_form.business_user = user
                    if request.POST.get('made_by_option', ''):
                        skigit_form.made_by_option = request.POST.get('made_by_option', '')

                    skigit_form.skigit_id = video
                    skigit_form.share_skigit = video
                    if request.POST.get("add_logo", '') == '1' and (
                                not request.POST.get("select_logo", '') == 'undefined' and not request.POST.get(
                                "select_logo",
                                '') == '') and \
                            BusinessLogo.objects.filter(id=request.POST.get("select_logo", '')).exists():
                        busness_logo = BusinessLogo.objects.get(id=request.POST.get("select_logo", ''))
                        skigit_form.business_logo = busness_logo
                        skigit_form.is_sperk = True
                        if request.POST.get('receive_donate_sperk', '') == '1':
                            donate = Donation.objects.get(id=request.POST.get('donate_sperk', ''))
                            skigit_form.donate_skigit = donate
                        if request.POST.get('receive_donate_sperk', '') == '2':
                            incentive = Incentive()
                            incentive.title = 'Incentive for %s skigit' % request.POST.get("title", '')
                            incentive.save()
                            skigit_form.incentive = incentive

                    skigit_form.bought_at = request.POST.get("bought_at", "")
                    skigit_form.why_rocks = request.POST.get("why_rocks", "")
                    receive_donate_sperk = request.POST.get('receive_donate_sperk', '')
                    if receive_donate_sperk == '' or receive_donate_sperk == 'undefined':
                        skigit_form.receive_donate_sperk = 0
                    skigit_form.view_count = 0
                    skigit_form.save()

                    form1 = SkigitUploadForm()
                    form2 = YoutubeLinkUploadForm()
                    organization_list = Donation.objects.all()
                    response_data['is_success'] = True
                    response_data[
                        'message'] = "<span style='font-size:20px;'><i class='glyphicon glyphicon-ok-circle' " \
                                     "style='top: 5px !important;' /></span> Your video was successfully uploaded. " \
                                     "Wait while video will be processed"
                    return JsonResponse(response_data)
            except:
                form1 = SkigitUploadForm()
                form2 = YoutubeLinkUploadForm()
                organization_list = Donation.objects.all()
                response_data['is_success'] = False
                response_data[
                    'message'] = "<span style='font-size:20px;'><i class='glyphicon glyphicon-remove-circle' " \
                                 "style='top: 5px !important;' /></span> Error into Link Skigit, Please try again later"
                return JsonResponse(response_data)
        else:
            form = YoutubeDirectUploadForm()
            form1 = SkigitUploadForm()
            form2 = YoutubeLinkUploadForm()
            organization_list = Donation.objects.all()
            return render(request, "youtube/yt_direct_upload.html", locals())


@method_decorator(login_required(login_url='/'), name="dispatch")
class GetSperk(View):
    def post(self, request):
        if request.is_ajax():
            incentive_detail = None
            user_id = request.POST.get('user_id', None)
            if not user_id:
                data = {'incentive_detail': incentive_detail, 'all_business_logo': ''}
                return JsonResponse(data)

            incentive_detail = None
            default_incentive_msg = 'This maker is not offering any Skigit incentives at this time. Check back later!'
            try:
                usr = User.objects.get(id=int(user_id))
            except:
                # incentive_detail = default_incentive_msg
                incentive_detail = None
            if user_id and Profile.objects.filter(user=usr, incentive=1).exists():
                incentive_detail = Profile.objects.get(user=usr).skigit_incentive
                if not incentive_detail:
                    incentive_detail = None
            all_business_logo = []
            # get business logo
            profile = Profile.objects.filter(user=usr)
            for prof in profile:
                if prof.logo_img.filter(is_deleted=False).all():
                    all_logo_obj = prof.logo_img.filter(is_deleted=False).all()
                    for l_obj in all_logo_obj:
                        tmp = []
                        tmp.append(l_obj.id)
                        tmp.append(l_obj.logo.url)
                        all_business_logo.append(tmp)
                        del tmp
            data = {'incentive_detail': incentive_detail, 'all_business_logo': all_business_logo}

            return JsonResponse(data)

# not used
# class GetLogo(View):
#     """
#         Business Logo
#     """
#     def get(self, request):
#         selected_business_user = request.POST.get('buser', None)
#         profile = Profile.objects.get(user=selected_business_user)
#         busiless_logo = profile.logo_img.filter(is_deleted=False).first.logo
#         return JsonResponse({"incentive_detail": busiless_logo})


# old views


@login_required(login_url='/')
def user_profile_notifications(request):
    context = {}
    user = request.user
    context['is_business'] = is_user_business(user)
    field = 'user_profile_notification_submit'
    if request.method == 'POST' and field in request.POST:

        form1 = ProfileNotificationForm(request.POST, instance=user.profile)
        if form1.is_valid():
            form1.save()
            messages.success(request, 'eNotification settings updated successfully!')
            form1 = ProfileNotificationForm(instance=user.profile)
    else:

        form1 = ProfileNotificationForm(instance=user.profile)
        Profile.objects.get_or_create(user=user)

    user_profile = Profile.objects.get(user=user)
    context.update(csrf(request))
    context['form1'] = form1
    context['user'] = user
    context['user_profile'] = user_profile

    return render(request, 'profile/user_profile_notifications.html', context)


@login_required(login_url='/')
def user_profile_delete(request):
    context = {}
    user = request.user
    context['is_business'] = is_user_business(user)
    if request.method == 'POST' and 'user_profile_delete' in request.POST:
        delete_account = request.POST.get('delete-account', None)
        if delete_account == '1':
            # R.248.1 remove business logo from skigits
            videos = VideoDetail.objects.filter(business_user=request.user)
            if videos:
                for video in videos:
                    video.business_user = None
                    video.business_logo = None
                    video.made_by = None
                    video.is_sperk = False
                    video.save()
            User.objects.get(pk=request.user.id).delete()
            logout(request)
            messages.success(request, 'Your account deactivated successfully!')
            return HttpResponseRedirect('/')
        else:
            messages.error(request, 'There Is Something Wrong in deactivate')
    else:
        Profile.objects.get_or_create(user=user)

    user_profile = Profile.objects.get(user=user)
    context.update(csrf(request))
    context['user'] = user
    context['user_profile'] = user_profile
    return render(request, 'profile/user_profile_delete.html', context)


@login_required(login_url='/')
def my_statistics(request):
    context = {}
    context['is_business'] = is_user_business(request.user)
    skigit_count = VideoDetail.objects.filter(skigit_id__user=request.user,
                                              status=1, is_active=True).count()
    primary_count = VideoDetail.objects.filter(skigit_id__user=request.user, status=1,
                                               is_plugged=False, is_active=True).count()
    plug_in_count = VideoDetail.objects.filter(skigit_id__user=request.user, status=1,
                                               is_plugged=True, is_active=True).count()
    plug_in_my_skigit = VideoDetail.objects.filter(plugged_skigit__user=request.user, status=1,
                                                   is_plugged=True, is_active=True).count()
    like_count = Like.objects.filter(user=request.user, status=True).count()
    favorite_count = Favorite.objects.filter(user=request.user, status=1).count()
    follow_count = Follow.objects.filter(follow=request.user, status=True).count()
    follow_me_count = Follow.objects.filter(user=request.user, status=True).count()
    f_count1 = Friend.objects.filter(to_user=request.user.id, status='1').count()
    f_count2 = Friend.objects.filter(from_user=request.user.id, status='1').count()
    friend_count = f_count1 + f_count2
    share_count = Share.objects.filter(user=request.user, is_active=True).count()

    context.update({'skigit_count': skigit_count,
                    'primary_count': primary_count,
                    'plug_in_count': plug_in_count,
                    'plug_to_my_skigit': plug_in_my_skigit,
                    'like_count': like_count,
                    'favorite_count': favorite_count,
                    'follow_count': follow_count,
                    'follow_me_count': follow_me_count,
                    'friend_count': friend_count,
                    'share_count': share_count,
                    })

    return render(request, 'profile/my_statistics.html', context)


@login_required(login_url='/')
def sperk_profile(request, user, logo):
    """
        On Click of Sperk logo page will be redirect to
        Sperk profile, page having information related
        Sperk

    Args:
        request: Requested Method GET POST
        user: user_id
        logo: sperk (Logo id)

    Returns:
        Sperk (Business Logo) detail view

    """

    if User.objects.filter(id=request.user.id).exists():
        ski_share_list = []
        busniess_logo = []
        friend_list = []
        like_dict = []
        id = user
        logoid = logo
        profile_list = Profile.objects.filter(user__id=user)
        try:
            request_user = User.objects.get(pk=profile_list[0].user.id, is_active=True)
        except ObjectDoesNotExist:
            messages.error(request, 'Sorry, Your Request User Not Found.')
            return HttpResponseRedirect('/')  # HttpResponseRedirect
        busniesslogo = BusinessLogo.objects.get(id=logo, is_deleted=False)

        for b_logo in profile_list:
            for bb_logo in b_logo.logo_img.filter(is_deleted=False).all():
                bb_logo.img_id = bb_logo.id
                bb_logo.l_img = get_thumbnail(bb_logo.logo, '300x120', quality=99, format='PNG').url
                busniess_logo.append(bb_logo)

        for user_list in profile_list:
            company_url = ProfileUrl.objects.filter(user=user_list.user)

        if Embed.objects.filter(to_user=request_user, is_embed=True).exists():
            embed_skigit_list = Embed.objects.filter(to_user=request_user, is_embed=True).values_list('skigit_id',
                                                                                                      flat=True)
            if request.user.is_authenticated():
                if Friend.objects.filter(Q(to_user=request.user.id) | Q(from_user=request.user.id), status=1).exists():
                    f_list = Friend.objects.filter(Q(to_user=request.user.id) | Q(from_user=request.user.id), status=1)
                    from_user_list = f_list.exclude(from_user=request.user.id).values_list('from_user',
                                                                                           flat=True).distinct()
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
                video_likes = Like.objects.filter(user_id=request.user.id, status=True)
                for likes in video_likes:
                    like_dict.append(likes.skigit_id)
            vid = VideoDetail.objects.select_related('skigit_id').filter(skigit_id__id__in=embed_skigit_list)
            serializer = VideoDetailSerializer(vid, many=True)
            for vid_data in vid:
                sharObj = Share.objects.filter(skigit_id=vid_data, is_active=True, user=profile_list[0].user).order_by(
                    'to_user', '-pk').distinct('to_user')
                for sh in sharObj:
                    ski_share_list.append(
                        {'share_date': sh.created_date, 'username': sh.to_user.username, 'vid': sh.skigit_id_id})
            request_user = request_user
            video_detail = serializer.data
            video_likes = like_dict
            friend_list = friend_list
            order_value = '1'
            togal_val = '1'
            skigit_list = ski_share_list
            users = get_all_logged_in_users()

    return render(request, 'sperk/sperk-profile.html', locals())


@csrf_exempt
@login_required(login_url='/')
@payment_required
@require_filled_profile
def ajax_skigit_plugin_link(request, plug_id):
    """
        Plug-in : link upload method
    """
    response_data = {}
    if request.is_ajax() and request.method == 'POST':
        try:
            video_detail = VideoDetail.objects.get(id=plug_id)
            username = video_detail.skigit_id.user.username
            plugged_user = video_detail.skigit_id.user
            skigit_title = video_detail.title
            plug_category = video_detail.category.id
            sub_catogery = video_detail.subject_category.id
            video_link = str(request.POST.get('video_link', ''))
            url_parts = video_link.split("/")
            url_parts.reverse()
            url_parts1 = url_parts[0].split("?v=")
            url_parts1.reverse()
            video_id = url_parts1[0]
            swf_url = 'http://www.youtube.com/embed/' + video_id + '?modestbranding=1&showinfo=0&autoplay=0&autohide=1&rel=0&wmode=transparent'

            if VideoDetail.objects.filter(title=request.POST.get("title", '')).exists():
                response_data['is_success'] = False
                response_data['message'] = "Title already in used please enter different one"
                return JsonResponse(response_data)

            if Video.objects.filter(video_id=video_id).exists():
                form1 = SkigitUploadForm()
                form2 = YoutubeLinkUploadForm()
                organization_list = Donation.objects.all()
                response_data['is_success'] = False
                response_data['message'] = "&#x2718; we're sorry.. your video failed to upload due to duplication of video link"
                return JsonResponse(response_data)
            else:
                video_link_obj = UploadedVideoLink.objects.create(video_link=request.POST.get('video_link', ''))
                # api = Api()
                # api.authenticate()

                # save video_id to video instance
                video = Video()
                video_tumb = video
                video.user = request.user
                video.video_id = video_id
                video.title = request.POST.get("title", '')
                video.youtube_url = video_link
                video.swf_url = swf_url
                video.save1()

                skigit_form = VideoDetail()
                skigit_form.title = request.POST.get("title", '')
                if request.POST.get('category', ''):
                    category = Category.objects.get(id=request.POST.get('category', ''))
                    skigit_form.category = category
                if request.POST.get('subject_category', ''):
                    subject_category = SubjectCategory.objects.get(id=request.POST.get('subject_category', ''))
                    skigit_form.subject_category = subject_category
                skigit_form.add_logo = request.POST.get('add_logo', '')
                receive_donate_sperk = request.POST.get('receive_donate_sperk', '')
                if receive_donate_sperk == '' or receive_donate_sperk == 'undefined':
                    skigit_form.receive_donate_sperk = 0
                skigit_form.why_rocks = request.POST.get('why_rocks', '')

                if request.POST.get('made_by', ''):
                    user = User.objects.get(id=request.POST.get("made_by", ''))
                    skigit_form.made_by = user
                    skigit_form.business_user = user
                if request.POST.get('made_by_option', ''):
                    skigit_form.made_by_option = request.POST.get('made_by_option', '')

                skigit_form.skigit_id = video
                skigit_form.share_skigit = video
                if request.POST.get("add_logo", '') == '1' and (not request.POST.get("select_logo", '') == 'undefined' and not request.POST.get("select_logo", '') == '') and \
                        BusinessLogo.objects.filter(id=request.POST.get("select_logo", '')).exists():
                    busness_logo = BusinessLogo.objects.get(id=request.POST.get("select_logo", ''))
                    skigit_form.business_logo = busness_logo
                    skigit_form.is_sperk = True
                    if request.POST.get('receive_donate_sperk', '') == '1':
                        donate = Donation.objects.get(id=request.POST.get('donate_sperk', ''))
                        skigit_form.donate_skigit = donate
                    if request.POST.get('receive_donate_sperk', '') == '2':
                        incentive = Incentive()
                        incentive.title = 'Incentive for %s skigit' % request.POST.get("title", '')
                        incentive.save()
                        skigit_form.incentive = incentive

                skigit_form.bought_at = request.POST.get("bought_at", "")
                skigit_form.why_rocks = request.POST.get("why_rocks", "")
                plugged_video = Video.objects.get(id=video_detail.skigit_id.id)
                skigit_form.is_plugged = True
                skigit_form.plugged_skigit = plugged_video
                skigit_form.share_skigit = video
                skigit_form.view_count = 0
                skigit_form.save()
                plug_videos = Plugged()
                plug_videos.skigit = Video.objects.get(id=video_detail.skigit_id.id)
                plug_videos.user = request.user
                plug_videos.plugged = plugged_user
                plug_videos.save()

                # THIS NOTIFICATION MUST BE APPEAR AFTER SKIGIT IS PUBLISHED
                # if (notification_settings(video_detail.skigit_id.user.id, 'plug_notify')) == True:
                #     if not (request.user.id == video_detail.skigit_id.user.id):
                #
                #         if not video_detail.is_plugged:
                #             plug_message = 'Congratulations! '
                #             plug_message += video_detail.skigit_id.user.username
                #             plug_message += ' has plugged into your Skigit '
                #             plug_message += skigit_title
                #
                #             Notification.objects.create(msg_type='plug', skigit_id=video_detail.skigit_id.id,
                #                                         user=video_detail.skigit_id.user, message=plug_message,
                #                                         from_user=request.user)
                #         else:
                #             plug_message = 'Coincidence? I think not! '
                #             plug_message += request.user.username
                #             plug_message += ' has plugged into a Skigit that you plugged into '
                #             plug_message += skigit_title
                #
                #             Notification.objects.create(msg_type='plug-plug', skigit_id=video_detail.skigit_id.id,
                #                                         user=video_detail.skigit_id.user, message=plug_message,
                #                                         from_user=request.user)

                form1 = SkigitUploadForm()
                form2 = YoutubeLinkUploadForm()
                response_data['is_success'] = True
                response_data['message'] = "<span style='font-size:20px;'><i class='glyphicon glyphicon-ok-circle' style='top: 5px !important;' /></span> Your video was successfully uploaded. Wait while video will be processed"
                return JsonResponse(response_data)
        except:
            form1 = SkigitUploadForm()
            form2 = YoutubeLinkUploadForm()
            organization_list = Donation.objects.all()
            response_data['is_success'] = False
            response_data['message'] = "<span style='font-size:20px;'><i class='glyphicon glyphicon-remove-circle' style='top: 5px !important;' /></span> Error into Link Skigit, Please try again later"
            return JsonResponse(response_data)
    else:
        video_detail = VideoDetail.objects.get(id=plug_id)
        username = video_detail.skigit_id.user.username
        skigit_title = video_detail.title
        plug_category = video_detail.category.id
        sub_catogery = video_detail.subject_category.id
        my_aws_by = video_detail.skigit_id.id
        form = YoutubeDirectUploadForm()
        form1 = SkigitUploadForm()
        form2 = YoutubeLinkUploadForm()
        organization_list = Donation.objects.all()
        return render(request, "youtube/yt_skigit_plugin.html", locals())


@csrf_exempt
@login_required(login_url='/')
@payment_required
@require_filled_profile
def ajax_skigit_plugin_video(request, plug_id):
    """
        Plug-in : direct upload method
    """
    response_data = {}
    if request.method == 'POST':
        try:
            form = YoutubeDirectUploadForm(request.POST, request.FILES)
            form2 = YoutubeLinkUploadForm(request.POST)
            video_detail = VideoDetail.objects.get(id=plug_id)
            username = video_detail.skigit_id.user.username
            plugged_user = video_detail.skigit_id.user
            skigit_title = video_detail.title
            sub_catogery = video_detail.subject_category.sub_cat_name

            if form.is_valid() and request.POST.get("title", '') and request.POST.get('category', ''):
                if VideoDetail.objects.filter(title=request.POST.get("title", '')).exists():
                    response_data['is_success'] = False
                    response_data['message'] = "Title already in used please enter diffrent one"
                    return JsonResponse(response_data)
                else:
                    uploaded_video = form.save()
                    title = request.POST.get("title", '')
                    description = request.POST.get('why_rocks', '')

                    # Youtube Video API Upload call
                    video_entry = upload_direct(str(uploaded_video.file_on_server.path), str(title), str(description))

                    if video_entry['id']:
                        swf_url = getSwfURL(video_entry['id'])
                        youtube_url = getYoutubeURL(video_entry['id'])
                        video_id = video_entry['id']

                        # save video_id to video instance
                        video = Video()
                        video.user = request.user
                        video.video_id = video_id
                        video.title = title
                        video.description = description
                        video.youtube_url = youtube_url
                        video.swf_url = swf_url
                        video.save()

                        # Creating Thumbnail Entry for Uploaded Videos
                        thumbnail = []
                        thumbnail.append(video_entry.get('snippet', {}).get('thumbnails', {}).get('high').get('url'))
                        thumbnail.append(video_entry.get('snippet', {}).get('thumbnails', {}).get('medium').get('url'))
                        thumbnail.append(video_entry.get('snippet', {}).get('thumbnails', {}).get('default', {}).get('url'))

                        for thumb in thumbnail:
                            Thumbnail.objects.create(video=video, url=thumb)

                        # save video_id to video instance

                        skigit_form = VideoDetail()
                        skigit_form.title = request.POST.get("title", '')
                        if request.POST.get('category', ''):
                            category = Category.objects.get(id=request.POST.get('category', ''))
                            skigit_form.category = category
                        if request.POST.get('subject_category', ''):
                            subject_category = SubjectCategory.objects.get(id=request.POST.get('subject_category', ''))
                            skigit_form.subject_category = subject_category
                        skigit_form.add_logo = request.POST.get('add_logo', '')
                        skigit_form.receive_donate_sperk = request.POST.get('receive_donate_sperk', '')
                        skigit_form.why_rocks = request.POST.get('why_rocks', '')

                        if request.POST.get('made_by', ''):
                            user = User.objects.get(id=request.POST.get("made_by", ''))
                            skigit_form.made_by = user
                            skigit_form.business_user = user
                        if request.POST.get('made_by_option', ''):
                            skigit_form.made_by_option = request.POST.get('made_by_option', '')

                        skigit_form.skigit_id = video
                        skigit_form.share_skigit = video
                        if request.POST.get("add_logo", '') == '1' and (not request.POST.get("select_logo", '') == 'undefined' and not request.POST.get("select_logo", '') == '') and \
                                BusinessLogo.objects.filter(id=request.POST.get("select_logo", '')).exists():
                            busness_logo = BusinessLogo.objects.get(id=request.POST.get("select_logo", ''))
                            skigit_form.business_logo = busness_logo
                            skigit_form.is_sperk = True
                            if request.POST.get('receive_donate_sperk', '') == '1':
                                donate = Donation.objects.get(id=request.POST.get('donate_sperk', ''))
                                skigit_form.donate_skigit = donate

                        skigit_form.bought_at = request.POST.get("bought_at", "")
                        skigit_form.why_rocks = request.POST.get("why_rocks", "")
                        plugged_video = Video.objects.get(id=video_detail.skigit_id.id)
                        skigit_form.is_plugged = True
                        skigit_form.plugged_skigit = plugged_video
                        skigit_form.share_skigit = video
                        skigit_form.view_count = 0
                        skigit_form.save()
                        plug_videos = Plugged()
                        plug_videos.skigit = Video.objects.get(id=video_detail.skigit_id.id)
                        plug_videos.user = request.user
                        plug_videos.plugged = plugged_user
                        plug_videos.save()

                        if (notification_settings(video_detail.skigit_id.user.id, 'plug_notify')) == True:

                            if not (request.user.id == video_detail.skigit_id.user.id):

                                if not video_detail.is_plugged:
                                    plug_message = 'Congratulations! '
                                    plug_message += video_detail.skigit_id.user.username
                                    plug_message += ' has plugged into your Skigit '
                                    plug_message += skigit_title
                                    Notification.objects.create(msg_type='plug', skigit_id=video_detail.skigit_id.id,
                                                                user=video_detail.skigit_id.user, message=plug_message,
                                                                from_user=request.user)
                                else:
                                    plug_message = 'Coincidence? I think not! '
                                    plug_message += request.user.username
                                    plug_message += ' has plugged into a Skigit that you plugged into '
                                    plug_message += skigit_title
                                    Notification.objects.create(msg_type='plug-plug', skigit_id=video_detail.skigit_id.id,
                                                                user=video_detail.skigit_id.user, message=plug_message,
                                                                from_user=request.user)

                        form1 = SkigitUploadForm()
                        form2 = YoutubeLinkUploadForm()
                        organization_list = Donation.objects.all()
                        response_data['is_success'] = True
                        response_data['message'] = "<span style='font-size:20px;'><i class='glyphicon glyphicon-ok-circle' style='top: 5px !important;' /></span> Your video was successfully uploaded. Wait while video will be processed."
                        return JsonResponse(response_data)
        except:
            form1 = SkigitUploadForm()
            form2 = YoutubeLinkUploadForm()
            organization_list = Donation.objects.all()
            response_data['is_success'] = False
            response_data['message'] = "<span style='font-size:20px;'><i class='glyphicon glyphicon-remove-circle' style='top: 5px !important;' /></span> Error into Link Skigit, Please try again later."
            # video.delete()
            return JsonResponse(response_data)
    else:
        video_detail = VideoDetail.objects.get(id=plug_id)
        username = video_detail.skigit_id.user.username
        skigit_title = video_detail.title
        plug_category = video_detail.category.id
        sub_catogery = video_detail.subject_category.id
        my_aws_by = video_detail.skigit_id.id
        form = YoutubeDirectUploadForm()
        form1 = SkigitUploadForm()
        form2 = YoutubeLinkUploadForm()
        organization_list = Donation.objects.all()
        message = ''
        return render(request, "youtube/yt_direct-upload.html", locals())


def skigit_count_update(request):
    response_data = {}
    if request.is_ajax() and request.method == 'POST':
        try:
            video_id = request.POST.get('skigit_id', None)
            if VideoDetail.objects.filter(id=int(video_id)).exists():
                vid = VideoDetail.objects.get(id=int(video_id))
                vid.view_count = vid.view_count + 1
                vid.save()
                response_data['view_count'] = vid.view_count
                response_data['is_success'] = True
                response_data['message'] = 'view count updated'
        except ObjectDoesNotExist:
            response_data['is_success'] = False
    return JsonResponse(response_data)


def get_user_notification(request):
    response_data = {'is_success': False, 'message': 'Error in get user notification'}
    if request.is_ajax() and request.user.is_authenticated:
        user = User.objects.get(pk=request.user.id)
        count = Notification.objects.filter(user=user, is_view=False, is_read=False, is_active=True).count()
        response_data['is_success'] = True
        response_data['message'] = 'Sucess in ajax call'
        response_data['count'] = count
    return JsonResponse(response_data)


@login_required(login_url='/')
@payment_required
@require_filled_profile
def my_skigits(request, user_id=None, template='category/my_skigits.html',
        page_template='includes/skigit_list.html'):

    user = vid = category = user_profile = video_likes = category_current = None
    like_dict = []
    profile_dic = []
    share_dict = []
    plug_dict = []
    try:
        category_current = request.user.username
        vid = VideoDetail.objects.select_related('skigit_id').filter(
            skigit_id__user=request.user, status=1, is_active=True).order_by('-updated_date')
        for vid_profile in vid:
            likes_count = Like.objects.filter(skigit=vid_profile.skigit_id, status=True).count()
            like_dict.append({'id': vid_profile.id, 'count': likes_count})
            video_share = Share.objects.filter(skigit_id=vid_profile, is_active=True).count()
            share_dict.append({'id': vid_profile.id, 'count': video_share})
            video_plug = VideoDetail.objects.filter(plugged_skigit=vid_profile.skigit_id,
                                                    is_plugged=True, status=1).count()
            plug_dict.append({'id': vid_profile.id, 'count': video_plug})
            if vid_profile.made_by:
                us_profile = Profile.objects.get(user=vid_profile.made_by)
                us_profile.made_by = vid_profile.made_by.id
                if us_profile.logo_img.filter(is_deleted=False).all().count() > 0:
                    us_profile.business_logo = us_profile.logo_img.filter(is_deleted=False).all()[0]
                    profile_dic.append(us_profile)
        profile_dic = list(set(profile_dic))

        ski_share_list = []
        for vid_data in vid:
            sharObj = Share.objects.filter(skigit_id=vid_data, is_active=True,
                                           user=request.user.id).order_by('to_user', '-pk').distinct('to_user')
            for sh in sharObj:
                ski_share_list.append(
                    {'share_date': sh.created_date, 'username': sh.to_user.username, 'vid': sh.skigit_id_id})

    except ObjectDoesNotExist:
        messages.error(request, 'No Skigits found...!!!')
        return HttpResponseRedirect("/")

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
    context = {
        'video_detail': vid,
        'category_current': category_current,
        'user': user,
        'user_profile': user_profile,
        'video_likes': like_skigit,
        'like_count': like_dict,
        'default_logo': profile_dic,
        'friend_list': friend_list,
        'video_share': share_dict,
        'video_plug': plug_dict,
        'skigit_list': ski_share_list,
        'users': get_all_logged_in_users()
    }
    if request.is_ajax():
        template = page_template
    return render_to_response(template, context)


@login_required(login_url='/')
@payment_required
@require_filled_profile
def my_skigits_view(request, user_id, template='sk_cat/skigit_plugged_into.html',
                            page_template='sk_cat/skigit_plugged_body.html'):

    user = us_profile = vid = category = user_profile = video_likes = category_current = None

    like_dict = []
    profile_dic = []
    share_dict = []
    plug_dict = []
    ski_share_list = []
    try:
        category_current = request.user.username
        vid = VideoDetail.objects.select_related('skigit_id').filter(
            skigit_id__user=user_id,
            status=True
        ).order_by('-updated_date')

        for vid_profile in vid:
            like_count = Like.objects.filter(skigit=vid_profile.skigit_id, status=True).count()
            like_dict.append({'id': vid_profile.id, 'count': like_count})
            video_share = Share.objects.filter(skigit_id=vid_profile, is_active=True).count()
            share_dict.append({'id': vid_profile.id, 'count': video_share})
            video_plug = VideoDetail.objects.filter(plugged_skigit=vid_profile.skigit_id, is_plugged=True, status=1).count()
            plug_dict.append({'id': vid_profile.id, 'count': video_plug})
            if vid_profile.made_by:
                us_profile = Profile.objects.get(user=vid_profile.made_by)
                us_profile.made_by = vid_profile.made_by.id
                if us_profile.logo_img.filter(is_deleted=False).all().count()>0:
                    us_profile.business_logo = us_profile.logo_img.filter(is_deleted=False).all()[0]
                profile_dic.append(us_profile)
        profile_dic = list(set(profile_dic))

        for vid_data in vid:
            sharObj = Share.objects.filter(skigit_id=vid_data, is_active=True, user=request.user.id).order_by('to_user', '-pk').distinct('to_user')
            for sh in sharObj:
                ski_share_list.append(
                    {'share_date': sh.created_date, 'username': sh.to_user.username, 'vid': sh.skigit_id_id})

    except ObjectDoesNotExist:
        messages.error(request, 'No Skigits found...!!!')
        return HttpResponseRedirect("/")
    user = User.objects.get(id=int(user_id))

    like_skigit = []
    if request.user.is_authenticated():
        video_likes = Like.objects.filter(user_id=request.user.id, status=True)
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

    context = {
        'video_detail': vid,
        'category_current': category_current,
        'user': user,
        'user_profile': us_profile,
        'video_likes': like_skigit,
        'like_count': like_dict,
        'video_type': 'c_o_skigit',
        'default_logo': profile_dic,
        'friend_list': friend_list,
        'video_share': share_dict,
        'video_plug': plug_dict,
        'skigit_list': ski_share_list,
        'users': get_all_logged_in_users()
    }

    if request.is_ajax():
        template = page_template
    return render_to_response(template, context)


@login_required(login_url='/')
@payment_required
@require_filled_profile
def plugged_in_skigits(request, template='sk_cat/skigit_plugged_into.html',
                       page_template='sk_cat/skigit_plugged_body.html'):
    user = vid = category = user_profile = video_likes = skigit_plug = None
    like_dict = []
    profile_dic = []
    vid_list = []
    share_dict = []
    plug_dict = []
    ski_share_list = []
    plug_skigit_list = []
    try:
        skigit_plug = request.user.username
        vid_record = Video.objects.filter(user=request.user.id).values_list('id', flat=True).order_by('-created_date')
        if VideoDetail.objects.filter(skigit_id__id__in=vid_record, status=True, is_plugged=True).exists():
            plug_id = VideoDetail.objects.filter(skigit_id__id__in=vid_record, status=True,
                                                 is_plugged=True).values_list('skigit_id', flat=True)
            vid = VideoDetail.objects.filter(skigit_id__id__in=plug_id, status=True)
            for vid_profile in vid:
                pluged_videos = VideoDetail.objects.get(title=vid_profile.plugged_skigit.title, status=True)
                plug_skigit_list.append({'plug_video_id': pluged_videos.id, 'vid_id': vid_profile.id})
                like_count = Like.objects.filter(skigit=vid_profile.skigit_id, status=True).count()
                like_dict.append({'id': vid_profile.id, 'count': like_count})
                video_share = Share.objects.filter(skigit_id=vid_profile, is_active=True).count()
                share_dict.append({'id': vid_profile.id, 'count': video_share})
                video_plug = VideoDetail.objects.filter(plugged_skigit=vid_profile.skigit_id,
                                                        is_plugged=True, status=1).count()
                plug_dict.append({'id': vid_profile.id, 'count': video_plug})
                if vid_profile.made_by:
                    us_profile = Profile.objects.get(user=vid_profile.made_by)
                    us_profile.made_by = vid_profile.made_by.id
                    if us_profile.logo_img.filter(is_deleted=False).all().count() > 0:
                        us_profile.business_logo = us_profile.logo_img.filter(is_deleted=False).all()[0]
                    profile_dic.append(us_profile)
                sharObj = Share.objects.filter(skigit_id=vid_profile, is_active=True,
                                               user=request.user.id).order_by('to_user', '-pk').distinct('to_user')
                for sh in sharObj:
                    ski_share_list.append({'share_date': sh.created_date, 'username': sh.to_user.username,
                                           'vid': sh.skigit_id_id})
        profile_dic = list(set(profile_dic))
    except ObjectDoesNotExist:
        messages.error(request, 'No Skigits found...!!!')
        return HttpResponseRedirect("/")

    like_skigit = []
    if request.user.is_authenticated():
        video_likes = Like.objects.filter(user_id=request.user.id, status=True)
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

    context = {
        'video_detail': vid,
        'skigit_plug': skigit_plug,
        'user': user,
        'user_profile': user_profile,
        'video_likes': like_skigit,
        'like_count': like_dict,
        'video_type': 'plugged',
        'default_logo': profile_dic,
        'friend_list': friend_list,
        'video_share': share_dict,
        'video_plug': plug_dict,
        'skigit_list': ski_share_list,
        'pluged_videos': plug_skigit_list,
        'users': get_all_logged_in_users()
    }

    if request.is_ajax():
        template = page_template
    return render(request, template, context)

@login_required(login_url='/')
@payment_required
@require_filled_profile
def liked_skigits(request, template='sk_cat/skigit_plugged_into.html',
                       page_template='sk_cat/skigit_plugged_body.html'):

    user = vid = category = user_profile = video_likes = skigit_like = None
    like_dict = []
    profile_dic = []
    share_dict = []
    plug_dict = []
    ski_share_list = []
    try:
        skigit_like = request.user.username
        liked_skigits = Like.objects.filter(
            user_id=request.user.id, status=True
        ).values('skigit_id')
        vid = VideoDetail.objects.select_related('skigit_id').filter(
            skigit_id__in=liked_skigits,
            status=1
        ).order_by('-updated_date')
        for vid_profile in vid:
            like_count = Like.objects.filter(skigit=vid_profile.skigit_id, status=True).count()
            like_dict.append({'id': vid_profile.id, 'count': like_count})
            video_share = Share.objects.filter(skigit_id=vid_profile, is_active=True).count()
            share_dict.append({'id': vid_profile.id, 'count': video_share})
            video_plug = VideoDetail.objects.filter(plugged_skigit=vid_profile.skigit_id, is_plugged=True, status=1).count()
            plug_dict.append({'id': vid_profile.id, 'count': video_plug})
            if vid_profile.made_by:
                us_profile = Profile.objects.get(user=vid_profile.made_by)
                us_profile.made_by = vid_profile.made_by.id
                if us_profile.logo_img.filter(is_deleted=False).all().count() > 0:
                    us_profile.business_logo = us_profile.logo_img.filter(is_deleted=False).all()[0]
                profile_dic.append(us_profile)
        profile_dic = list(set(profile_dic))

        for vid_data in vid:
            sharObj = Share.objects.filter(skigit_id=vid_data, is_active=True, user=request.user.id).order_by('to_user', '-pk').distinct('to_user')
            for sh in sharObj:
                ski_share_list.append(
                    {'share_date': sh.created_date, 'username': sh.to_user.username, 'vid': sh.skigit_id_id})
    except ObjectDoesNotExist:
        messages.error(request, 'No Skigits found...!!!')
        return HttpResponseRedirect("/")

    like_skigit = []
    if request.user.is_authenticated():
        video_likes = Like.objects.filter(user_id=request.user.id, status=True)
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

    context = {
        'video_detail': vid,
        'skigit_like': skigit_like,
        'user': user,
        'user_profile': user_profile,
        'video_likes': like_skigit,
        'like_count': like_dict,
        'video_share': share_dict,
        'video_plug': plug_dict,
        'video_type': 'liked',
        'default_logo': profile_dic,
        'friend_list': friend_list,
        'skigit_list': ski_share_list,
        'users': get_all_logged_in_users()
    }
    if request.is_ajax():
        template = page_template
    return render(request, template, context)

@login_required(login_url='/')
@payment_required
@require_filled_profile
def favorite_skigits(request, template='sk_cat/skigit_plugged_into.html',
                       page_template='sk_cat/skigit_plugged_body.html'):

    user = vid = category = user_profile = video_fav = skigit_fav = None
    profile_dic = []
    share_dict = []
    plug_dict = []
    like_dict = []
    ski_share_list = []
    try:
        skigit_fav = request.user.username
        fav_skigits = Favorite.objects.filter(
            user_id=request.user.id, status=True
        ).values('skigit_id')
        vid = VideoDetail.objects.select_related('skigit_id').filter(
            skigit_id__in=fav_skigits,
            status=1
        ).order_by('-updated_date')
        for vid_profile in vid:
            like_count = Like.objects.filter(skigit=vid_profile.skigit_id, status=True).count()
            like_dict.append({'id': vid_profile.id, 'count': like_count})
            video_share = Share.objects.filter(skigit_id=vid_profile, is_active=True).count()
            share_dict.append({'id': vid_profile.id, 'count': video_share})
            video_plug = VideoDetail.objects.filter(plugged_skigit=vid_profile.skigit_id, is_plugged=True, status=1).count()
            plug_dict.append({'id': vid_profile.id, 'count': video_plug})
            if vid_profile.made_by:
                us_profile = Profile.objects.get(user=vid_profile.made_by)
                us_profile.made_by = vid_profile.made_by.id
                if us_profile.logo_img.filter(is_deleted=False).all().count() > 0:
                    us_profile.business_logo = us_profile.logo_img.filter(is_deleted=False).all()[0]
                profile_dic.append(us_profile)
        profile_dic = list(set(profile_dic))

        for vid_data in vid:
            sharObj = Share.objects.filter(skigit_id=vid_data, is_active=True, user=request.user.id).order_by('to_user', '-pk').distinct('to_user')
            for sh in sharObj:
                ski_share_list.append(
                    {'share_date': sh.created_date, 'username': sh.to_user.username, 'vid': sh.skigit_id_id})
    except ObjectDoesNotExist:
        messages.error(request, 'No Skigits found...!!!')
        return HttpResponseRedirect("/")

    like_skigit = []
    if request.user.is_authenticated():
        video_likes = Like.objects.filter(user_id=request.user.id, status=True)
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
    context = {
        'video_detail': vid,
        'skigit_fav': skigit_fav,
        'user': user,
        'user_profile': user_profile,
        'video_likes': like_skigit,
        'like_count': like_dict,
        'video_type': 'fav',
        'default_logo': profile_dic,
        'friend_list': friend_list,
        'video_share': share_dict,
        'video_plug': plug_dict,
        'skigit_list': ski_share_list,
        'users': get_all_logged_in_users()
    }
    if request.is_ajax():
        template = page_template
    return render(request, template, context)

@login_required(login_url='/')
@payment_required
@require_filled_profile
def i_am_following_view(request, template='sk_cat/skigit_plugged_into.html',
                        page_template='sk_cat/i_am_following_body.html'):
    follow_list = []
    try:
        follow_record = Follow.objects.filter(user=request.user.id, status=True).order_by('-follow__first_name')
        for following in follow_record:
            if User.objects.exclude(id=request.user.id).filter(id=following.follow.id).exists():
                user_follow_detail = User.objects.exclude(id=request.user.id).filter(id=following.follow.id)
                for user_detail in user_follow_detail:
                    user_profile = Profile.objects.get(user=user_detail)
                    name = user_detail.get_full_name()
                    if user_profile.profile_img:
                        l_img = get_thumbnail(user_profile.profile_img, '100x100', quality=99, format='PNG').url
                    else:
                        l_img = "/static/skigit/detube/images/noimage_user.jpg"
                    follow_count = Follow.objects.exclude(follow=request.user.id).filter(follow=user_detail.id, status=True).count()
                    follow_list.append({'user': request.user.id, 'follower': user_detail.id, 'name': name,
                         'follower_img': l_img, 'username': user_detail.username, 'count': follow_count})
        follow_list = sorted(follow_list, key=lambda follow: (follow['name']))

    except ObjectDoesNotExist:
        messages.error(request, 'No Following user were found...!!!')
        return HttpResponseRedirect("/")

    context = {
        'video_detail': follow_list,
        'current_user': request.user.username,
        'video_type': 'i_am_following',
    }

    if request.is_ajax():
        template = page_template
    return render(request, template, context)


@login_required(login_url='/')
@csrf_protect
def share_to_friends(request):
    response_data = {}
    if request.is_ajax() and request.method == 'POST':
        # try:
            time_zone = request.POST.get('time_zone', '')
            skigit_id = request.POST.get('vid_id', None)
            f_list = request.POST.getlist('friend_list[]', None)
            notify = Profile.objects.filter(user=request.user).values('share_notify')
            for f_id in f_list:
                if User.objects.filter(id=f_id).exists():
                    user_obj = User.objects.get(id=f_id)
                    share_obj = Share.objects.create(user=request.user, to_user=user_obj, skigit_id_id=skigit_id)
                    if VideoDetail.objects.filter(id=int(skigit_id)).exists():
                        video = VideoDetail.objects.get(id=int(skigit_id))
                        business_share_invoice(request.user.id, video.skigit_id.id)
                        mail_id = user_obj.email
                        mail_body = "<center><label><h3 style='color:#1C913F;font-family: " + "Proza Libre" + ", sans-serif;'>" \
                                    "You gotta check this out!<h3></label></center>\r\n\r\n<p><center>" \
                                    "<a href='http://skigit.com?id=" + str(skigit_id) + "'style='text-decoration:none;color:#0386B8;margin: 10px auto;display: table;font-size:16px;font-family: " + "Proza Libre" + ", sans-serif;'>" + video.title + "</a>" \
                                    "</center></p>\r\n<p style='text-align:justyfy;'>" + video.why_rocks + "</p>\r\n" \
                                    "<p><center><img src='http://skigit.com/static/skigit/images/shair.png' style='width:165px;' class='img-responsive'></center></p>"
                        send_email(request.user.username + ' Shared an Awesome Skigit with You!', mail_body, mail_id, '', EMAIL_HOST_VIDEO)

                        f_nt_message = " "
                        f_nt_message += "You are on the Radar! "
                        f_nt_message += request.user.username
                        f_nt_message += " has shared the awesome Skigit "
                        f_nt_message += video.title
                        f_nt_message += " with you! "
                        if (notification_settings(user_obj.id, 'share_notify')) == True:
                            if not Notification.objects.filter(msg_type='share', user=user_obj,
                                                               skigit_id=video.skigit_id.id,
                                                               from_user=request.user).exists():
                                Notification.objects.create(user=user_obj, from_user=request.user,
                                                            skigit_id=video.skigit_id.id,
                                                            msg_type='share',
                                                            message=f_nt_message)
                            else:
                                Notification.objects.filter(user=user_obj, skigit_id=video.skigit_id.id,
                                                            from_user=request.user,
                                                            msg_type='share').update(msg_type='share_old', is_view=True,
                                                                                     is_active=False, is_read=True)
                                Notification.objects.filter(user=user_obj, from_user=request.user,
                                                            skigit_id=video.skigit_id.id, msg_type='share_old').delete()
                                Notification.objects.create(user=user_obj, from_user=request.user,
                                                            skigit_id=video.skigit_id.id, msg_type='share',
                                                            message=f_nt_message)
            response_data['is_success'] = True
            response_data['message'] = 'Skigit Share Successfully'
            response_data['date'] = get_time_delta(datetime.datetime.utcnow(), time_zone)
        #
        # except ObjectDoesNotExist:
        #     response_data['is_success'] = False
    return JsonResponse(response_data)


@login_required(login_url='/')
def email_share_friends(request):
    response_data = {}
    if request.is_ajax() and request.method == 'POST':
        # try:
            em = []
            email = request.POST.get('email_list', None)
            video_id = request.POST.get('video_id', None)
            if VideoDetail.objects.filter(id=int(video_id)).exists():
                video = VideoDetail.objects.get(id=int(video_id))
                mail_body = "<center><label><h3 style='color:#1C913F;font-family: "+"Proza Libre"+", sans-serif;'>" \
                        "You gotta chek this out!<h3></label></center>\r\n\r\n<p><center>" \
                        "<a href='http://skigit.com?id="+str(video_id)+"'style='text-decoration:none;color:#0386B8;margin: 10px auto;display: table;font-size:16px;font-family: "+"Proza Libre"+", sans-serif;'>"+video.title +"</a>" \
                        "</center></p>\r\n<p style='text-align:justyfy;'>"+video.why_rocks+"</p>\r\n" \
                        "<p><center><img src='http://skigit.com/static/skigit/images/shair.png' style='width:165px;' class='img-responsive'></center></p>"
                if email:
                    em = email.split(',')
                    for mail_id in em:
                        send_email(request.user.username+' Shared an Awesome Skigit with You!', mail_body, mail_id, '', EMAIL_HOST_VIDEO)
                response_data['is_success'] = True
                response_data['message'] = 'Skigit Shared Successfully'
            else:
                response_data['is_success'] = False
        #         response_data['message'] = 'Trying to share skigit is not found.'
        # except ObjectDoesNotExist:
        #     response_data['is_success'] = False
        #     response_data['message'] = 'Skigit Share failed'
    return JsonResponse(response_data)

@csrf_protect
def i_am_following(request):
    """
        Follow Skigit User
    """
    response_data = {}
    is_success = False
    is_follow, message = None, None
    follow_id = request.POST.get('follow_id', None)
    skigit_id = request.POST.get('skigit_id', None)
    if request.is_ajax() and request.method == 'POST':

        if follow_id and follow_id is not None:
            if request.user.is_authenticated():
                follow_msg = 'Congratulations '
                follow_msg += request.user.username
                follow_msg += ' Started following you.'
                user = request.user
                is_found = User.objects.get(pk=follow_id)
                if is_found and is_found is not None:
                    try:
                        if Follow.objects.filter(follow=follow_id, user_id=user.id).exists():
                            is_follow = Follow.objects.filter(follow=follow_id, user_id=user.id).update(status=True)
                            is_success = True
                            if (notification_settings(is_found.id, 'follow_un_follow_notify')) == True:
                                if not (user == is_found):
                                    if not Notification.objects.filter(msg_type='follow', user=is_found,
                                                                       from_user=user).exists():
                                        Notification.objects.create(msg_type='follow', skigit_id=skigit_id, user=is_found,
                                                                    from_user=user, message=follow_msg)
                                    else:
                                        Notification.objects.filter(msg_type='follow', skigit_id=skigit_id, user=is_found,
                                                                    from_user=user).update(is_read=False,
                                                                                           message=follow_msg)
                            message = "Following Skigit"
                        else:
                            Follow.objects.create(follow=is_found, user=user, status=True)
                            if (notification_settings(is_found.id, 'follow_un_follow_notify')) == True:
                                if not (user.id == is_found):
                                    if not Notification.objects.filter(msg_type='follow', user=is_found,
                                                                       from_user=user).exists():
                                        Notification.objects.create(msg_type='follow', skigit_id=skigit_id,
                                                                    user=is_found, from_user=user, message=follow_msg)
                                    else:
                                        Notification.objects.filter(msg_type='follow', skigit_id=skigit_id,
                                                                    user=is_found, from_user=user).update(is_read=False,
                                                                                                         message=follow_msg)
                            message = "new entry in follow table"
                            is_success = True
                            is_follow = 1
                    except MultipleObjectsReturned:
                        message = "Oops ! Server Encounter An " \
                                  "Error Into This follow Skigit"
                        is_success = False
                        response_data['message'] = message
                        response_data['is_success'] = is_success
                        response_data['is_follow'] = is_follow
                        return JsonResponse(response_data)
                else:
                    message = "Invalid User Identity"
            else:
                message = "Please Login And Then Try To Follow User"
        else:
            message = "Skigit User Identity Not Found"
    else:
        message = "Invalid Request"
    response_data['message'] = message
    response_data['is_follow'] = is_follow
    response_data['is_success'] = is_success
    return JsonResponse(response_data)


@csrf_protect
def un_following(request):
    """
        Un Follow Skigit User
    """
    response_data = {}
    is_success = False
    is_follow, message = None, None
    follow_id = request.POST.get('follow_id', None)
    if request.is_ajax() and request.method == 'POST':
        user = request.user
        is_found = User.objects.get(pk=follow_id)
        if follow_id and follow_id is not None:
            if request.user.is_authenticated():
                if Follow.objects.filter(user=request.user.id, follow=follow_id, status=True).exists():
                    try:
                        is_follow = Follow.objects.filter(user=request.user.id, follow=follow_id,
                                                          status=True).update(status=False)
                        if not (user == is_found):
                            if Notification.objects.filter(msg_type='follow', user=is_found, from_user=user).exists():
                                Notification.objects.filter(msg_type='follow', user=is_found,
                                                            from_user=user).update(msg_type='unfollow_deleted',
                                                                                   is_read=True, is_active=False,
                                                                                   is_view=True)
                        is_success = True
                        message = "Un Follow User Sussessfully"
                    except MultipleObjectsReturned:
                        message = "Oops ! Server Encounter An " \
                                  "Error Into This Skigit Like"
                        is_success = False
                        response_data['message'] = message
                        response_data['is_success'] = is_success
                        response_data['is_follow'] = is_follow
                        return JsonResponse(response_data)
                else:
                    message = "Invalid follower Identity"
            else:
                message = "Please Login And Then Try To Unfollow Skigit User"
        else:
            message = "Skigit User Identity Not Found"
    else:
        message = "Invalid Request"
    response_data['message'] = message
    response_data['is_follow'] = is_follow
    response_data['is_success'] = is_success
    return JsonResponse(response_data)

@csrf_exempt
def skigit_statistics(request):
    response_data = {'is_success': False}
    like_count = plug_count = fav_count = view_count = share_count = 0
    if request.is_ajax() and request.method == 'POST':
        skigit = request.POST.get("skigit_id", "")

        try:
            like_count = Like.objects.filter(skigit__id=skigit, status=True).count()
        except:
             like_count = 0
        try:
            fav_count = Favorite.objects.filter(skigit__id=skigit, status=1, is_active=True).count()
        except:
            fav_count = 0
        try:
            plug_count = VideoDetail.objects.filter(plugged_skigit__id=skigit, is_plugged=True, status=1).count()
        except:
            plug_count = 0
        try:
            if VideoDetail.objects.filter(skigit_id__id=skigit, status=1).exists():
                vid = VideoDetail.objects.get(skigit_id__id=skigit, status=1)
                view_count = vid.view_count
            else:
                view_count = 0
        except:
            view_count = 0
        try:
            if Share.objects.filter(skigit_id=skigit, is_active=True).exists():
                share_count = Share.objects.filter(skigit_id=skigit, is_active=True).count()
        except:
            share_count = 0

        response_data['like_count'] = like_count
        response_data['fav_count'] = fav_count
        response_data['plug_count'] = plug_count
        response_data['view_count'] = view_count
        response_data['share_count'] = share_count
        response_data['is_success'] = True
        response_data['message'] = 'Statistic Count.'
    return JsonResponse(response_data)


@csrf_exempt
def skigit_i_like(request):
    """
     Like skigit
    """
    skigit_id, message, like_count, is_found, like = None, None, None, None, None
    is_success = False
    response_data = {}
    skigit_id = request.POST.get('skigit_id', None)
    if request.is_ajax() and request.method == 'POST':
        if skigit_id and skigit_id is not None:
            if request.user.is_authenticated():
                user = request.user
                is_found = Video.objects.filter(pk=skigit_id)

                if is_found and is_found is not None:
                    try:
                        if Like.objects.filter(skigit__id=skigit_id, user_id=user.id).exists():
                            like = Like.objects.filter(skigit__id=skigit_id, user_id=user.id).update(status=True)
                            is_success = True
                            message = "Skigit Liked"
                            if (notification_settings(is_found[0].user.id, 'like_notify')) == True:
                                if not(user.id == is_found[0].user.id):
                                    if not Notification.objects.filter(msg_type='like', skigit_id=is_found[0].id,
                                                                       user=is_found[0].user, from_user=user).exists():
                                        Notification.objects.create(msg_type='like', skigit_id=is_found[0].id,
                                                                    user=is_found[0].user, from_user=user,
                                                                    message='skigit_like')
                                    else:
                                        Notification.objects.filter(msg_type='like', skigit_id=is_found[0].id,
                                                                    user=is_found[0].user, from_user=user
                                                                    ).update(is_read=False, message='skigit_updated_like',
                                                                             )
                        else:
                            Like.objects.create(skigit=is_found[0], user=user, status=True, is_read=False)
                            if not (user == is_found[0].user):
                                if (notification_settings(is_found[0].user.id, 'like_notify')) == True:
                                    if not Notification.objects.filter(msg_type='like', skigit_id=is_found[0].id,
                                                                       user=is_found[0].user, from_user=user).exists():
                                        Notification.objects.create(msg_type='like', skigit_id=is_found[0].id,
                                                                    user=is_found[0].user, from_user=user,
                                                                    message='skigit_like')
                                    else:
                                        Notification.objects.filter(msg_type='like', skigit_id=is_found[0].id,
                                                                    user=is_found[0].user, from_user=user
                                                                    ).update(is_read=False, message='skigit_updated_like',
                                                                             )
                            message = "new entry in like table"
                            is_success = True
                            like = 1
                    except MultipleObjectsReturned:
                        message = "Oops ! Server Encounter An " \
                                  "Error Into This Skigit Like"
                        is_success = False
                        response_data['message'] = message
                        response_data['is_success'] = is_success
                        response_data['like'] = like
                        return JsonResponse(response_data)
                else:
                    message = "Invalid Skigit Identity"
            else:
                message = "Please Login And Then Try To Like Skigit"
        else:
            message = "Skigit Identity Not Found"
    else:
        message = "Invalid Request"
    response_data['message'] = message
    response_data['like'] = like
    response_data['is_success'] = is_success
    return JsonResponse(response_data)


@csrf_exempt
def skigit_i_unlike(request):
    skigit_id, message, like_count, is_found, unlike = None, None, None, None, None
    is_success = False
    response_data = {}
    skigit_id = request.POST.get('skigit_id', None)
    if request.is_ajax() and request.method == 'POST':
        user = request.user
        is_found = Video.objects.filter(pk=skigit_id)
        if skigit_id and skigit_id is not None:
            if request.user.is_authenticated():
                user = request.user
                if Like.objects.filter(skigit__id=skigit_id, user_id=user.id).exists():
                    try:
                        unlike = Like.objects.filter(skigit__id=skigit_id, user_id=user.id).update(status=False)
                        if Notification.objects.filter(msg_type='like', skigit_id=is_found[0].id,
                                                       user=is_found[0].user, from_user=user).exists():
                            Notification.objects.filter(msg_type='like', skigit_id=is_found[0].id, user=is_found[0].user, from_user=user
                                                        ).update(msg_type='unlike_deleted',
                                                                 message='Unlike', is_view=False,
                                                                 is_active=False, is_read=True)
                        is_success = True
                        message = ""
                    except MultipleObjectsReturned:
                        message = "Oops ! Server Encounter An " \
                                  "Error Into This Skigit Like"
                        is_success = False
                        response_data['message'] = message
                        response_data['is_success'] = is_success
                        response_data['unlike'] = unlike
                        return JsonResponse(response_data)
                else:
                    message = "Invalid Skigit Identity"
            else:
                message = "Please Login And Then Try To Like Skigit"
        else:
            message = "Skigit Identity Not Found"
    else:
        message = "Invalid Request"
    response_data['message'] = message
    response_data['unlike'] = unlike
    response_data['is_success'] = is_success
    return JsonResponse(response_data)


@csrf_exempt
def my_favourite_skigit(request):
    """
         Favourite skigit
    """
    response_data = {}
    is_success = False
    is_fav, message = None, None
    skigit_id = request.POST.get('skigit_id', None)
    if request.is_ajax() and request.method == 'POST':
        if skigit_id and skigit_id is not None:
            if request.user.is_authenticated():
                user = request.user
                is_found = Video.objects.filter(pk=skigit_id)
                if is_found and is_found is not None:
                    try:
                        if Favorite.objects.filter(skigit__id=skigit_id, user_id=user.id).exists():
                            is_fav = Favorite.objects.filter(skigit__id=skigit_id, user_id=user.id).update(status=1)
                            is_success = True
                            message = "Favorite Skigit"
                        else:
                            Favorite.objects.create(skigit=is_found[0], user=user, status=1)
                            message = "new entry in favorite table"
                            is_success = True
                            is_fav = 1
                    except MultipleObjectsReturned:
                        message = "Oops ! Server Encounter An " \
                                  "Error Into This Favorite Skigit"
                        is_success = False
                        response_data['message'] = message
                        response_data['is_success'] = is_success
                        response_data['is_fav'] = is_fav
                        return JsonResponse(response_data)
                else:
                    message = "Invalid Skigit Identity"
            else:
                message = "Please Login And Then Try To Like Skigit"
        else:
            message = "Skigit Identity Not Found"
    else:
        message = "Invalid Request"
    response_data['message'] = message
    response_data['is_fav'] = is_fav
    response_data['is_success'] = is_success
    return JsonResponse(response_data)


@csrf_exempt
def un_favourite_skigit(request):
    """
         Unfavoured skigit
    """
    response_data = {}
    is_success = False
    is_fav, message = None, None
    skigit_id = request.POST.get('skigit_id', None)
    if request.is_ajax() and request.method == 'POST':
        if skigit_id and skigit_id is not None:
            if request.user.is_authenticated():
                user = request.user
                if Favorite.objects.filter(skigit__id=skigit_id, user_id=user.id).exists():
                    try:
                        is_fav = Favorite.objects.filter(skigit__id=skigit_id, user_id=user.id).update(status=0)
                        is_success = True
                        message = "Unfavoured skigit"
                    except MultipleObjectsReturned:
                        message = "Oops ! Server Encounter An " \
                                  "Error Into This Skigit Like"
                        is_success = False
                        response_data['message'] = message
                        response_data['is_success'] = is_success
                        response_data['is_fav'] = is_fav
                        return JsonResponse(response_data)
                else:
                    message = "Invalid Skigit Identity"
            else:
                message = "Please Login And Then Try To Like Skigit"
        else:
            message = "Skigit Identity Not Found"
    else:
        message = "Invalid Request"
    response_data['message'] = message
    response_data['is_fav'] = is_fav
    response_data['is_success'] = is_success
    return JsonResponse(response_data)

@login_required(login_url='/')
def display_business_logo(request):
    """
    To retrive logo image and display in skigit upload form
    """
    bus_logo = None
    message = "Logo not found"
    is_success = False
    if request.method == 'POST' and request.is_ajax():
        bus_user_id = request.POST['bus_user_id']
        # Check whether the user exist or not
        is_user = User.objects.get(pk=bus_user_id)

        if is_user:
            bus_logo = Profile.objects.get(user=is_user)
            if bus_logo:
                bus_logo = bus_logo.logo_img.url
                message = "User exist"
                is_success = True
            else:
                message = "Logo not found"
                is_success = False
        else:
            message = "User not exist"
            is_success = False

    response_data = {
        "logo_main": bus_logo,
        "message": message,
        "is_success": is_success,
    }

    return JsonResponse(response_data)


def skigit_view_count(request):
    """
    To update view count of skigit
    """
    response_data = {}
    count = None
    is_success = None
    if request.method == 'POST' and request.is_ajax():
        skigit_id = request.POST['skigit_id']

        try:
            total_count = VideoDetail.objects.get(skigit_id=skigit_id)
            count = total_count.view_count + 1
            total_count.view_count = count
            total_count.save()
            is_success = True
        except ObjectDoesNotExist:
            is_success = False

        response_data['view_count'] = count
        response_data['is_success'] = is_success

        return JsonResponse(response_data)

def linked_in_share(request, pk):
    """
       Skigit Sharing on Linked In View
    """
    skigit = get_object_or_404(VideoDetail, pk=pk)
    u_profile = Profile.objects.get(user=skigit.skigit_id.user)
    company_logo_url = get_thumbnail(u_profile.profile_img, '100x100', quality=99).url
    video_share_url = None
    if skigit.business_logo:

        if skigit.made_by and skigit.business_logo.is_deleted is False:
            if skigit.business_logo:
                skigit_b_logo = get_thumbnail(skigit.business_logo.logo, '100x100', quality=99).url
                video_share_url = create_share_thumbnails(skigit, skigit.skigit_id.thumbnails.all()[0].url,
                                                          request.build_absolute_uri(skigit_b_logo),
                                                          request.build_absolute_uri(company_logo_url))
        else:
            if skigit.made_by:
                u_profile = Profile.objects.get(user=skigit.made_by)
                if u_profile.logo_img.filter(is_deleted=False).all().count() > 0:
                    blogo = u_profile.logo_img.filter(is_deleted=False).all()[0]
                    skigit_b_logo = get_thumbnail(blogo.logo, '100x100', quality=99).url
                    video_share_url = create_share_thumbnails(skigit, skigit.skigit_id.thumbnails.all()[0].url,
                                                              request.build_absolute_uri(skigit_b_logo),
                                                              request.build_absolute_uri(company_logo_url))
    else:
        video_share_url = create_share_thumbnails(skigit, skigit.skigit_id.thumbnails.all()[0].url)
    video_share_url1 = request.build_absolute_uri(video_share_url)
    return render(request, 'pages/linkedin.html', locals())


@receiver(user_signed_up)
def complete_social_signup(sender, **kwargs):
    """
    Receives user_signed_up signal and provides a hook for populating
    additional user data.
    The user_signed_up signal is sent when a user signs up for an account.
    This signal is typically
    followed by a user_logged_in, unless e-mail verification prohibits the user
    to log in.

    You may populate user data collected from social login's extra info, or
    other user data here.
    """
    user = kwargs.pop('user')
    request = kwargs.pop('request')
    if cache.get('account_type') == 'general':
        group = Group.objects.get(name=settings.GENERAL_USER)
    elif cache.get('account_type') == 'business':
        group = Group.objects.get(name=settings.BUSINESS_USER)
    else:
        group = Group.objects.get(name=settings.GENERAL_USER)
    user.groups.add(group)
    user.save()


@receiver(email_confirmed)
def email_confirmed_(request, email_address, **kwargs):
    """
        Email Confirmation View.
    """
    # new_email_address = EmailAddress.objects.get(email=email_address)
    user = User.objects.get(email=email_address.email)
    user.is_active = True
    messages.success(request, 'Your Account Activated SuccessFully')
    user.save()


@csrf_protect
def register(request):
    """
        User Registration View.
    """
    context = RequestContext(request)

    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password1'],
                email=form.cleaned_data['email'])

            context['user'] = user
            return render(request, 'registration/success.html', context)
    else:
        form = RegistrationForm()

    context = RequestContext(request, {'form': form})
    return render(request, 'registration/register.html', context)


@login_required(login_url='/')
def view_user_profile(request):
    """
        User Profile View
    """
    context = RequestContext(request)
    user = request.user

    try:
        is_business = is_user_business(user)
        context['is_business'] = is_user_business(user)
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
        pay_pal_token = client_PayPal_token(request)
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

        elif is_business and not Invoice.objects.filter(user=request.user, type='CreditCard', is_deleted=False).exists() and not \
                Invoice.objects.filter(user=request.user, type='PayPalAccount', is_deleted=False).exists() and is_business:
            messages.error(request, 'Payment information is not verified. Please verify payment method by '
                                    'filling PayPal or Credit/Debit card details.')
        elif is_business and request.user.profile.payment_method == '1' \
                and not Invoice.objects.filter(user=request.user, type='CreditCard', is_deleted=False).exists() and is_business:
            messages.error(request, 'Payment information is not verified. Please verify payment method by '
                                    'filling PayPal or Credit/Debit card details.')
        elif is_business and request.user.profile.payment_method == '0' \
                and not Invoice.objects.filter(user=request.user, type='PayPalAccount', is_deleted=False).exists() and is_business:
            messages.error(request, 'Payment information is not verified. Please verify payment method by '
                                    'filling PayPal or Credit/Debit card details.')
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

    if request.method == 'POST' and 'basic_profile_submit' in request.POST:
        context['backend_name'] = cache.get('backend')
        if user.is_superuser or (user.is_staff and is_general) or is_general:
            form1 = UserForm(request.POST, instance=request.user)
            form2 = ProfileForm(request.POST, request.FILES, instance=request.user.profile)

        elif is_business:
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

                message ="<table style='width:100%;' cellpadding='0' cellspacing='0'>"\
                         "<tr><td style='text-align:center;'><h3 style='color:#d22b2b;' margin-bottom:0;font-family: "+"Proza Libre"+", sans-serif;'>"\
                         "Account Verification Task - Admin </h3></td></tr>"\
                         "<tr><td><p style='text-align:justify;font-family: "+"Proza Libre"+", sans-serif;'>"\
                         "<span style='color:#1C913F;font-family: "+"Proza Libre"+", sans-serif;'>"+user.username+"</span> has joined skigit. please verify account information by clicking the link below.</p>"\
                         "<p><br/></p></td></tr>"\
                         "<tr><td style='text-align:center;'><a href='"+confirm+"' style='text-decoration:none;color:#0386B8;margin: 20px auto;display: table;font-weight: 700;font-size: 15px;font-family: "+"Proza Libre"+", sans-serif;'>"\
                         " User Account Verification </a></td></tr>"\
                         "<tr><td style='text-align:center; width:168px;'><img src='http://skigit.com/static/skigit/images/shair.png' style='width:165px;'/></td></tr>"\
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
            elif is_business and not Invoice.objects.filter(user=request.user, type='CreditCard', is_deleted=False).exists() and not \
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
    else:
        context['backend_name'] = cache.get('backend')
        Profile.objects.get_or_create(user=user)
        if user.is_superuser or (user.is_staff and is_general) or is_general:
            form1 = UserForm(instance=user)
            form2 = ProfileForm(instance=user.profile)
        elif is_business:
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


def handle_uploaded_file(f, unique_filename):
    """
        Updating file Uploading View.
    """
    file_path = "%s/media/skigit/profile/%s" % ((settings.BASE_DIR).replace('\\', '/'), unique_filename)
    with open(file_path, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)
    return file_path


def handle_uploaded_coupan_img(f, unique_filename):
    """
        Updating Coupan Image View.
    """
    file_path = "%s/media/skigit/coupan/%s" % ((settings.BASE_DIR).replace('\\', '/'), unique_filename)
    with open(file_path, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)
    return file_path


def handle_uploaded_business_logo(f, unique_filename):
    """
        Updating Business Logo View.
    """
    file_path = "%s/media/skigit/logo/%s" % ((settings.BASE_DIR).replace('\\', '/'), unique_filename)
    with open(file_path, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)
    return file_path


def handle_uploaded_video(f, unique_filename):
    """
        Video Updating/ Handleing View.
    """
    file_path = "%s/media/videos/%s" % ((settings.BASE_DIR).replace('\\', '/'), unique_filename)
    with open(file_path, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)
    return file_path


@csrf_exempt
@login_required(login_url='/')
def delete_business_logo(request):
    context = {}
    file_name = request.POST.get('file_name', '')
    user = request.user
    user.profile.logo_img.filter(logo=file_name).update(is_deleted=True)

    context.update({'is_success': "delete_success", 'message': "skigit/logo/%s" % file_name})

    return HttpResponse(json.dumps(context, cls=DjangoJSONEncoder),
                        content_type="application/json")


@csrf_exempt
@login_required(login_url='/')
def delete_extra_profile_image(request):
    context = {}
    file_name = request.POST.get('file_name', '')
    user = request.user
    user.profile.extra_profile_img.filter(profile_img=file_name).delete()

    context.update({'is_success': "delete_success", 'message': "%s" % file_name})

    return HttpResponse(json.dumps(context, cls=DjangoJSONEncoder),
                        content_type="application/json")


@csrf_exempt
@login_required(login_url='/')
def profile_extra_image(request):
    context = {}
    user = request.user
    unique_filename = uuid.uuid4()
    file_path = handle_uploaded_file(request.FILES['file'], unique_filename)

    user.profile.extra_profile_img.create(profile_img="skigit/profile/%s" % unique_filename)

    context.update({'is_success': "is_success", 'message': "skigit/profile/%s" % unique_filename,
                    "unique_filename": str(unique_filename)})

    return HttpResponse(json.dumps(context, cls=DjangoJSONEncoder),
                        content_type="application/json")


@csrf_exempt
@login_required(login_url='/')
def business_logo(request):
    context = {}
    user = request.user
    unique_filename = uuid.uuid4()

    file_path = handle_uploaded_business_logo(request.FILES['file'], unique_filename)
    user.profile.logo_img.create(logo="skigit/logo/%s" % unique_filename)
    context.update({'is_success': "is_success", 'message': "skigit/logo/%s" % unique_filename,
                    "unique_filename": str(unique_filename)})

    return HttpResponse(json.dumps(context, cls=DjangoJSONEncoder),
                        content_type="application/json")


@login_required(login_url='/')
def business_logo_get_target(request):
    user = request.user
    context = user.profile.logo_img.filter(is_deleted=False).values("logo")
    return HttpResponse(json.dumps(list(context), cls=DjangoJSONEncoder),
                        content_type="application/json")


@csrf_exempt
@login_required(login_url='/')
def profile_pic(request):
    context = {}
    user = request.user

    file_path = handle_uploaded_file(request.FILES['p_pic'], request.FILES['p_pic'].name)

    if not request.FILES['p_pic'].name.lower().endswith(('.jpg', '.jpeg', '.gif', '.png')):
        context.update(
            {'is_success': "is_success", 'message': "Please select valid file format like *.jpg, *.jpeg,*.gif ,*.png ",
             'valid_format': False})

        return HttpResponse(json.dumps(context, cls=DjangoJSONEncoder),
                            content_type="application/json")

    profile = Profile.objects.get(user=user)
    profile.profile_img = "skigit/profile/%s" % request.FILES['p_pic'].name
    profile.save()
    user.save()
    context.update({'is_success': "is_success", 'message': "skigit/profile/%s" % request.FILES['p_pic'].name,
                    'valid_format': True})

    return HttpResponse(json.dumps(context, cls=DjangoJSONEncoder),
                        content_type="application/json")


@csrf_exempt
@login_required(login_url='/')
def coupan_image_upload(request):
    context = {}
    user = request.user
    file_path = handle_uploaded_coupan_img(request.FILES['coupan_img'], request.FILES['coupan_img'].name)
    if not request.FILES['coupan_img'].name.lower().endswith(('.jpg', '.jpeg', '.gif', '.png')):
        context.update(
            {'is_success': "is_success", 'message': "Please select valid file format like *.jpg, *.jpeg,*.gif ,*.png ",
             'valid_format': False})
        return HttpResponse(json.dumps(context, cls=DjangoJSONEncoder), content_type="application/json")

    profile = Profile.objects.get(user=user)
    profile.coupan_image = "skigit/coupan/%s" % request.FILES['coupan_img'].name
    profile.save()
    user.save()
    context.update({'is_success': "is_success", 'message': "skigit/coupan/%s" % request.FILES['coupan_img'].name})
    return HttpResponse(json.dumps(context, cls=DjangoJSONEncoder), content_type="application/json")


@login_required(login_url='/')
def profile_get_target(request):
    context = {}
    user = request.user
    context = user.profile.extra_profile_img.values("profile_img")
    return HttpResponse(json.dumps(list(context), cls=DjangoJSONEncoder), content_type="application/json")


@csrf_protect
def login_ajax(request):
    context = {}
    if request.is_ajax() and request.method == 'POST':
        if request.POST is not None:
            try:
                username = request.POST.get('log', None)
                password = request.POST.get('pwd', None)

                base_location = request.POST.get('base_location', None)

                if base_location:
                    b_location = base_location.split('/?next=')
                    if len(b_location) > 1:
                        base_location = b_location[0]+b_location[-1]
                    else:
                        base_location = b_location[0]
                else:
                    base_location = '/'

                if User.objects.filter(email=username).exists():
                    user_name = User.objects.get(email=username).username
                    user = authenticate(username=user_name, password=password)
                    request.session['user_id'] = user.id
                    from django.contrib.auth import update_session_auth_hash
                else:
                    user = None

                if user is not None:
                    # Is the account active? It could have been disabled.
                    if user.is_active:
                        # If the account is valid and active, we can log the user in
                        # We'll send the user back to the homepage.
                        login(request, user)
                        is_success = True
                        message = "<span class='sign-error'><i class='glyphicon glyphicon-ok-circle' /></span><span class='text-error'>Your login was successful!</span>";
                        location = base_location
                    else:
                        # An inactive account was used - no logging in!
                        is_success = False
                        message = "<span class='sign-error'><i class='glyphicon glyphicon-remove-circle' /></span><span class='text-error'>Your account is inactivate. Please activate first then try to login.</span>";
                        location = base_location
                else:
                    # Bad login details were provided. So we can't log the user in.
                    is_success = False
                    message = "<span class='sign-error'><i class='glyphicon glyphicon-remove-circle' /></span><span class='text-error'>Your username and/or password are incorrect. Please try again.</span>";
                    location = base_location
            except Exception:
                is_success = False
                message = "<span class='sign-error'><i class='glyphicon glyphicon-remove-circle' /></span><span class='text-error'>Your username and/or password are incorrect. Please try again.</span>";
                location = 'None'
                pass
        else:
            is_success = False
            message = 'Require login parameter not found'
            location = '/'
    else:
        is_success = False
        message = 'Invalid Request'
        location = '/'

    context.update({'is_success': is_success, 'message': message, 'base_location': location})
    return HttpResponse(json.dumps(context, cls=DjangoJSONEncoder),
                        content_type="application/json")


def get_youtube_video_thumbnail(request):
    video_id = request.POST.get('video_id')
    vdo_obj = Video.objects.get(id=str(video_id))
    thumbnail = Thumbnail.objects.filter(video=vdo_obj)[0]
    thumbnail_url = thumbnail.url

    return HttpResponse(json.dumps({'url': thumbnail_url, 'is_success': True}), content_type="application/json")


def login_require(request):
    context = RequestContext(request)
    next = "/"

    if request.GET:
        next = request.GET['next']

    if request.user.is_authenticated():
        logout(request)
        return HttpResponseRedirect(next)
    elif request.method == 'POST' and 'login_submit_required' in request.POST:
        username = request.POST.get('log', None)
        password = request.POST.get('pwd', None)
        user = authenticate(username=username, password=password)
        if user:
            # Is the account active? It could have been disabled.
            if user.is_active:
                # If the account is valid and active, we can log the user in.
                # We'll send the user back to the homepage.
                login(request, user)
                return HttpResponseRedirect(next)
            else:
                # An inactive account was used - no logging in!
                context.update(csrf(request))
                context.update(
                    {'login_error': 'Your Skigit account is disabled.', 'next': next})
                return render(request, 'registration/login_required.html',
                                          context)
        else:
            # Bad login details were provided. So we can't log the user in.
            context.update(csrf(request))
            msg = "Invalid login details: {0}, {1}".format(username, password)
            context.update({'login_error': msg, 'next': next})
            return render(request, 'registration/login_required.html',
                                      context)
    else:
        context.update(csrf(request))
        context.update({'next': next})
        return render(request, 'registration/login_required.html', context)


def register_confirm(request, activation_key):
    context = RequestContext(request)

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


def register_type(request):
    context = RequestContext(request)

    if request.user.is_authenticated():
        return HttpResponseRedirect('/')
    elif request.method == 'POST':
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
                key_expires = datetime.datetime.today() + datetime.timedelta(6)

                # Save The Hash to user Profile
                new_profile = Profile(user=user, activation_key=activation_key, key_expires=key_expires)
                new_profile.save()

                email_subject = 'Welcome to Skigit!'
                confirm_path = "/register/confirm/%s" % activation_key
                confirm = request.build_absolute_uri(confirm_path)
                email_body ="<table style='width:100%;' cellpadding='0' cellspacing='0'>"\
                            "<tr><td style='text-align:center;'><h3 style='color:#0386B8; margin-bottom:0;font-family: "+"Proza Libre"+", sans-serif;'>"\
                            "Welcome to Skigit!</h3></td></tr>"\
                            "<tr><td style='text-align:center;'><h5 style='color:#1C913F; margin-top:10px; font-family: "+"Proza Libre"+", sans-serif;'>"\
                            "We're so glad you joined us!</h5></td></tr>"\
                            "<tr><td style='color:#222;'><p style='text-align:justify;'>"\
                            "Please click the link below so that we can confirm your email address. Without verification, you won't be able to establish an accounts and create Skigits.</p>"\
                            "<p>Thank you,<br/>Skigit</p></td></tr>"\
                            "<tr><td style='text-align:center;'><a href='" + confirm + "' style='text-decoration:none;color:#0386B8;margin: 20px auto;display: table;font-weight: 700;font-size: 15px; font-family: "+"Proza Libre"+", sans-serif;'> Click to verify your Email </a></td></tr>"\
                            "<tr><td style='text-align:center;width:165px;'><img src='http://skigit.com/static/skigit/images/shair.png' style='width:165px;'/></td></tr>"\
                            "</table>"\

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
                key_expires = datetime.datetime.today() + datetime.timedelta(6)

                # Save The Hash to user Profile
                new_profile = Profile(user=user, activation_key=activation_key,
                                      key_expires=key_expires)
                new_profile.save()

                email_subject = 'Welcome to Skigit | Skigit'
                confirm_path = "/register/confirm/%s" % activation_key
                confirm = request.build_absolute_uri(confirm_path)
                email_body ="<table style='width:100%;' cellpadding='0' cellspacing='0'>"\
                            "<tr><td style='text-align:center;'><h3 style='color:#0386B8; margin-bottom:0;font-family: "+"Proza Libre"+", sans-serif;'>"\
                            "Welcome to Skigit!</h3></td></tr>"\
                            "<tr><td style='text-align:center;'><h5 style='color:#1C913F; margin-top:10px; font-family: "+"Proza Libre"+", sans-serif;'>"\
                            "We're so glad you joined us!</h5></td></tr>"\
                            "<tr><td style='color: #222;'><p style='text-align:justify;'>"\
                            "Please click the link below so that we can confirm your email address. Without verification, you won't be able to establish an accounts and create Skigits.</p>"\
                            "<p>Thank you,<br/>Skigit</p></td></tr>"\
                            "<tr><td style='text-align:center;'><a href='" + confirm + "' style='text-decoration:none;color:#0386B8;margin: 20px auto;display: table;font-weight: 700;font-size: 15px; font-family: "+"Proza Libre"+", sans-serif;'> Click to verify your Email </a></td></tr>"\
                            "<tr><td style='text-align:center;width:165px;'><img src='http://skigit.com/static/skigit/images/shair.png' style='width:165px;'/></td></tr>"\
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

    else:
        context.update(csrf(request))
        return render(request,
            'registration/registration_type.html',
            context
        )


@login_required(login_url='/')
def user_profile_notifications(request):
    context = RequestContext(request)
    user = request.user
    context['is_business'] = is_user_business(user)
    field = 'user_profile_notification_submit'
    if request.method == 'POST' and field in request.POST:

        form1 = ProfileNotificationForm(request.POST, instance=user.profile)
        if form1.is_valid():
            form1.save()
            messages.success(request, 'eNotification settings updated successfully!')
            form1 = ProfileNotificationForm(instance=user.profile)
    else:

        form1 = ProfileNotificationForm(instance=user.profile)
        Profile.objects.get_or_create(user=user)

    user_profile = Profile.objects.get(user=user)
    context.update(csrf(request))
    context['form1'] = form1
    context['user'] = user
    context['user_profile'] = user_profile

    return render(request, 'profile/user_profile_eNotifications.html', context)


@login_required(login_url='/')
def my_statistics(request):
    context = RequestContext(request)
    context['is_business'] = is_user_business(request.user)
    skigit_count = VideoDetail.objects.filter(skigit_id__user=request.user,
                                              status=1, is_active=True).count()
    primary_count = VideoDetail.objects.filter(skigit_id__user=request.user, status=1,
                                               is_plugged=False, is_active=True).count()
    plug_in_count = VideoDetail.objects.filter(skigit_id__user=request.user, status=1,
                                               is_plugged=True, is_active=True).count()
    plug_in_my_skigit = VideoDetail.objects.filter(plugged_skigit__user=request.user, status=1,
                                                   is_plugged=True, is_active=True).count()
    like_count = Like.objects.filter(user=request.user, status=True).count()
    favorite_count = Favorite.objects.filter(user=request.user, status=1).count()
    follow_count = Follow.objects.filter(follow=request.user, status=True).count()
    follow_me_count = Follow.objects.filter(user=request.user, status=True).count()
    f_count1 = Friend.objects.filter(to_user=request.user.id, status='1').count()
    f_count2 = Friend.objects.filter(from_user=request.user.id, status='1').count()
    friend_count = f_count1 + f_count2
    share_count = Share.objects.filter(user=request.user, is_active=True).count()

    context.update({'skigit_count': skigit_count,
                    'primary_count': primary_count,
                    'plug_in_count': plug_in_count,
                    'plug_to_my_skigit': plug_in_my_skigit,
                    'like_count': like_count,
                    'favorite_count': favorite_count,
                    'follow_count': follow_count,
                    'follow_me_count': follow_me_count,
                    'friend_count': friend_count,
                    'share_count': share_count,
                    })

    return render(request, 'profile/my_statistics.html', context)


def all_statistic_count(request):
    context = RequestContext(request)
    skigit_count = VideoDetail.objects.filter(skigit_id__user=request.user,
                                              status=1, is_active=True).count()
    primary_count = VideoDetail.objects.filter(skigit_id__user=request.user, status=1,
                                               is_plugged=False, is_active=True).count()
    plug_in_count = VideoDetail.objects.filter(skigit_id__user=request.user, status=1,
                                               is_plugged=True, is_active=True).count()
    plug_in_my_skigit = VideoDetail.objects.filter(plugged_skigit__user=request.user, status=1,
                                                   is_plugged=True, is_active=True).count()
    like_count = Like.objects.filter(user=request.user, status=True).count()
    favorite_count = Favorite.objects.filter(user=request.user, status=1).count()
    follow_count = Follow.objects.exclude(user=request.user).filter(follow=request.user, status=True).count()
    follow_me_count = Follow.objects.exclude(follow=request.user).filter(user=request.user, status=True).count()
    f_count1 = Friend.objects.filter(to_user=request.user.id, status='1').count()
    f_count2 = Friend.objects.filter(from_user=request.user.id, status='1').count()
    friend_count = f_count1 + f_count2
    share_count = Share.objects.filter(user=request.user, is_active=True).count()

    context.update({'skigit_count': skigit_count,
                    'primary_count': primary_count,
                    'plug_in_count': plug_in_count,
                    'plug_to_my_skigit': plug_in_my_skigit,
                    'like_count': like_count,
                    'favorite_count': favorite_count,
                    'follow_count': follow_count,
                    'follow_me_count': follow_me_count,
                    'friend_count': friend_count,
                    'share_count': share_count,
                    })

    return render(request, 'profile/statistics_menu.html', context)


@login_required(login_url='/')
def user_profile_delete(request):
    context = RequestContext(request)
    user = request.user
    context['is_business'] = is_user_business(user)
    if request.method == 'POST' and 'user_profile_delete' in request.POST:
        delete_account = request.POST.get('delete-account', None)
        if delete_account == '1':
            User.objects.get(pk=request.user.id).delete()
            logout(request)
            messages.success(request, 'Your account deactivated successfully!')
            return HttpResponseRedirect('/')
        else:
            messages.error(request, 'There Is Something Wrong in deactivate')
    else:
        Profile.objects.get_or_create(user=user)

    user_profile = Profile.objects.get(user=user)
    context.update(csrf(request))
    context['user'] = user
    context['user_profile'] = user_profile
    return render(request, 'profile/user_profile_delete.html', context)


def reset_confirm(request, uidb64=None, token=None):

    # Wrap the built-in reset confirmation view and pass to it all the
    # captured parameters like uidb64, token
    # and template name, url to redirect after password reset is confirmed.
    return password_reset_confirm(
        request, template_name='registration/password_reset_confirm.html',
        uidb64=uidb64, token=token, post_reset_redirect=reverse('reset_done'))


def reset_done(request):
    context = RequestContext(request)
    return render(request, 'registration/password_reset_complete.html', context)


def reset_success(request):
    context = RequestContext(request)
    return render(request, 'registration/password_resets_done.html', context)


def reset(request):

    return password_reset(
        request, template_name='registration/password_reset_form.html',
        html_email_template_name='registration/password_reset_email.html',
        subject_template_name='registration/recovery_email_subject.txt',
        post_reset_redirect=reverse('reset_success')
    )


def logout_user(request):
    auth.logout(request)
    messages.info(request, 'You have successfully logged out')
    return render(request, 'template/logoutpage.html', {'logout_message': 'You have successfully logged out'})


def logout_page(request):
    messages.info(request, 'You have successfully logged out')
    return render(request, 'index.html', {'logout_message': 'You have successfully logged out'})


def aboust_us_view(request):
    context = RequestContext(request)
    return render(request, 'aboutus/about_us.html', context)


def faq_view(request):
    context = RequestContext(request)
    return render(request, 'aboutus/FAQ.html', context)


def privacy_policy_view(request):
    context = RequestContext(request)
    return render(request, 'aboutus/privacy_policy.html', context)


def t_and_c_view(request):
    context = RequestContext(request)
    return render(request, 'aboutus/t_and_c.html', context)


def acceptable_use_policy_view(request):
    context = RequestContext(request)
    return render(request, 'aboutus/acceptable_use_policy.html', context)


def copyright_policy_view(request):
    context = RequestContext(request)
    return render(request, 'aboutus/Copyright_policy.html', context)


def skigit_for_business_view(request):
    context = RequestContext(request)
    return render(request, 'aboutus/skigit_for_business.html', context)


def business_terms_of_service(request):
    context = RequestContext(request)
    return render(request, 'aboutus/businessvalueservicesandfees.html', context)


def rules_for_your_company_skigit(request):
    context = RequestContext(request)
    return render(request, 'aboutus/rules_for_your_company_skigit.html', context)


def investors_view(request):
    context = RequestContext(request)
    return render(request, 'aboutus/Investors.html', context)


def guidelines_view(request):
    context = RequestContext(request)
    return render(request, 'guidelines/guidelines.html', context)


def skigitology_view(request):
    context = RequestContext(request)
    return render(request, 'guidelines/skigitology.html', context)


def skigit_length_view(request):
    context = RequestContext(request)
    return render(request, 'guidelines/skigit_length.html', context)


def making_your_skigit_view(request):
    context = RequestContext(request)
    template = 'guidelines/making_your_skigit_view.html'
    return render(request, template, context)


def allowed_video_formats_view(request):
    context = RequestContext(request)
    template = 'guidelines/allowed_video_formats_view.html'
    return render(request, template, context)


def _video_params(request, video_id):
    width = request.GET.get("width", "70%")
    height = request.GET.get("height", "350")
    origin = request.get_host()
    return {"video_id": video_id, "origin": origin, "width": width, "height": height}


@login_required(login_url='/')
def get_sperk(request):
    if request.is_ajax() and request.method == 'POST':
        incentive_detail = None
        user_id = request.POST.get('user_id', None)

        if not user_id:
            data = {'incentive_detail': incentive_detail, 'all_business_logo': ''}
            return HttpResponse(json.dumps(data), content_type="application/json")

        incentive_detail = None
        default_incentive_msg = 'This maker is not offering any Skigit incentives at this time. Check back later!'
        try:
            usr = User.objects.get(id=int(user_id))
        except:
            # incentive_detail = default_incentive_msg
            incentive_detail = None
        if user_id and Profile.objects.filter(user=usr, incentive=1).exists():
            incentive_detail = Profile.objects.get(user=usr).skigit_incentive
            if not incentive_detail:
                incentive_detail = None
        all_business_logo = []
        # get business logo
        profile = Profile.objects.filter(user=usr)
        for prof in profile:
            if prof.logo_img.filter(is_deleted=False).all():
                all_logo_obj = prof.logo_img.filter(is_deleted=False).all()
                for l_obj in all_logo_obj:
                    tmp = []
                    tmp.append(l_obj.id)
                    tmp.append(l_obj.logo.url)
                    all_business_logo.append(tmp)
                    del tmp
        data = {'incentive_detail': incentive_detail, 'all_business_logo': all_business_logo}

        return HttpResponse(json.dumps(data), content_type="application/json")


def get_logo(request):
    """
        Business Logo
    """
    selected_business_user = request.POST.get('buser', None)
    profile = Profile.objects.get(user=selected_business_user)
    busiless_logo = profile.logo_img.filter(is_deleted=False).first.logo
    return HttpResponse(json.dumps({"incentive_detail": busiless_logo}), content_type="application/json")


@payment_required
@require_filled_profile
def category_view(request):
    return render(request, 'sk_cat/category.html', {
        'category': Category.objects.all(),
    })


@payment_required
@require_filled_profile
def category_detail_view(request, cat_slug, template='sk_cat/category_bash.html',
                         page_template='sk_cat/category_body.html'):
    video_detail = []
    profile_dic = []
    like_dict = []
    share_dict = []
    plug_dict = []

    category_current = Category.objects.get(cat_slug=cat_slug)
    vid_latest_uploaded = VideoDetail.objects.select_related('skigit_id')
    vid_latest_uploaded = vid_latest_uploaded.filter(status=1, is_active=True)
    vid_latest_uploaded = vid_latest_uploaded.filter(category=category_current)

    if request.method == 'POST' and request.POST.get('sort', '') == '0':

        vid_latest_uploaded = vid_latest_uploaded.order_by('updated_date')

        if vid_latest_uploaded:
            vid_latest_uploaded = vid_latest_uploaded[0]
        videos = VideoDetail.objects.filter(category=category_current, status=1,
                                            is_active=True).order_by('updated_date')
        for vid in videos:
            like_count = Like.objects.filter(skigit=vid.skigit_id, status=True).count()
            like_dict.append({'id': vid.id, 'count': like_count})
            video_share = Share.objects.filter(skigit_id=vid, is_active=True).count()
            share_dict.append({'id': vid.id, 'count': video_share})
            video_plug = VideoDetail.objects.filter(plugged_skigit=vid.skigit_id, is_plugged=True, status=1).count()
            plug_dict.append({'id': vid.id, 'count': video_plug})
            video_detail.append(vid)
            if vid.made_by:
                us_profile = Profile.objects.get(user=vid.made_by)
                if us_profile.logo_img.filter(is_deleted=False).all().count()>0:
                    vid.default_business_logo = us_profile.logo_img.filter(is_deleted=False).all()[0]
                else:
                    vid.default_business_logo = ''
            else:
                vid.default_business_logo = ''
            video_detail.append(vid)

        ski_share_list = []
        for vid_data in videos:
            sharObj = Share.objects.filter(skigit_id=vid_data, is_active=True,
                                           user=request.user.id).order_by('to_user', '-pk').distinct('to_user')
            for sh in sharObj:
                ski_share_list.append({'share_date': sh.created_date, 'username': sh.to_user.username,
                                       'vid': sh.skigit_id_id})

        like_skigit = []
        video_likes = Like.objects.filter(user_id=request.user.id, status=True)
        for likes in video_likes:
            like_skigit.append(likes.skigit_id)
        context = {
            'page_template': page_template,
            'category_current': category_current,
            'video_detail': video_detail,
            'vid_latest_uploaded': vid_latest_uploaded,
            'video_share': share_dict,
            'video_plug': plug_dict,
            'video_likes': like_skigit,
            'like_count': like_dict,
            'skigit_list': ski_share_list,
            'order': 1,
            'order_title':  1,
            'order_views': 1,
            'order_random': 1,
            'order_likes': 1,
            'page_type': 'categorys',
            'users': get_all_logged_in_users()
        }
        if request.is_ajax():
            template = page_template
        return render(request, template, context)
    else:
        vid_latest_uploaded = vid_latest_uploaded.order_by('-updated_date')
        ski_share_list = []
        if vid_latest_uploaded:
            vid_latest_uploaded = vid_latest_uploaded[0]
        videos = VideoDetail.objects.filter(category=category_current, status=1, is_active=True).order_by('-updated_date')
        for vid in videos:
            like_count = Like.objects.filter(skigit=vid.skigit_id, status=True).count()
            like_dict.append({'id': vid.id, 'count': like_count})
            video_share = Share.objects.filter(skigit_id=vid, is_active=True).count()
            share_dict.append({'id': vid.id, 'count': video_share})
            video_plug = VideoDetail.objects.filter(plugged_skigit=vid.skigit_id, is_plugged=True, status=1).count()
            plug_dict.append({'id': vid.id, 'count': video_plug})
            sharObj = Share.objects.filter(skigit_id=vid, is_active=True, user=request.user.id).order_by('to_user', '-pk').distinct('to_user')
            for sh in sharObj:
                ski_share_list.append(
                    {'share_date': sh.created_date, 'username': sh.to_user.username, 'vid': sh.skigit_id_id})
            if vid.made_by:
                us_profile = Profile.objects.get(user=vid.made_by)
                if us_profile.logo_img.filter(is_deleted=False).all().count()> 0:
                    vid.default_business_logo = us_profile.logo_img.filter(is_deleted=False).all()[0]
                else:
                    vid.default_business_logo = ''
            else:
                vid.default_business_logo = ''
            video_detail.append(vid)
        like_skigit = []
        video_likes = Like.objects.filter(user_id=request.user.id, status=True)
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

    context = {
        'page_template': page_template,
        'category_current': category_current,
        'video_detail': video_detail,
        'page_template': page_template,
        'vid_latest_uploaded': vid_latest_uploaded,
        'friend_list': friend_list,
        'video_share': share_dict,
        'video_plug': plug_dict,
        'video_likes': like_skigit,
        'like_count': like_dict,
        'skigit_list': ski_share_list,
        'order': 1,
        'order_views': 1,
        'order_title': 1,
        'order_random': 1,
        'order_likes': 1,
        'page_type': 'categorys',
        'users': get_all_logged_in_users()
    }
    if request.is_ajax():
        template = page_template
    return render(request, template, context)


def popup_page(request, video_id):
    """
    Displays a video in an embed player
    """

    context = RequestContext(request)

    try:

        vid = VideoDetail.objects.select_related('skigit_id').get(
            skigit_id__id=video_id
        )
        user = None
        user_profile = None
        is_followed = Follow.objects.filter(
            user_id=request.user.id,
            follow_id=vid.skigit_id.user_id
        )

        inapp_reasons = InappropriateSkigitReason.objects.all()
        context.update({'inapp_reasons': inapp_reasons})
        context.update({'is_followed': is_followed})

        video_likes = Like.objects.filter(user_id=request.user.id, status=True)
        like_dict = []
        for likes in video_likes:
            like_dict.append(likes.skigit_id)

        if request.user.is_authenticated():
            user = User.objects.get(pk=request.user.id)
            user_profile = Profile.objects.get(user=user)
            fields = [
                user_profile.profile_img,
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
                user_profile = Profile.objects.get(user=user)

        # query below return uploaded latest 7 videos by user whos video
        # opend in popup
        skigits_might_like = VideoDetail.objects.select_related(
            'skigit_id'
        ).filter(
            skigit_id__user=vid.skigit_id.user,
            status=True
        ).exclude(
            skigit_id__id=video_id
        ).order_by('-updated_date')[:5]

        social_redirect_path = '%s%s' % (
            settings.SOCIAL_REDIRECT_URL, video_id
        )
        social_redirect_url = request.build_absolute_uri(social_redirect_path)

        context.update({
            'vid': vid,
            'user': user,
            'user_profile': user_profile,
            'skigits_might_like': skigits_might_like,
            'social_redirect_url': social_redirect_url,
            'video_likes': like_dict,
        })

        return render(request, "youtube/yt_popuppage.html", context)

    except ObjectDoesNotExist:
        messages.error(request, 'Skigit details not found...!!!')
        return HttpResponseRedirect('/')


def skigit_data(request, pk):

    video_likes = []
    all_reasion = []
    video_favorite = []
    video_follow = []
    ski_share_list = []

    if VideoDetail.objects.filter(id=pk):
        skigit = get_object_or_404(VideoDetail, pk=pk)

    else:
        return HttpResponseRedirect("/?id=%s" % pk)
    context = RequestContext(request)

    current_date = datetime.datetime.now().date
    user = request.user
    embed_skigit = EmbedInvoice.objects.filter(skigit_user__id=skigit.skigit_id.user.id, user__id=request.user.id,
                                               billing_month=current_date, embed_ski=skigit).exists()
    if not user.is_anonymous():
        type = get_user_type(user)
        if type == 'general':
           is_business = False
        elif type == 'business':
           is_business = True
    else:
        is_business = False

    time_zone = request.GET.get('time_zone', '')
    count_i_plugged_into = 0
    related_user_list = get_related_users(request, skigit.skigit_id.user.id)
    all_sub_cat_skigits = VideoDetail.objects.exclude(id=pk).filter(Q(subject_category=skigit.subject_category) |
                                                                    Q(skigit_id__user__in=related_user_list),
                                                                    status=1, is_active=True).order_by('?')
    if not request.user.is_anonymous():
        count_i_plugged_into = VideoDetail.objects.filter(plugged_skigit__user=request.user, status=1,
                                                          is_plugged=True).count()
    if request.user.is_authenticated():
        video_likes = Like.objects.filter(user_id=request.user.id, status=True).values_list("skigit_id__id", flat=True)
        all_reasion = InappropriateSkigitReason.objects.values('id', 'reason_title')
        video_favorite = Favorite.objects.filter(user_id=request.user.id,
                                                 status=1).values_list("skigit_id__id", flat=True)
        video_follow = Follow.objects.filter(user=request.user.id, status=True).values_list("follow__id", flat=True)

    profile_dic = []
    for vid_profile in all_sub_cat_skigits:
        if vid_profile.made_by:
            us_profile = Profile.objects.get(user=vid_profile.made_by)
            us_profile.made_by = vid_profile.made_by.id
            if us_profile.logo_img.filter(is_deleted=False).all().count() > 0:
                us_profile.business_logo = us_profile.logo_img.filter(is_deleted=False).all()[0]
                profile_dic.append(us_profile)
    profile_dic = list(set(profile_dic))
    current_view_count = skigit.view_count
    video_share_url = None
    u_profile = Profile.objects.get(user=skigit.skigit_id.user)
    company_logo_url = get_thumbnail(u_profile.profile_img, '100x100', quality=99).url

    if skigit.business_logo:

        if skigit.made_by and skigit.business_logo.is_deleted is False:
            if skigit.business_logo:
                skigit_b_logo = get_thumbnail(skigit.business_logo.logo, '100x100', quality=99).url
                video_share_url = create_share_thumbnails(skigit, skigit.skigit_id.thumbnails.all()[0].url,
                                                          request.build_absolute_uri(skigit_b_logo),
                                                          request.build_absolute_uri(company_logo_url))
        else:
            if skigit.made_by and skigit.business_logo.is_deleted is True:
                u_profile = Profile.objects.get(user=skigit.made_by)
                if u_profile.logo_img.filter(is_deleted=False).all().count() > 0:
                    blogo = u_profile.logo_img.filter(is_deleted=False).all()[0]
                    skigit_b_logo = get_thumbnail(blogo.logo, '100x100', quality=99).url
                    video_share_url = create_share_thumbnails(skigit, skigit.skigit_id.thumbnails.all()[0].url,
                                                              request.build_absolute_uri(skigit_b_logo),
                                                              request.build_absolute_uri(company_logo_url))
    else:
        video_share_url = create_share_thumbnails(skigit, skigit.skigit_id.thumbnails.all()[0].url)

    share_obj = Share.objects.exclude(to_user=request.user.id).filter(skigit_id__id=skigit.id, is_active=True,
                                                                      user=request.user.id
                                                                      ).order_by('to_user', '-pk').distinct('to_user')
    if share_obj:
        for sh in share_obj:
            share_date = datetime.datetime.strptime(str(sh.created_date.date()), '%Y-%m-%d').strftime('%d-%b-%Y')
            ski_share_list.append({'share_date': share_date, 'username': sh.to_user.username, 'vid': sh.skigit_id_id})

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
    context = {
        "skigit": skigit,
        "video_likes": video_likes,
        "embed_skigit_vid": embed_skigit,
        "all_reasion": all_reasion,
        "all_sub_cat_skigits": all_sub_cat_skigits,
        "video_favorite": video_favorite,
        "video_favorite_count": video_favorite,
        "count_i_plugged_into": count_i_plugged_into,
        "default_logo": profile_dic,
        "video_follow": video_follow,
        "friend_list": friend_list,
        "skigit_list": ski_share_list,
        "is_business": is_business,
        "users": get_all_logged_in_users(),
        "video_share_url": request.build_absolute_uri(video_share_url),
    }

    return render(request, "includes/skigit_popup.html", context)


def social_redirect(request, video_id):
    context = RequestContext(request)
    user, vid, category, user_profile, video_likes, category_current = None, None, None, None, None, None

    vid = VideoDetail.objects.select_related('skigit_id').get(
        skigit_id__id=video_id)

    if request.user.is_authenticated():
        user = User.objects.get(pk=request.user.id)
        user_profile = Profile.objects.get(user=user)
        if user_profile.profile_img == '' or user_profile.profile_img is None or user.username == '' or user.username is None or user.first_name == '' or user.first_name is None or user.last_name == '' or user.last_name is None or user.email == '' or user.email is None or user_profile.birthdate == '' or user_profile.birthdate is None or user_profile.language == '' or user_profile.language is None or user_profile.country == '' or user_profile.country is None or user_profile.state == '' or user_profile.state is None or user_profile.city == '' or user_profile.city is None or user_profile.zip_code == '' or user_profile.zip_code is None:
            user_profile = Profile.objects.get(user=user)

    # query below return uploaded latest 7 videos by
    # user whos video opend in popup
    skigits_might_like = VideoDetail.objects.select_related(
        'skigit_id'
    ).filter(
        skigit_id__user=vid.skigit_id.user, status=1
    ).exclude(
        skigit_id__id=video_id
    ).order_by('-updated_date')[:5]

    context.update({
        'vid': vid,
        'user': user,
        'user_profile': user_profile,
        'skigits_might_like': skigits_might_like,
    })

    return render(request, "social_share/social_share.html", context)


@login_required(login_url='/')
def display_business_logo(request):
    """
    To retrive logo image and display in skigit upload form
    """
    bus_logo = None
    message = "Logo not found"
    is_success = False
    if request.method == 'POST' and request.is_ajax():
        bus_user_id = request.POST['bus_user_id']
        # Check whether the user exist or not
        is_user = User.objects.get(pk=bus_user_id)

        if is_user:
            bus_logo = Profile.objects.get(user=is_user)
            if bus_logo:
                bus_logo = bus_logo.logo_img.url
                message = "User exist"
                is_success = True
            else:
                message = "Logo not found"
                is_success = False
        else:
            message = "User not exist"
            is_success = False

    response_data = {
        "logo_main": bus_logo,
        "message": message,
        "is_success": is_success,
    }

    return JsonResponse(response_data)


def skigit_view_count(request):
    """
    To update view count of skigit
    """
    response_data = {}
    count = None
    is_success = None
    if request.method == 'POST' and request.is_ajax():
        skigit_id = request.POST['skigit_id']

        try:
            total_count = VideoDetail.objects.get(skigit_id=skigit_id)
            count = total_count.view_count + 1
            total_count.view_count = count
            total_count.save()
            is_success = True
        except ObjectDoesNotExist:
            is_success = False

        response_data['view_count'] = count
        response_data['is_success'] = is_success

        return JsonResponse(response_data)


def get_inapp_reason(request):
    # if request.method == 'GET' and request.is_ajax():
    if request.user.is_authenticated():
        user_id = request.user.id
        all_reasion = InappropriateSkigitReason.objects.values('id', 'reason_title')
        return HttpResponse(json.dumps(all_reasion), content_type="application/json")


@csrf_exempt
def skigit_inapp_reason(request):
    """
        To save data of inappropriate skigit reason form data
    """
    response_data = {}
    if request.method == 'POST' and request.is_ajax():

        skigit_id = request.POST.get('skigit_id', None)
        reason_id = request.POST.get('skigit_reasons', None)
        user_id = None
        message = None

        if request.user.is_authenticated():
            user_id = request.user.id

            if reason_id is not None:
                is_success = True

                try:
                    inapp_instance = InappropriateSkigit()
                    inapp_instance.skigit = VideoDetail.objects.get(skigit_id=skigit_id)
                    inapp_instance.reported_user = request.user
                    inapp_instance.reason = InappropriateSkigitReason.objects.get(pk=reason_id)
                    inapp_instance.action = '0'
                    inapp_instance.save()
                except ObjectDoesNotExist:
                    is_success = False
                    message = "Invalid details found!"
            else:
                is_success = False
                message = "Please select a reason!"
        else:
            is_success = False
            message = "Please login first!"

        response_data['skigit_id'] = skigit_id
        response_data['user_id'] = user_id
        response_data['reason_id'] = reason_id
        response_data['is_success'] = is_success
        response_data['message'] = message
        return JsonResponse(response_data)


def inappropriateskigit_status_save(request):
    inappid = request.GET.get("inappid", None)
    status_id = request.GET.get("status_id", None)
    response_data={}
    response_data['inappid'] = inappid
    response_data['status_id'] = status_id
    obj = InappropriateSkigit.objects.get(pk=inappid)
    obj.status = status_id
    obj.save()
    return JsonResponse(response_data)


def get_username(request):
    """
        Comment: Function For Get Users Name.
        Args:
            request: Requested user information
    """
    response_data = {}
    is_success = False
    message = None
    users = {}

    if request.method == 'POST' and request.is_ajax():
        keyword = request.POST.get('keyword', None)
        if request.user.is_authenticated():
            try:
                users = list(
                    User.objects.filter(username__startswith=keyword).exclude(
                        pk=request.user.id).values('username'))

                is_success = True
                message = "Matched username"
            except:
                is_success = False
                message = "No match found for your request"

    response_data['is_success'] = is_success
    response_data['message'] = message
    response_data['users'] = users
    return JsonResponse(response_data)


@login_required(login_url='/')
@payment_required
@require_filled_profile
def user_profile_display(request, username):
    """
        Comment: User profile Display Function
        Args:
            request: requested user
            username: User name of user

        Returns: User profile display
    """
    context = RequestContext(request)
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
        extra_profile_img_url = [get_thumbnail(profile_img.profile_img, '300x120', quality=99, format='PNG').url for profile_img in extra_profile_img]

    if request_user.is_superuser or (request_user.is_staff and is_user_general(request_user)) or is_user_general(
            request_user):
        user_template = 'profile/general_user_profile.html'
    elif request_user.groups.all()[0].name == settings.BUSINESS_USER:
        user_template = 'profile/busieness_user_profile.html'
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

        if Embed.objects.filter(to_user=request_user_profile, is_embed=True).exists():
            embed_skigit_list = Embed.objects.filter(to_user=request_user_profile, is_embed=True).values_list('skigit_id', flat=True)

            if request.user.is_authenticated():
                if Friend.objects.filter(Q(to_user=request.user.id) | Q(from_user=request.user.id), status=1).exists():
                    f_list = Friend.objects.filter(Q(to_user=request.user.id) | Q(from_user=request.user.id), status=1)
                    from_user_list = f_list.exclude(from_user=request.user.id).values_list('from_user',
                                                                                           flat=True).distinct()
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
                video_likes = Like.objects.filter(user_id=request.user.id, status=True)
                for likes in video_likes:
                    like_dict.append(likes.skigit_id)
            vid = VideoDetail.objects.select_related('skigit_id').filter(skigit_id__id__in=embed_skigit_list)
            serializer = VideoDetailSerializer(vid, many=True)
            for vid_data in vid:
                sharObj = Share.objects.filter(skigit_id=vid_data, is_active=True, user=request_user_profile).order_by(
                    'to_user', '-pk').distinct('to_user')
                for sh in sharObj:
                    ski_share_list.append(
                        {'share_date': sh.created_date, 'username': sh.to_user.username, 'vid': sh.skigit_id_id})
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


@payment_required
@require_filled_profile
def awesome_things(request):
    context = RequestContext(request)

    awesome_cat = SubjectCategory.objects.filter(is_active=True).order_by(
        'sub_cat_name')
    if awesome_cat:
        context.update({'awesome_cat': awesome_cat})
    return render(request, "sk_cat/awesome_category.html", context)


@login_required(login_url='/')
@payment_required
@require_filled_profile
def awesome_things_category(request, sub_cat_slug, template='sk_cat/skigit_plugged_into.html',
                            page_template='sk_cat/skigit_plugged_body.html'):

    user = vid = category = user_profile = video_likes = category_current = None
    like_dict = []
    friend_list = []
    share_dict = []
    plug_dict = []
    ski_share_list = []

    try:
        category_current = SubjectCategory.objects.get(
            sub_cat_slug=sub_cat_slug)
        vid = VideoDetail.objects.select_related('skigit_id').filter(
            subject_category=category_current, status=1).order_by(
            '-updated_date')
        for vid_profile in vid:
            like_count = Like.objects.filter(skigit=vid_profile.skigit_id, status=True).count()
            like_dict.append({'id': vid_profile.id, 'count': like_count})
            video_share = Share.objects.filter(skigit_id=vid_profile, is_active=True).count()
            share_dict.append({'id': vid_profile.id, 'count': video_share})
            video_plug = VideoDetail.objects.filter(plugged_skigit=vid_profile.skigit_id, is_plugged=True, status=1).count()
            plug_dict.append({'id': vid_profile.id, 'count': video_plug})

        for vid_data in vid:
            sharObj = Share.objects.filter(skigit_id=vid_data, is_active=True, user=request.user.id).order_by('to_user', '-pk').distinct('to_user')
            for sh in sharObj:
                ski_share_list.append(
                    {'share_date': sh.created_date, 'username': sh.to_user.username, 'vid': sh.skigit_id_id})
    except ObjectDoesNotExist:
        messages.error(request, 'Your Requested Awesome things not found...!!!')
        return HttpResponseRedirect("/")

    like_skigit = []
    if request.user.is_authenticated():
        video_likes = Like.objects.filter(user_id=request.user.id, status=True)
        for likes in video_likes:
            like_skigit.append(likes.skigit_id)

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

    context = {
        'video_detail': vid,
        'category_current': category_current,
        'user': user,
        'user_profile': user_profile,
        'video_likes': like_skigit,
        'like_count': like_dict,
        'video_type': 'sub_cat',
        'friend_list': friend_list,
        'video_share': share_dict,
        'video_plug': plug_dict,
        'skigit_list': ski_share_list,
        'users': get_all_logged_in_users()
    }

    if request.is_ajax():
        template = page_template
    return render(request, template, context)


@login_required(login_url='/')
@payment_required
@require_filled_profile
def my_skigits(request, user_id=None, template='category/my_skigits.html',
        page_template='includes/skigit_list.html'):

    user = vid = category = user_profile = video_likes = category_current = None
    like_dict = []
    profile_dic = []
    share_dict = []
    plug_dict = []
    try:
        category_current = request.user.username
        vid = VideoDetail.objects.select_related('skigit_id').filter(
            skigit_id__user=request.user, status=1, is_active=True).order_by('-updated_date')
        for vid_profile in vid:
            likes_count = Like.objects.filter(skigit=vid_profile.skigit_id, status=True).count()
            like_dict.append({'id': vid_profile.id, 'count': likes_count})
            video_share = Share.objects.filter(skigit_id=vid_profile, is_active=True).count()
            share_dict.append({'id': vid_profile.id, 'count': video_share})
            video_plug = VideoDetail.objects.filter(plugged_skigit=vid_profile.skigit_id,
                                                    is_plugged=True, status=1).count()
            plug_dict.append({'id': vid_profile.id, 'count': video_plug})
            if vid_profile.made_by:
                us_profile = Profile.objects.get(user=vid_profile.made_by)
                us_profile.made_by = vid_profile.made_by.id
                if us_profile.logo_img.filter(is_deleted=False).all().count() > 0:
                    us_profile.business_logo = us_profile.logo_img.filter(is_deleted=False).all()[0]
                    profile_dic.append(us_profile)
        profile_dic = list(set(profile_dic))

        ski_share_list = []
        for vid_data in vid:
            sharObj = Share.objects.filter(skigit_id=vid_data, is_active=True,
                                           user=request.user.id).order_by('to_user', '-pk').distinct('to_user')
            for sh in sharObj:
                ski_share_list.append(
                    {'share_date': sh.created_date, 'username': sh.to_user.username, 'vid': sh.skigit_id_id})

    except ObjectDoesNotExist:
        messages.error(request, 'No Skigits found...!!!')
        return HttpResponseRedirect("/")

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
    context = {
        'video_detail': vid,
        'category_current': category_current,
        'user': user,
        'user_profile': user_profile,
        'video_likes': like_skigit,
        'like_count': like_dict,
        'default_logo': profile_dic,
        'friend_list': friend_list,
        'video_share': share_dict,
        'video_plug': plug_dict,
        'skigit_list': ski_share_list,
        'users': get_all_logged_in_users()
    }
    if request.is_ajax():
        template = page_template
    return render(request, template, context)


@login_required(login_url='/')
@payment_required
@require_filled_profile
def my_skigits_view(request, user_id, template='sk_cat/skigit_plugged_into.html',
                            page_template='sk_cat/skigit_plugged_body.html'):

    user = us_profile = vid = category = user_profile = video_likes = category_current = None

    like_dict = []
    profile_dic = []
    share_dict = []
    plug_dict = []
    ski_share_list = []
    try:
        category_current = request.user.username
        vid = VideoDetail.objects.select_related('skigit_id').filter(
            skigit_id__user=user_id,
            status=True
        ).order_by('-updated_date')

        for vid_profile in vid:
            like_count = Like.objects.filter(skigit=vid_profile.skigit_id, status=True).count()
            like_dict.append({'id': vid_profile.id, 'count': like_count})
            video_share = Share.objects.filter(skigit_id=vid_profile, is_active=True).count()
            share_dict.append({'id': vid_profile.id, 'count': video_share})
            video_plug = VideoDetail.objects.filter(plugged_skigit=vid_profile.skigit_id, is_plugged=True, status=1).count()
            plug_dict.append({'id': vid_profile.id, 'count': video_plug})
            if vid_profile.made_by:
                us_profile = Profile.objects.get(user=vid_profile.made_by)
                us_profile.made_by = vid_profile.made_by.id
                if us_profile.logo_img.filter(is_deleted=False).all().count()>0:
                    us_profile.business_logo = us_profile.logo_img.filter(is_deleted=False).all()[0]
                profile_dic.append(us_profile)
        profile_dic = list(set(profile_dic))

        for vid_data in vid:
            sharObj = Share.objects.filter(skigit_id=vid_data, is_active=True, user=request.user.id).order_by('to_user', '-pk').distinct('to_user')
            for sh in sharObj:
                ski_share_list.append(
                    {'share_date': sh.created_date, 'username': sh.to_user.username, 'vid': sh.skigit_id_id})

    except ObjectDoesNotExist:
        messages.error(request, 'No Skigits found...!!!')
        return HttpResponseRedirect("/")
    user = User.objects.get(id=int(user_id))

    like_skigit = []
    if request.user.is_authenticated():
        video_likes = Like.objects.filter(user_id=request.user.id, status=True)
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

    context = {
        'video_detail': vid,
        'category_current': category_current,
        'user': user,
        'user_profile': us_profile,
        'video_likes': like_skigit,
        'like_count': like_dict,
        'video_type': 'c_o_skigit',
        'default_logo': profile_dic,
        'friend_list': friend_list,
        'video_share': share_dict,
        'video_plug': plug_dict,
        'skigit_list': ski_share_list,
        'users': get_all_logged_in_users()
    }

    if request.is_ajax():
        template = page_template
    return render(request, template, context)


@login_required(login_url='/')
@payment_required
@require_filled_profile
def plugged_in_skigits(request, template='sk_cat/skigit_plugged_into.html',
                       page_template='sk_cat/skigit_plugged_body.html'):
    user = vid = category = user_profile = video_likes = skigit_plug = None
    like_dict = []
    profile_dic = []
    vid_list = []
    share_dict = []
    plug_dict = []
    ski_share_list = []
    plug_skigit_list = []
    try:
        skigit_plug = request.user.username
        vid_record = Video.objects.filter(user=request.user.id).values_list('id', flat=True).order_by('-created_date')
        if VideoDetail.objects.filter(skigit_id__id__in=vid_record, status=True, is_plugged=True).exists():
            plug_id = VideoDetail.objects.filter(skigit_id__id__in=vid_record, status=True,
                                                 is_plugged=True).values_list('skigit_id', flat=True)
            vid = VideoDetail.objects.filter(skigit_id__id__in=plug_id, status=True)
            for vid_profile in vid:
                pluged_videos = VideoDetail.objects.get(title=vid_profile.plugged_skigit.title, status=True)
                plug_skigit_list.append({'plug_video_id': pluged_videos.id, 'vid_id': vid_profile.id})
                like_count = Like.objects.filter(skigit=vid_profile.skigit_id, status=True).count()
                like_dict.append({'id': vid_profile.id, 'count': like_count})
                video_share = Share.objects.filter(skigit_id=vid_profile, is_active=True).count()
                share_dict.append({'id': vid_profile.id, 'count': video_share})
                video_plug = VideoDetail.objects.filter(plugged_skigit=vid_profile.skigit_id,
                                                        is_plugged=True, status=1).count()
                plug_dict.append({'id': vid_profile.id, 'count': video_plug})
                if vid_profile.made_by:
                    us_profile = Profile.objects.get(user=vid_profile.made_by)
                    us_profile.made_by = vid_profile.made_by.id
                    if us_profile.logo_img.filter(is_deleted=False).all().count() > 0:
                        us_profile.business_logo = us_profile.logo_img.filter(is_deleted=False).all()[0]
                    profile_dic.append(us_profile)
                sharObj = Share.objects.filter(skigit_id=vid_profile, is_active=True,
                                               user=request.user.id).order_by('to_user', '-pk').distinct('to_user')
                for sh in sharObj:
                    ski_share_list.append({'share_date': sh.created_date, 'username': sh.to_user.username,
                                           'vid': sh.skigit_id_id})
        profile_dic = list(set(profile_dic))
    except ObjectDoesNotExist:
        messages.error(request, 'No Skigits found...!!!')
        return HttpResponseRedirect("/")

    like_skigit = []
    if request.user.is_authenticated():
        video_likes = Like.objects.filter(user_id=request.user.id, status=True)
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

    context = {
        'video_detail': vid,
        'skigit_plug': skigit_plug,
        'user': user,
        'user_profile': user_profile,
        'video_likes': like_skigit,
        'like_count': like_dict,
        'video_type': 'plugged',
        'default_logo': profile_dic,
        'friend_list': friend_list,
        'video_share': share_dict,
        'video_plug': plug_dict,
        'skigit_list': ski_share_list,
        'pluged_videos': plug_skigit_list,
        'users': get_all_logged_in_users()
    }

    if request.is_ajax():
        template = page_template
    return render(request, template, context)


def delete_liked_skigit(request):
    skigit_id = request.POST.get('skigit_v_id')
    vdo_obj = Video.objects.get(id=int(skigit_id))
    like_obj = Like.objects.get(skigit=vdo_obj)
    like_obj.status = False

    like_obj.save()
    context = {'is_success': "Ture", 'message': "Skigit unliked successfully"}

    return HttpResponse(json.dumps(context, cls=DjangoJSONEncoder),
                        content_type="application/json")


@login_required(login_url='/')
@payment_required
@require_filled_profile
def liked_skigits(request, template='sk_cat/skigit_plugged_into.html',
                       page_template='sk_cat/skigit_plugged_body.html'):

    user = vid = category = user_profile = video_likes = skigit_like = None
    like_dict = []
    profile_dic = []
    share_dict = []
    plug_dict = []
    ski_share_list = []
    try:
        skigit_like = request.user.username
        liked_skigits = Like.objects.filter(
            user_id=request.user.id, status=True
        ).values('skigit_id')
        vid = VideoDetail.objects.select_related('skigit_id').filter(
            skigit_id__in=liked_skigits,
            status=1
        ).order_by('-updated_date')
        for vid_profile in vid:
            like_count = Like.objects.filter(skigit=vid_profile.skigit_id, status=True).count()
            like_dict.append({'id': vid_profile.id, 'count': like_count})
            video_share = Share.objects.filter(skigit_id=vid_profile, is_active=True).count()
            share_dict.append({'id': vid_profile.id, 'count': video_share})
            video_plug = VideoDetail.objects.filter(plugged_skigit=vid_profile.skigit_id, is_plugged=True, status=1).count()
            plug_dict.append({'id': vid_profile.id, 'count': video_plug})
            if vid_profile.made_by:
                us_profile = Profile.objects.get(user=vid_profile.made_by)
                us_profile.made_by = vid_profile.made_by.id
                if us_profile.logo_img.filter(is_deleted=False).all().count() > 0:
                    us_profile.business_logo = us_profile.logo_img.filter(is_deleted=False).all()[0]
                profile_dic.append(us_profile)
        profile_dic = list(set(profile_dic))

        for vid_data in vid:
            sharObj = Share.objects.filter(skigit_id=vid_data, is_active=True, user=request.user.id).order_by('to_user', '-pk').distinct('to_user')
            for sh in sharObj:
                ski_share_list.append(
                    {'share_date': sh.created_date, 'username': sh.to_user.username, 'vid': sh.skigit_id_id})
    except ObjectDoesNotExist:
        messages.error(request, 'No Skigits found...!!!')
        return HttpResponseRedirect("/")

    like_skigit = []
    if request.user.is_authenticated():
        video_likes = Like.objects.filter(user_id=request.user.id, status=True)
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

    context = {
        'video_detail': vid,
        'skigit_like': skigit_like,
        'user': user,
        'user_profile': user_profile,
        'video_likes': like_skigit,
        'like_count': like_dict,
        'video_share': share_dict,
        'video_plug': plug_dict,
        'video_type': 'liked',
        'default_logo': profile_dic,
        'friend_list': friend_list,
        'skigit_list': ski_share_list,
        'users': get_all_logged_in_users()
    }
    if request.is_ajax():
        template = page_template
    return render(request, template, context)


def delete_favorite_skigit(request):
    skigit_id = request.POST.get('skigit_v_id')
    vdo_obj = Video.objects.get(id=int(skigit_id))
    fav_obj = Favorite.objects.filter(skigit=vdo_obj)[0]
    fav_obj.status = 0
    fav_obj.save()
    context = {'is_success': True, 'message': "Skigit unfavorite successfully"}

    return HttpResponse(json.dumps(context, cls=DjangoJSONEncoder), content_type="application/json")


@login_required(login_url='/')
@payment_required
@require_filled_profile
def favorite_skigits(request, template='sk_cat/skigit_plugged_into.html',
                       page_template='sk_cat/skigit_plugged_body.html'):

    user = vid = category = user_profile = video_fav = skigit_fav = None
    profile_dic = []
    share_dict = []
    plug_dict = []
    like_dict = []
    ski_share_list = []
    try:
        skigit_fav = request.user.username
        fav_skigits = Favorite.objects.filter(
            user_id=request.user.id, status=True
        ).values('skigit_id')
        vid = VideoDetail.objects.select_related('skigit_id').filter(
            skigit_id__in=fav_skigits,
            status=1
        ).order_by('-updated_date')
        for vid_profile in vid:
            like_count = Like.objects.filter(skigit=vid_profile.skigit_id, status=True).count()
            like_dict.append({'id': vid_profile.id, 'count': like_count})
            video_share = Share.objects.filter(skigit_id=vid_profile, is_active=True).count()
            share_dict.append({'id': vid_profile.id, 'count': video_share})
            video_plug = VideoDetail.objects.filter(plugged_skigit=vid_profile.skigit_id, is_plugged=True, status=1).count()
            plug_dict.append({'id': vid_profile.id, 'count': video_plug})
            if vid_profile.made_by:
                us_profile = Profile.objects.get(user=vid_profile.made_by)
                us_profile.made_by = vid_profile.made_by.id
                if us_profile.logo_img.filter(is_deleted=False).all().count() > 0:
                    us_profile.business_logo = us_profile.logo_img.filter(is_deleted=False).all()[0]
                profile_dic.append(us_profile)
        profile_dic = list(set(profile_dic))

        for vid_data in vid:
            sharObj = Share.objects.filter(skigit_id=vid_data, is_active=True, user=request.user.id).order_by('to_user', '-pk').distinct('to_user')
            for sh in sharObj:
                ski_share_list.append(
                    {'share_date': sh.created_date, 'username': sh.to_user.username, 'vid': sh.skigit_id_id})
    except ObjectDoesNotExist:
        messages.error(request, 'No Skigits found...!!!')
        return HttpResponseRedirect("/")

    like_skigit = []
    if request.user.is_authenticated():
        video_likes = Like.objects.filter(user_id=request.user.id, status=True)
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
    context = {
        'video_detail': vid,
        'skigit_fav': skigit_fav,
        'user': user,
        'user_profile': user_profile,
        'video_likes': like_skigit,
        'like_count': like_dict,
        'video_type': 'fav',
        'default_logo': profile_dic,
        'friend_list': friend_list,
        'video_share': share_dict,
        'video_plug': plug_dict,
        'skigit_list': ski_share_list,
        'users': get_all_logged_in_users()
    }
    if request.is_ajax():
        template = page_template
    return render(request, template, context)


@login_required(login_url='/')
def delete_skigit(request):
    response_data = {'is_success': False, 'message': 'Error in delete ajax call'}
    parent_plug = None
    if request.is_ajax() and request.method == 'POST':
        try:
            vdo_id = request.POST.get('skigit_v_id')
            vdo_detail_obj = VideoDetail.objects.get(id=int(vdo_id))

            child_plug = VideoDetail.objects.filter(plugged_skigit=vdo_detail_obj.skigit_id, is_plugged=True,
                                                    status=1).values_list('id', flat=True)
            if VideoDetail.objects.filter(skigit_id=vdo_detail_obj.plugged_skigit, is_plugged=True, status=1).exists():
                parent_plug = VideoDetail.objects.get(skigit_id=vdo_detail_obj.plugged_skigit, is_plugged=True,
                                                      status=1)
            f_nt_message = " The Primary skigit "
            f_nt_message += vdo_detail_obj.title
            if child_plug:
                plg_video = VideoDetail.objects.filter(id__in=child_plug, status=1)
                if parent_plug:
                    f_nt_message += " was deleted. You are now connected to the next Plug-in in the *@p* "
                    f_nt_message += str(parent_plug.skigit_id.id)

                for vid_plug in plg_video:
                    if not parent_plug:
                        f_nt_message += " was deleted. *@c* "
                        f_nt_message += str(vid_plug.skigit_id.id)
                    if (notification_settings(vid_plug.skigit_id.user.id, 'plug_notify')) == True:
                        web_push_notifications('plug_primary', vid_plug.skigit_id.user,
                                               request.user, vdo_detail_obj.skigit_id.id, f_nt_message)
                        if parent_plug:
                            VideoDetail.objects.filter(id__in=child_plug, status=1).update(plugged_skigit=parent_plug.skigit_id.id)

            if vdo_detail_obj.is_plugged == False:
                VideoDetail.objects.filter(plugged_skigit=vdo_detail_obj.skigit_id, status=1).update(is_plugged=False)

            vdo_detail_obj.is_plugged = False
            vdo_detail_obj.is_active = False
            vdo_detail_obj.save()
            response_data['is_success'] = True
            response_data['message'] = " %s Skigit was deleted. \r\n" % vdo_detail_obj.title
        except Exception:
            response_data['is_success'] = False
            response_data['message'] = "Skigit Deletion Error"
    return JsonResponse(response_data)


@login_required(login_url='/')
def unplug_skigit(request):
    response_data = {}
    is_success = False
    message = 'Error in delete ajax call'
    if request.is_ajax() and request.method == 'POST':
        try:
            vdo_id = request.POST.get('skigit_unplug_id')
            if VideoDetail.objects.filter(id=vdo_id, skigit_id__user=request.user.id, status=True).exists():

                vid_record = VideoDetail.objects.get(id=vdo_id, skigit_id__user=request.user.id, status=True)
                vid_record.is_plugged = False
                vid_record.save()

                if(notification_settings(vid_record.plugged_skigit.user.id, 'un_plug_notify')) == True:
                    f_nt_message = " "
                    f_nt_message += " We're sorry... your got unplugged."
                    f_nt_message += request.user.username
                    f_nt_message += " unplugged from your Skigit"
                    f_nt_message += vid_record.title + '.'
                    Notification.objects.create(msg_type='un_plug', skigit_id=vid_record.skigit_id.id,
                                                user=vid_record.plugged_skigit.user,
                                                from_user=request.user, message=f_nt_message)
                response_data['is_success'] = True
                response_data['message'] = " %s Skigit was Unplugged. \r\n" % vid_record.title
        except Exception:
            response_data['is_success'] = False
            response_data['message'] = "Skigit Deletion Error"
    return JsonResponse(response_data)


@csrf_protect
def email_exits_check(request):
    response_data = {}
    if request.is_ajax() and request.method == 'POST':
        email_id = request.POST.get('email', None)
        if email_id and email_id != '' and email_id is not None:
            email_check = User.objects.filter(email=email_id).exists()
            if email_check and email_check is not None:
                is_success = True
                message = 'please Wait....'
            else:
                is_success = False
                message = 'E-mail Address Not Found'
        else:
            is_success = False
            message = 'Invalid E-mail Address'
    else:
        is_success = False
        message = 'Invalid Request'

    response_data['is_success'] = is_success
    response_data['message'] = message
    return JsonResponse(response_data)


@login_required(login_url='/')
@payment_required
@require_filled_profile
def sperks(request, template='sperk/sperk.html', page_template='sperk/sperk_body.html'):
    """
        Comment: Sperk list display by business user who provide incentive
        Args: request: Request method
        Returns: Sperk (First Business Logo)
    """
    if User.objects.filter(id=request.user.id).exists():
        sperk_logo_list = []
        sperk_logo = Profile.objects.filter(incentive=True).order_by('company_title')
        for b_logo in sperk_logo:
            if b_logo.logo_img.filter(is_deleted=False).all():
                b_logo.img_id = b_logo.logo_img.filter(is_deleted=False).all()[0]
                b_logo.b_img = get_thumbnail(b_logo.logo_img.filter(is_deleted=False).all()[0].logo, '90x60',
                                             quality=99, format='PNG').url
                sperk_logo_list.append(b_logo)

        context = {
            'page_template': page_template,
            'sperk_logo_list': sperk_logo_list,
        }
        if request.is_ajax():
            template = page_template
        return render(request, template, context)


@login_required(login_url='/')
def sperk_profile(request, user, logo):
    """
        On Click of Sperk logo page will be redirect to
        Sperk profile, page having information related
        Sperk

    Args:
        request: Requested Method GET POST
        user: user_id
        logo: sperk (Logo id)

    Returns:
        Sperk (Business Logo) detail view

    """

    if User.objects.filter(id=request.user.id).exists():
        ski_share_list = []
        busniess_logo = []
        friend_list = []
        like_dict = []
        id = user
        logoid = logo
        profile_list = Profile.objects.filter(user__id=user)
        try:
            request_user = User.objects.get(pk=profile_list[0].user.id, is_active=True)
        except ObjectDoesNotExist:
            messages.error(request, 'Sorry, Your Request User Not Found.')
            return HttpResponseRedirect('/')  # HttpResponseRedirect
        busniesslogo = BusinessLogo.objects.get(id=logo, is_deleted=False)

        for b_logo in profile_list:
            for bb_logo in b_logo.logo_img.filter(is_deleted=False).all():
                bb_logo.img_id = bb_logo.id
                bb_logo.l_img = get_thumbnail(bb_logo.logo, '300x120', quality=99, format='PNG').url
                busniess_logo.append(bb_logo)

        for user_list in profile_list:
            company_url = ProfileUrl.objects.filter(user=user_list.user)

        if Embed.objects.filter(to_user=request_user, is_embed=True).exists():
            embed_skigit_list = Embed.objects.filter(to_user=request_user, is_embed=True).values_list('skigit_id',
                                                                                                      flat=True)
            if request.user.is_authenticated():
                if Friend.objects.filter(Q(to_user=request.user.id) | Q(from_user=request.user.id), status=1).exists():
                    f_list = Friend.objects.filter(Q(to_user=request.user.id) | Q(from_user=request.user.id), status=1)
                    from_user_list = f_list.exclude(from_user=request.user.id).values_list('from_user',
                                                                                           flat=True).distinct()
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
                video_likes = Like.objects.filter(user_id=request.user.id, status=True)
                for likes in video_likes:
                    like_dict.append(likes.skigit_id)
            vid = VideoDetail.objects.select_related('skigit_id').filter(skigit_id__id__in=embed_skigit_list)
            serializer = VideoDetailSerializer(vid, many=True)
            for vid_data in vid:
                sharObj = Share.objects.filter(skigit_id=vid_data, is_active=True, user=user).order_by(
                    'to_user', '-pk').distinct('to_user')
                for sh in sharObj:
                    ski_share_list.append(
                        {'share_date': sh.created_date, 'username': sh.to_user.username, 'vid': sh.skigit_id_id})
            request_user = request_user
            video_detail = serializer.data
            video_likes = like_dict
            friend_list = friend_list
            order_value = '1'
            togal_val = '1'
            skigit_list = ski_share_list
            users = get_all_logged_in_users()

    return render(request, 'sperk/sperk-profile.html', locals())


@csrf_exempt
def bug_management(request):

    response_data = {'is_success': False}
    if request.is_ajax() and request.method == 'POST':
        bug_mgm = BugReport()
        bug_mgm.user = request.user

        if request.POST.get('skigit_id', ''):
            video_inst = VideoDetail.objects.get(id=request.POST.get('skigit_id', ''))
            bug_mgm.skigit_id = video_inst

        bug_mgm.bug_page_url = request.POST.get('bug_url', '')
        bug_mgm.bug_description = request.POST.get('bug_desc', '')
        if request.POST.get('bug_repeated', '') == '0' or request.POST.get('bug_repeated', '') == 0:
            bug_mgm.bug_repeated = False
        else:
            bug_mgm.bug_repeated = True
        bug_mgm.save()
        BugReport.objects.filter(id=bug_mgm.id).update(bug_title='Bug#'+str(bug_mgm.id))
        response_data['is_success'] = True
        response_data['message'] = '&#10004 Bug Report Submitted.'
        return JsonResponse(response_data)


def getSwfURL(video_id):
    url = 'https://www.youtube.com/embed/%s' \
          '?modestbranding=1&showinfo=0&autoplay=0&autohide=1&rel=0&wmode=transparent' % (video_id)
    return url


def getYoutubeURL(video_id):
    url = 'https://www.youtube.com/watch?v=%s' % video_id
    return url


@csrf_exempt
@login_required(login_url='/')
@payment_required
@require_filled_profile
def ajax_direct_uploade(request):
    """
        PRIMARY SKIGIT: Direct video upload method
    """
    response_data = {}
    if request.method == 'POST':
        try:
            form = YoutubeDirectUploadForm(request.POST, request.FILES)
            form2 = YoutubeLinkUploadForm(request.POST)

            if form.is_valid() and request.POST.get("title", '') and request.POST.get('category', ''):
                if VideoDetail.objects.filter(title=request.POST.get("title", '')).exists():
                    response_data['is_success'] = False
                    response_data['message'] = "Title already in used please enter diffrent one"
                    return JsonResponse(response_data)
                else:
                    uploaded_video = form.save()
                    title = request.POST.get("title", '')
                    description = request.POST.get('why_rocks', '')

                    # Youtube Video API Upload call
                    video_entry = upload_direct(str(uploaded_video.file_on_server.path), str(title), str(description))

                    if video_entry['id']:
                        swf_url = getSwfURL(video_entry['id'])
                        youtube_url = getYoutubeURL(video_entry['id'])
                        video_id = video_entry['id']

                        # save video_id to video instance
                        video = Video()
                        video.user = request.user
                        video.video_id = video_id
                        video.title = title
                        video.description = description
                        video.youtube_url = youtube_url
                        video.swf_url = swf_url
                        video.save()

                        # Creating Thumbnail Entry for Uploaded Videos
                        thumbnail=[]
                        thumbnail.append(video_entry.get('snippet', {}).get('thumbnails', {}).get('high').get('url'))
                        thumbnail.append(video_entry.get('snippet', {}).get('thumbnails', {}).get('medium').get('url'))
                        thumbnail.append(video_entry.get('snippet', {}).get('thumbnails', {}).get('default', {}).get('url'))

                        for thumb in thumbnail:
                            Thumbnail.objects.create(video=video, url=thumb)

                        skigit_form = VideoDetail()
                        skigit_form.title = request.POST.get("title", '')
                        if request.POST.get('category', ''):
                            category = Category.objects.get(id=request.POST.get('category', ''))
                            skigit_form.category = category
                        if request.POST.get('subject_category', ''):
                            subject_category = SubjectCategory.objects.get(id=request.POST.get('subject_category', ''))
                            skigit_form.subject_category = subject_category
                        skigit_form.add_logo = request.POST.get('add_logo', '')
                        skigit_form.receive_donate_sperk = request.POST.get('receive_donate_sperk', '')
                        skigit_form.why_rocks = request.POST.get('why_rocks', '')

                        if request.POST.get('made_by', ''):
                            user = User.objects.get(id=request.POST.get("made_by", ''))
                            skigit_form.made_by = user
                            skigit_form.business_user = user
                        if request.POST.get('made_by_option', ''):
                            skigit_form.made_by_option = request.POST.get('made_by_option', '')

                        skigit_form.skigit_id = video
                        skigit_form.share_skigit = video

                        if request.POST.get("add_logo", '') == '1' and (
                            not request.POST.get("select_logo", '') == 'undefined' and not request.POST.get("select_logo",
                                                                                                            '') == '') and \
                                BusinessLogo.objects.filter(id=request.POST.get("select_logo", '')).exists():
                            busness_logo = BusinessLogo.objects.get(id=request.POST.get("select_logo", ''))
                            skigit_form.business_logo = busness_logo
                            skigit_form.is_sperk = True
                            if request.POST.get('receive_donate_sperk', '') == '1':
                                donate = Donation.objects.get(id=(request.POST.get('donate_sperk', '')))
                                skigit_form.donate_skigit = donate

                        skigit_form.bought_at = request.POST.get("bought_at", "")
                        skigit_form.why_rocks = request.POST.get("why_rocks", "")
                        skigit_form.view_count = 0
                        skigit_form.save()

                        # delete the uploaded video instance
                        uploaded_video.delete()

                        form1 = SkigitUploadForm()
                        form2 = YoutubeLinkUploadForm()
                        organization_list = Donation.objects.all()
                        response_data['is_success'] = True
                        response_data['message'] = "<span style='font-size:20px;'><i class='glyphicon glyphicon-ok-circle' style='top: 5px !important;' /></span> Your video was successfully uploaded. Wait while video will be processed"

                        return JsonResponse(response_data)
                    else:
                        form1 = SkigitUploadForm()
                        form2 = YoutubeLinkUploadForm()
                        organization_list = Donation.objects.all()
                        response_data['is_success'] = False
                        response_data['message'] = video_entry['message']
                    return JsonResponse(response_data)
        except:
            form1 = SkigitUploadForm()
            form2 = YoutubeLinkUploadForm()
            organization_list = Donation.objects.all()
            response_data['is_success'] = False
            response_data['message'] = 'Error into Upload Skigit, Please try again later'
            return JsonResponse(response_data)
    form = YoutubeDirectUploadForm()
    form1 = SkigitUploadForm()
    form2 = YoutubeLinkUploadForm()
    organization_list = Donation.objects.all()
    message = ''
    return render(request, "youtube/yt_direct-upload.html", locals())


@csrf_exempt
@login_required(login_url='/')
@payment_required
@require_filled_profile
def ajax_link_uploade(request):
    """
        PRIMARY SKIGIT: link upload method
    """
    response_data = {}
    if request.is_ajax() and request.method == 'POST':
        try:
            video_link = str(request.POST.get('video_link', ''))
            url_parts = video_link.split("/")
            url_parts.reverse()
            url_parts1 = url_parts[0].split("?v=")
            url_parts1.reverse()
            video_id = url_parts1[0]
            swf_url = 'http://www.youtube.com/embed/' + video_id + '?modestbranding=1&showinfo=0&autoplay=0&autohide=1&rel=0&wmode=transparent'

            if VideoDetail.objects.filter(title=request.POST.get("title", '')).exists():
                response_data['is_success'] = False
                response_data['message'] = "Title already in used please enter diffrent one"
                return JsonResponse(response_data)

            if Video.objects.filter(video_id=video_id).exists():
                form1 = SkigitUploadForm()
                form2 = YoutubeLinkUploadForm()
                organization_list = Donation.objects.all()
                # messages.error(request, "We're sorry.. your video failed to load due to duplication of video link")
                response_data['is_success'] = False
                response_data['message'] = "&#x2718; we're sorry.. your video failed to upload due to duplication of video link"
                return JsonResponse(response_data)
            else:
                video_link_obj = UploadedVideoLink.objects.create(video_link=request.POST.get('video_link', ''))
                api = Api()
                api.authenticate()

                # save video_id to video instance
                video = Video()
                video_tumb = video
                video.user = request.user
                video.video_id = video_id
                video.title = request.POST.get("title", '')
                video.youtube_url = video_link
                video.swf_url = swf_url
                video.save1()

                skigit_form = VideoDetail()
                skigit_form.title = request.POST.get("title", '')
                if request.POST.get('category', ''):
                    category = Category.objects.get(id=request.POST.get('category', ''))
                    skigit_form.category = category
                if request.POST.get('subject_category', ''):
                    subject_category = SubjectCategory.objects.get(id=request.POST.get('subject_category', ''))
                    skigit_form.subject_category = subject_category
                skigit_form.add_logo = request.POST.get('add_logo', '')
                skigit_form.receive_donate_sperk = request.POST.get('receive_donate_sperk', '')
                skigit_form.why_rocks = request.POST.get('why_rocks', '')

                if request.POST.get('made_by', ''):
                    user = User.objects.get(id=request.POST.get("made_by", ''))
                    skigit_form.made_by = user
                    skigit_form.business_user = user
                if request.POST.get('made_by_option', ''):
                    skigit_form.made_by_option = request.POST.get('made_by_option', '')

                skigit_form.skigit_id = video
                skigit_form.share_skigit = video
                if request.POST.get("add_logo", '') == '1' and (not request.POST.get("select_logo", '') == 'undefined' and not request.POST.get("select_logo", '') == '') and \
                        BusinessLogo.objects.filter(id=request.POST.get("select_logo", '')).exists():
                    busness_logo = BusinessLogo.objects.get(id=request.POST.get("select_logo", ''))
                    skigit_form.business_logo = busness_logo
                    skigit_form.is_sperk = True
                    if request.POST.get('receive_donate_sperk', '') == '1':
                        donate = Donation.objects.get(id=request.POST.get('donate_sperk', ''))
                        skigit_form.donate_skigit = donate

                skigit_form.bought_at = request.POST.get("bought_at", "")
                skigit_form.why_rocks = request.POST.get("why_rocks", "")
                skigit_form.view_count = 0
                skigit_form.save()

                form1 = SkigitUploadForm()
                form2 = YoutubeLinkUploadForm()
                organization_list = Donation.objects.all()
                response_data['is_success'] = True
                response_data['message'] = "<span style='font-size:20px;'><i class='glyphicon glyphicon-ok-circle' style='top: 5px !important;' /></span> Your video was successfully uploaded. Wait while video will be processed"
                return JsonResponse(response_data)
        except:
            form1 = SkigitUploadForm()
            form2 = YoutubeLinkUploadForm()
            organization_list = Donation.objects.all()
            response_data['is_success'] = False
            response_data['message'] = "<span style='font-size:20px;'><i class='glyphicon glyphicon-remove-circle' style='top: 5px !important;' /></span> Error into Link Skigit, Please try again later"
            return JsonResponse(response_data)
    else:
        form = YoutubeDirectUploadForm()
        form1 = SkigitUploadForm()
        form2 = YoutubeLinkUploadForm()
        organization_list = Donation.objects.all()
        return render(request, "youtube/yt_direct-upload.html", locals())


@csrf_exempt
@login_required(login_url='/')
@payment_required
@require_filled_profile
def ajax_skigit_plugin_link(request, plug_id):
    """
        Plug-in : link upload method
    """
    response_data = {}
    if request.is_ajax() and request.method == 'POST':
        try:
            video_detail = VideoDetail.objects.get(id=plug_id)
            username = video_detail.skigit_id.user.username
            plugged_user = video_detail.skigit_id.user
            skigit_title = video_detail.title
            plug_category = video_detail.category.id
            sub_catogery = video_detail.subject_category.id
            video_link = str(request.POST.get('video_link', ''))
            url_parts = video_link.split("/")
            url_parts.reverse()
            url_parts1 = url_parts[0].split("?v=")
            url_parts1.reverse()
            video_id = url_parts1[0]
            swf_url = 'http://www.youtube.com/embed/' + video_id + '?modestbranding=1&showinfo=0&autoplay=0&autohide=1&rel=0&wmode=transparent'

            if VideoDetail.objects.filter(title=request.POST.get("title", '')).exists():
                response_data['is_success'] = False
                response_data['message'] = "Title already in used please enter diffrent one"
                return JsonResponse(response_data)

            if Video.objects.filter(video_id=video_id).exists():
                form1 = SkigitUploadForm()
                form2 = YoutubeLinkUploadForm()
                organization_list = Donation.objects.all()
                response_data['is_success'] = False
                response_data['message'] = "&#x2718; we're sorry.. your video failed to upload due to duplication of video link"
                return JsonResponse(response_data)
            else:
                video_link_obj = UploadedVideoLink.objects.create(video_link=request.POST.get('video_link', ''))
                api = Api()
                api.authenticate()

                # save video_id to video instance
                video = Video()
                video_tumb = video
                video.user = request.user
                video.video_id = video_id
                video.title = request.POST.get("title", '')
                video.youtube_url = video_link
                video.swf_url = swf_url
                video.save1()

                skigit_form = VideoDetail()
                skigit_form.title = request.POST.get("title", '')
                if request.POST.get('category', ''):
                    category = Category.objects.get(id=request.POST.get('category', ''))
                    skigit_form.category = category
                if request.POST.get('subject_category', ''):
                    subject_category = SubjectCategory.objects.get(id=request.POST.get('subject_category', ''))
                    skigit_form.subject_category = subject_category
                skigit_form.add_logo = request.POST.get('add_logo', '')
                skigit_form.receive_donate_sperk = request.POST.get('receive_donate_sperk', '')
                skigit_form.why_rocks = request.POST.get('why_rocks', '')

                if request.POST.get('made_by', ''):
                    user = User.objects.get(id=request.POST.get("made_by", ''))
                    skigit_form.made_by = user
                    skigit_form.business_user = user
                if request.POST.get('made_by_option', ''):
                    skigit_form.made_by_option = request.POST.get('made_by_option', '')

                skigit_form.skigit_id = video
                skigit_form.share_skigit = video
                if request.POST.get("add_logo", '') == '1' and (not request.POST.get("select_logo", '') == 'undefined' and not request.POST.get("select_logo", '') == '') and \
                        BusinessLogo.objects.filter(id=request.POST.get("select_logo", '')).exists():
                    busness_logo = BusinessLogo.objects.get(id=request.POST.get("select_logo", ''))
                    skigit_form.business_logo = busness_logo
                    skigit_form.is_sperk = True
                    if request.POST.get('receive_donate_sperk', '') == '1':
                        donate = Donation.objects.get(id=request.POST.get('donate_sperk', ''))
                        skigit_form.donate_skigit = donate

                skigit_form.bought_at = request.POST.get("bought_at", "")
                skigit_form.why_rocks = request.POST.get("why_rocks", "")
                plugged_video = Video.objects.get(id=video_detail.skigit_id.id)
                skigit_form.is_plugged = True
                skigit_form.plugged_skigit = plugged_video
                skigit_form.share_skigit = video
                skigit_form.view_count = 0
                skigit_form.save()
                plug_videos = Plugged()
                plug_videos.skigit = Video.objects.get(id=video_detail.skigit_id.id)
                plug_videos.user = request.user
                plug_videos.plugged = plugged_user
                plug_videos.save()

                if (notification_settings(video_detail.skigit_id.user.id, 'plug_notify')) == True:
                    if not (request.user.id == video_detail.skigit_id.user.id):

                        if not video_detail.is_plugged:
                            plug_message = 'Congratulations! '
                            plug_message += video_detail.skigit_id.user.username
                            plug_message += ' has plugged into your Skigit '
                            plug_message += skigit_title

                            Notification.objects.create(msg_type='plug', skigit_id=video_detail.skigit_id.id,
                                                        user=video_detail.skigit_id.user, message=plug_message,
                                                        from_user=request.user)
                        else:
                            plug_message = 'Coincidence? I think not! '
                            plug_message += request.user.username
                            plug_message += ' has plugged into a Skigit that you plugged into '
                            plug_message += skigit_title

                            Notification.objects.create(msg_type='plug-plug', skigit_id=video_detail.skigit_id.id,
                                                        user=video_detail.skigit_id.user, message=plug_message,
                                                        from_user=request.user)

                form1 = SkigitUploadForm()
                form2 = YoutubeLinkUploadForm()
                response_data['is_success'] = True
                response_data['message'] = "<span style='font-size:20px;'><i class='glyphicon glyphicon-ok-circle' style='top: 5px !important;' /></span> Your video was successfully uploaded. Wait while video will be processed"
                return JsonResponse(response_data)
        except:
            form1 = SkigitUploadForm()
            form2 = YoutubeLinkUploadForm()
            organization_list = Donation.objects.all()
            response_data['is_success'] = False
            response_data['message'] = "<span style='font-size:20px;'><i class='glyphicon glyphicon-remove-circle' style='top: 5px !important;' /></span> Error into Link Skigit, Please try again later"
            return JsonResponse(response_data)
    else:
        video_detail = VideoDetail.objects.get(id=plug_id)
        username = video_detail.skigit_id.user.username
        skigit_title = video_detail.title
        plug_category = video_detail.category.id
        sub_catogery = video_detail.subject_category.id
        my_aws_by = video_detail.skigit_id.id
        form = YoutubeDirectUploadForm()
        form1 = SkigitUploadForm()
        form2 = YoutubeLinkUploadForm()
        organization_list = Donation.objects.all()
        return render(request, "youtube/yt_skigit_plugin.html", locals())


@csrf_exempt
@login_required(login_url='/')
@payment_required
@require_filled_profile
def ajax_skigit_plugin_video(request, plug_id):
    """
        Plug-in : direct upload method
    """
    response_data = {}
    if request.method == 'POST':
        try:
            form = YoutubeDirectUploadForm(request.POST, request.FILES)
            form2 = YoutubeLinkUploadForm(request.POST)
            video_detail = VideoDetail.objects.get(id=plug_id)
            username = video_detail.skigit_id.user.username
            plugged_user = video_detail.skigit_id.user
            skigit_title = video_detail.title
            sub_catogery = video_detail.subject_category.sub_cat_name

            if form.is_valid() and request.POST.get("title", '') and request.POST.get('category', ''):
                if VideoDetail.objects.filter(title=request.POST.get("title", '')).exists():
                    response_data['is_success'] = False
                    response_data['message'] = "Title already in used please enter diffrent one"
                    return JsonResponse(response_data)
                else:
                    uploaded_video = form.save()
                    title = request.POST.get("title", '')
                    description = request.POST.get('why_rocks', '')

                    # Youtube Video API Upload call
                    video_entry = upload_direct(str(uploaded_video.file_on_server.path), str(title), str(description))

                    if video_entry['id']:
                        swf_url = getSwfURL(video_entry['id'])
                        youtube_url = getYoutubeURL(video_entry['id'])
                        video_id = video_entry['id']

                        # save video_id to video instance
                        video = Video()
                        video.user = request.user
                        video.video_id = video_id
                        video.title = title
                        video.description = description
                        video.youtube_url = youtube_url
                        video.swf_url = swf_url
                        video.save()

                        # Creating Thumbnail Entry for Uploaded Videos
                        thumbnail = []
                        thumbnail.append(video_entry.get('snippet', {}).get('thumbnails', {}).get('high').get('url'))
                        thumbnail.append(video_entry.get('snippet', {}).get('thumbnails', {}).get('medium').get('url'))
                        thumbnail.append(
                            video_entry.get('snippet', {}).get('thumbnails', {}).get('default', {}).get('url'))

                        for thumb in thumbnail:
                            Thumbnail.objects.create(video=video, url=thumb)

                        # save video_id to video instance

                        skigit_form = VideoDetail()
                        skigit_form.title = request.POST.get("title", '')
                        if request.POST.get('category', ''):
                            category = Category.objects.get(id=request.POST.get('category', ''))
                            skigit_form.category = category
                        if request.POST.get('subject_category', ''):
                            subject_category = SubjectCategory.objects.get(id=request.POST.get('subject_category', ''))
                            skigit_form.subject_category = subject_category
                        skigit_form.add_logo = request.POST.get('add_logo', '')
                        skigit_form.receive_donate_sperk = request.POST.get('receive_donate_sperk', '')
                        skigit_form.why_rocks = request.POST.get('why_rocks', '')

                        if request.POST.get('made_by', ''):
                            user = User.objects.get(id=request.POST.get("made_by", ''))
                            skigit_form.made_by = user
                            skigit_form.business_user = user
                        if request.POST.get('made_by_option', ''):
                            skigit_form.made_by_option = request.POST.get('made_by_option', '')

                        skigit_form.skigit_id = video
                        skigit_form.share_skigit = video
                        if request.POST.get("add_logo", '') == '1' and (not request.POST.get("select_logo", '') == 'undefined' and not request.POST.get("select_logo", '') == '') and \
                                BusinessLogo.objects.filter(id=request.POST.get("select_logo", '')).exists():
                            busness_logo = BusinessLogo.objects.get(id=request.POST.get("select_logo", ''))
                            skigit_form.business_logo = busness_logo
                            skigit_form.is_sperk = True
                            if request.POST.get('receive_donate_sperk', '') == '1':
                                donate = Donation.objects.get(id=request.POST.get('donate_sperk', ''))
                                skigit_form.donate_skigit = donate

                        skigit_form.bought_at = request.POST.get("bought_at", "")
                        skigit_form.why_rocks = request.POST.get("why_rocks", "")
                        plugged_video = Video.objects.get(id=video_detail.skigit_id.id)
                        skigit_form.is_plugged = True
                        skigit_form.plugged_skigit = plugged_video
                        skigit_form.share_skigit = video
                        skigit_form.view_count = 0
                        skigit_form.save()
                        plug_videos = Plugged()
                        plug_videos.skigit = Video.objects.get(id=video_detail.skigit_id.id)
                        plug_videos.user = request.user
                        plug_videos.plugged = plugged_user
                        plug_videos.save()

                        if (notification_settings(video_detail.skigit_id.user.id, 'plug_notify')) == True:

                            if not (request.user.id == video_detail.skigit_id.user.id):

                                if not video_detail.is_plugged:
                                    plug_message = 'Congratulations! '
                                    plug_message += video_detail.skigit_id.user.username
                                    plug_message += ' has plugged into your Skigit '
                                    plug_message += skigit_title
                                    Notification.objects.create(msg_type='plug', skigit_id=video_detail.skigit_id.id,
                                                                user=video_detail.skigit_id.user, message=plug_message,
                                                                from_user=request.user)
                                else:
                                    plug_message = 'Coincidence? I think not! '
                                    plug_message += request.user.username
                                    plug_message += ' has plugged into a Skigit that you plugged into '
                                    plug_message += skigit_title
                                    Notification.objects.create(msg_type='plug-plug', skigit_id=video_detail.skigit_id.id,
                                                                user=video_detail.skigit_id.user, message=plug_message,
                                                                from_user=request.user)

                        form1 = SkigitUploadForm()
                        form2 = YoutubeLinkUploadForm()
                        organization_list = Donation.objects.all()
                        response_data['is_success'] = True
                        response_data['message'] = "<span style='font-size:20px;'><i class='glyphicon glyphicon-ok-circle' style='top: 5px !important;' /></span> Your video was successfully uploaded. Wait while video will be processed."
                        return JsonResponse(response_data)
        except:
            form1 = SkigitUploadForm()
            form2 = YoutubeLinkUploadForm()
            organization_list = Donation.objects.all()
            response_data['is_success'] = False
            response_data['message'] = "<span style='font-size:20px;'><i class='glyphicon glyphicon-remove-circle' style='top: 5px !important;' /></span> Error into Link Skigit, Please try again later."
            # video.delete()
            return JsonResponse(response_data)
    else:
        video_detail = VideoDetail.objects.get(id=plug_id)
        username = video_detail.skigit_id.user.username
        skigit_title = video_detail.title
        plug_category = video_detail.category.id
        sub_catogery = video_detail.subject_category.id
        my_aws_by = video_detail.skigit_id.id
        form = YoutubeDirectUploadForm()
        form1 = SkigitUploadForm()
        form2 = YoutubeLinkUploadForm()
        organization_list = Donation.objects.all()
        message = ''
        return render(request, "youtube/yt_direct-upload.html", locals())


@csrf_exempt
@login_required(login_url='/')
@payment_required
@require_filled_profile
def copyright(request, ski_id):
    instance = VideoDetail.objects.get(pk=ski_id)
    form = CopyrightInfringementForm(initial={'skigit_id': ski_id})
    skigitt_id = ski_id
    if request.method == 'POST':
        form = CopyrightInfringementForm(request.POST)
        if form.is_valid():
            copy_right = form.save(commit=False)
            user_profile = Profile.objects.get(user__id=request.user.id)
            copy_right.user_id = user_profile.user
            copy_right.submitted_by = user_profile
            copy_right.skigit_id = ski_id
            copy_right.save()

            # set the skigit under open copyright infringement
            instance.copyright_skigit = 0
            instance.save()

            messages.success(request, 'A Copyright Infringement claim has been submitted!')
            form = CopyrightInfringementForm()
            return HttpResponseRedirect('/')
        form = CopyrightInfringementForm()
    return render(request, "includes/copyrightinfregment.html", locals())


@csrf_exempt
def skigit_statistics(request):
    response_data = {'is_success': False}
    like_count = plug_count = fav_count = view_count = share_count = 0
    if request.is_ajax() and request.method == 'POST':
        skigit = request.POST.get("skigit_id", "")

        try:
            like_count = Like.objects.filter(skigit__id=skigit, status=True).count()
        except:
             like_count = 0
        try:
            fav_count = Favorite.objects.filter(skigit__id=skigit, status=1, is_active=True).count()
        except:
            fav_count = 0
        try:
            plug_count = VideoDetail.objects.filter(plugged_skigit__id=skigit, is_plugged=True, status=1).count()
        except:
            plug_count = 0
        try:
            if VideoDetail.objects.filter(skigit_id__id=skigit, status=1).exists():
                vid = VideoDetail.objects.get(skigit_id__id=skigit, status=1)
                view_count = vid.view_count
            else:
                view_count = 0
        except:
            view_count = 0
        try:
            if Share.objects.filter(skigit_id=skigit, is_active=True).exists():
                share_count = Share.objects.filter(skigit_id=skigit, is_active=True).count()
        except:
            share_count = 0

        response_data['like_count'] = like_count
        response_data['fav_count'] = fav_count
        response_data['plug_count'] = plug_count
        response_data['view_count'] = view_count
        response_data['share_count'] = share_count
        response_data['is_success'] = True
        response_data['message'] = 'Statistic Count.'
    return JsonResponse(response_data)


@csrf_exempt
def skigit_i_like(request):
    """
     Like skigit
    """
    skigit_id, message, like_count, is_found, like = None, None, None, None, None
    is_success = False
    response_data = {}
    skigit_id = request.POST.get('skigit_id', None)
    if request.is_ajax() and request.method == 'POST':
        if skigit_id and skigit_id is not None:
            if request.user.is_authenticated():
                user = request.user
                is_found = Video.objects.filter(pk=skigit_id)

                if is_found and is_found is not None:
                    try:
                        if Like.objects.filter(skigit__id=skigit_id, user_id=user.id).exists():
                            like = Like.objects.filter(skigit__id=skigit_id, user_id=user.id).update(status=True)
                            is_success = True
                            message = "Skigit Liked"
                            if (notification_settings(is_found[0].user.id, 'like_notify')) == True:
                                if not(user.id == is_found[0].user.id):
                                    if not Notification.objects.filter(msg_type='like', skigit_id=is_found[0].id,
                                                                       user=is_found[0].user, from_user=user).exists():
                                        Notification.objects.create(msg_type='like', skigit_id=is_found[0].id,
                                                                    user=is_found[0].user, from_user=user,
                                                                    message='skigit_like')
                                    else:
                                        Notification.objects.filter(msg_type='like', skigit_id=is_found[0].id,
                                                                    user=is_found[0].user, from_user=user
                                                                    ).update(is_read=False, message='skigit_updated_like',
                                                                             )
                        else:
                            Like.objects.create(skigit=is_found[0], user=user, status=True, is_read=False)
                            if not (user == is_found[0].user):
                                if (notification_settings(is_found[0].user.id, 'like_notify')) == True:
                                    if not Notification.objects.filter(msg_type='like', skigit_id=is_found[0].id,
                                                                       user=is_found[0].user, from_user=user).exists():
                                        Notification.objects.create(msg_type='like', skigit_id=is_found[0].id,
                                                                    user=is_found[0].user, from_user=user,
                                                                    message='skigit_like')
                                    else:
                                        Notification.objects.filter(msg_type='like', skigit_id=is_found[0].id,
                                                                    user=is_found[0].user, from_user=user
                                                                    ).update(is_read=False, message='skigit_updated_like',
                                                                             )
                            message = "new entry in like table"
                            is_success = True
                            like = 1
                    except MultipleObjectsReturned:
                        message = "Oops ! Server Encounter An " \
                                  "Error Into This Skigit Like"
                        is_success = False
                        response_data['message'] = message
                        response_data['is_success'] = is_success
                        response_data['like'] = like
                        return JsonResponse(response_data)
                else:
                    message = "Invalid Skigit Identity"
            else:
                message = "Please Login And Then Try To Like Skigit"
        else:
            message = "Skigit Identity Not Found"
    else:
        message = "Invalid Request"
    response_data['message'] = message
    response_data['like'] = like
    response_data['is_success'] = is_success
    return JsonResponse(response_data)


@csrf_exempt
def skigit_i_unlike(request):
    skigit_id, message, like_count, is_found, unlike = None, None, None, None, None
    is_success = False
    response_data = {}
    skigit_id = request.POST.get('skigit_id', None)
    if request.is_ajax() and request.method == 'POST':
        user = request.user
        is_found = Video.objects.filter(pk=skigit_id)
        if skigit_id and skigit_id is not None:
            if request.user.is_authenticated():
                user = request.user
                if Like.objects.filter(skigit__id=skigit_id, user_id=user.id).exists():
                    try:
                        unlike = Like.objects.filter(skigit__id=skigit_id, user_id=user.id).update(status=False)
                        if Notification.objects.filter(msg_type='like', skigit_id=is_found[0].id,
                                                       user=is_found[0].user, from_user=user).exists():
                            Notification.objects.filter(msg_type='like', skigit_id=is_found[0].id, user=is_found[0].user, from_user=user
                                                        ).update(msg_type='unlike_deleted',
                                                                 message='Unlike', is_view=False,
                                                                 is_active=False, is_read=True)
                        is_success = True
                        message = ""
                    except MultipleObjectsReturned:
                        message = "Oops ! Server Encounter An " \
                                  "Error Into This Skigit Like"
                        is_success = False
                        response_data['message'] = message
                        response_data['is_success'] = is_success
                        response_data['unlike'] = unlike
                        return JsonResponse(response_data)
                else:
                    message = "Invalid Skigit Identity"
            else:
                message = "Please Login And Then Try To Like Skigit"
        else:
            message = "Skigit Identity Not Found"
    else:
        message = "Invalid Request"
    response_data['message'] = message
    response_data['unlike'] = unlike
    response_data['is_success'] = is_success
    return JsonResponse(response_data)


@csrf_exempt
def my_favourite_skigit(request):
    """
         Favourite skigit
    """
    response_data = {}
    is_success = False
    is_fav, message = None, None
    skigit_id = request.POST.get('skigit_id', None)
    if request.is_ajax() and request.method == 'POST':
        if skigit_id and skigit_id is not None:
            if request.user.is_authenticated():
                user = request.user
                is_found = Video.objects.filter(pk=skigit_id)
                if is_found and is_found is not None:
                    try:
                        if Favorite.objects.filter(skigit__id=skigit_id, user_id=user.id).exists():
                            is_fav = Favorite.objects.filter(skigit__id=skigit_id, user_id=user.id).update(status=1)
                            is_success = True
                            message = "Favorite Skigit"
                        else:
                            Favorite.objects.create(skigit=is_found[0], user=user, status=1)
                            message = "new entry in favorite table"
                            is_success = True
                            is_fav = 1
                    except MultipleObjectsReturned:
                        message = "Oops ! Server Encounter An " \
                                  "Error Into This Favorite Skigit"
                        is_success = False
                        response_data['message'] = message
                        response_data['is_success'] = is_success
                        response_data['is_fav'] = is_fav
                        return JsonResponse(response_data)
                else:
                    message = "Invalid Skigit Identity"
            else:
                message = "Please Login And Then Try To Like Skigit"
        else:
            message = "Skigit Identity Not Found"
    else:
        message = "Invalid Request"
    response_data['message'] = message
    response_data['is_fav'] = is_fav
    response_data['is_success'] = is_success
    return JsonResponse(response_data)


@csrf_exempt
def un_favourite_skigit(request):
    """
         Unfavoured skigit
    """
    response_data = {}
    is_success = False
    is_fav, message = None, None
    skigit_id = request.POST.get('skigit_id', None)
    if request.is_ajax() and request.method == 'POST':
        if skigit_id and skigit_id is not None:
            if request.user.is_authenticated():
                user = request.user
                if Favorite.objects.filter(skigit__id=skigit_id, user_id=user.id).exists():
                    try:
                        is_fav = Favorite.objects.filter(skigit__id=skigit_id, user_id=user.id).update(status=0)
                        is_success = True
                        message = "Unfavoured skigit"
                    except MultipleObjectsReturned:
                        message = "Oops ! Server Encounter An " \
                                  "Error Into This Skigit Like"
                        is_success = False
                        response_data['message'] = message
                        response_data['is_success'] = is_success
                        response_data['is_fav'] = is_fav
                        return JsonResponse(response_data)
                else:
                    message = "Invalid Skigit Identity"
            else:
                message = "Please Login And Then Try To Like Skigit"
        else:
            message = "Skigit Identity Not Found"
    else:
        message = "Invalid Request"
    response_data['message'] = message
    response_data['is_fav'] = is_fav
    response_data['is_success'] = is_success
    return JsonResponse(response_data)


@csrf_protect
def i_am_following(request):
    """
        Follow Skigit User
    """
    response_data = {}
    is_success = False
    is_follow, message = None, None
    follow_id = request.POST.get('follow_id', None)
    skigit_id = request.POST.get('skigit_id', None)
    if request.is_ajax() and request.method == 'POST':

        if follow_id and follow_id is not None:
            if request.user.is_authenticated():
                follow_msg = 'Congratulations '
                follow_msg += request.user.username
                follow_msg += ' Started following you.'
                user = request.user
                is_found = User.objects.get(pk=follow_id)
                if is_found and is_found is not None:
                    try:
                        if Follow.objects.filter(follow=follow_id, user_id=user.id).exists():
                            is_follow = Follow.objects.filter(follow=follow_id, user_id=user.id).update(status=True)
                            is_success = True
                            if (notification_settings(is_found.id, 'follow_un_follow_notify')) == True:
                                if not (user == is_found):
                                    if not Notification.objects.filter(msg_type='follow', user=is_found,
                                                                       from_user=user).exists():
                                        Notification.objects.create(msg_type='follow', skigit_id=skigit_id, user=is_found,
                                                                    from_user=user, message=follow_msg)
                                    else:
                                        Notification.objects.filter(msg_type='follow', skigit_id=skigit_id, user=is_found,
                                                                    from_user=user).update(is_read=False,
                                                                                           message=follow_msg)
                            message = "Following Skigit"
                        else:
                            Follow.objects.create(follow=is_found, user=user, status=True)
                            if (notification_settings(is_found.id, 'follow_un_follow_notify')) == True:
                                if not (user.id == is_found):
                                    if not Notification.objects.filter(msg_type='follow', user=is_found,
                                                                       from_user=user).exists():
                                        Notification.objects.create(msg_type='follow', skigit_id=skigit_id,
                                                                    user=is_found, from_user=user, message=follow_msg)
                                    else:
                                        Notification.objects.filter(msg_type='follow', skigit_id=skigit_id,
                                                                    user=is_found, from_user=user).update(is_read=False,
                                                                                                         message=follow_msg)
                            message = "new entry in follow table"
                            is_success = True
                            is_follow = 1
                    except MultipleObjectsReturned:
                        message = "Oops ! Server Encounter An " \
                                  "Error Into This follow Skigit"
                        is_success = False
                        response_data['message'] = message
                        response_data['is_success'] = is_success
                        response_data['is_follow'] = is_follow
                        return JsonResponse(response_data)
                else:
                    message = "Invalid User Identity"
            else:
                message = "Please Login And Then Try To Follow User"
        else:
            message = "Skigit User Identity Not Found"
    else:
        message = "Invalid Request"
    response_data['message'] = message
    response_data['is_follow'] = is_follow
    response_data['is_success'] = is_success
    return JsonResponse(response_data)


@csrf_protect
def un_following(request):
    """
        Un Follow Skigit User
    """
    response_data = {}
    is_success = False
    is_follow, message = None, None
    follow_id = request.POST.get('follow_id', None)
    if request.is_ajax() and request.method == 'POST':
        user = request.user
        is_found = User.objects.get(pk=follow_id)
        if follow_id and follow_id is not None:
            if request.user.is_authenticated():
                if Follow.objects.filter(user=request.user.id, follow=follow_id, status=True).exists():
                    try:
                        is_follow = Follow.objects.filter(user=request.user.id, follow=follow_id,
                                                          status=True).update(status=False)
                        if not (user == is_found):
                            if Notification.objects.filter(msg_type='follow', user=is_found, from_user=user).exists():
                                Notification.objects.filter(msg_type='follow', user=is_found,
                                                            from_user=user).update(msg_type='unfollow_deleted',
                                                                                   is_read=True, is_active=False,
                                                                                   is_view=True)
                        is_success = True
                        message = "Un Follow User Sussessfully"
                    except MultipleObjectsReturned:
                        message = "Oops ! Server Encounter An " \
                                  "Error Into This Skigit Like"
                        is_success = False
                        response_data['message'] = message
                        response_data['is_success'] = is_success
                        response_data['is_follow'] = is_follow
                        return JsonResponse(response_data)
                else:
                    message = "Invalid follower Identity"
            else:
                message = "Please Login And Then Try To Unfollow Skigit User"
        else:
            message = "Skigit User Identity Not Found"
    else:
        message = "Invalid Request"
    response_data['message'] = message
    response_data['is_follow'] = is_follow
    response_data['is_success'] = is_success
    return JsonResponse(response_data)


@login_required(login_url='/')
@payment_required
@require_filled_profile
def i_am_following_view(request, template='sk_cat/skigit_plugged_into.html',
                        page_template='sk_cat/i_am_following_body.html'):
    follow_list = []
    try:
        follow_record = Follow.objects.filter(user=request.user.id, status=True).order_by('-follow__first_name')
        for following in follow_record:
            if User.objects.exclude(id=request.user.id).filter(id=following.follow.id).exists():
                user_follow_detail = User.objects.exclude(id=request.user.id).filter(id=following.follow.id)
                for user_detail in user_follow_detail:
                    user_profile = Profile.objects.get(user=user_detail)
                    name = user_detail.get_full_name()
                    if user_profile.profile_img:
                        l_img = get_thumbnail(user_profile.profile_img, '100x100', quality=99, format='PNG').url
                    else:
                        l_img = "/static/skigit/detube/images/noimage_user.jpg"
                    follow_count = Follow.objects.exclude(follow=request.user.id).filter(follow=user_detail.id, status=True).count()
                    follow_list.append({'user': request.user.id, 'follower': user_detail.id, 'name': name,
                         'follower_img': l_img, 'username': user_detail.username, 'count': follow_count})
        follow_list = sorted(follow_list, key=lambda follow: (follow['name']))

    except ObjectDoesNotExist:
        messages.error(request, 'No Following user were found...!!!')
        return HttpResponseRedirect("/")

    context = {
        'video_detail': follow_list,
        'current_user': request.user.username,
        'video_type': 'i_am_following',
    }

    if request.is_ajax():
        template = page_template
    return render(request, template, context)


@login_required(login_url='/')
@csrf_protect
def share_to_friends(request):
    response_data = {}
    if request.is_ajax() and request.method == 'POST':
        # try:
            time_zone = request.POST.get('time_zone', '')
            skigit_id = request.POST.get('vid_id', None)
            f_list = request.POST.getlist('friend_list[]', None)
            notify = Profile.objects.filter(user=request.user).values('share_notify')
            for f_id in f_list:
                if User.objects.filter(id=f_id).exists():
                    user_obj = User.objects.get(id=f_id)
                    share_obj = Share.objects.create(user=request.user, to_user=user_obj, skigit_id_id=skigit_id)
                    if VideoDetail.objects.filter(id=int(skigit_id)).exists():
                        video = VideoDetail.objects.get(id=int(skigit_id))
                        business_share_invoice(request.user.id, video.skigit_id.id)
                        mail_id = user_obj.email
                        mail_body = "<center><label><h3 style='color:#1C913F;font-family: " + "Proza Libre" + ", sans-serif;'>" \
                                    "You gotta check this out!<h3></label></center>\r\n\r\n<p><center>" \
                                    "<a href='http://skigit.com?id=" + str(skigit_id) + "'style='text-decoration:none;color:#0386B8;margin: 10px auto;display: table;font-size:16px;font-family: " + "Proza Libre" + ", sans-serif;'>" + video.title + "</a>" \
                                    "</center></p>\r\n<p style='text-align:justyfy;'>" + video.why_rocks + "</p>\r\n" \
                                    "<p><center><img src='http://skigit.com/static/skigit/images/shair.png' style='width:165px;' class='img-responsive'></center></p>"
                        send_email(request.user.username + ' Shared an Awesome Skigit with You!', mail_body, mail_id, '', EMAIL_HOST_VIDEO)

                        f_nt_message = " "
                        f_nt_message += "You are on the Radar! "
                        f_nt_message += request.user.username
                        f_nt_message += " has shared the awesome Skigit "
                        f_nt_message += video.title
                        f_nt_message += " with you! "
                        if (notification_settings(user_obj.id, 'share_notify')) == True:
                            if not Notification.objects.filter(msg_type='share', user=user_obj,
                                                               skigit_id=video.skigit_id.id,
                                                               from_user=request.user).exists():
                                Notification.objects.create(user=user_obj, from_user=request.user,
                                                            skigit_id=video.skigit_id.id,
                                                            msg_type='share',
                                                            message=f_nt_message)
                            else:
                                Notification.objects.filter(user=user_obj, skigit_id=video.skigit_id.id,
                                                            from_user=request.user,
                                                            msg_type='share').update(msg_type='share_old', is_view=True,
                                                                                     is_active=False, is_read=True)
                                Notification.objects.filter(user=user_obj, from_user=request.user,
                                                            skigit_id=video.skigit_id.id, msg_type='share_old').delete()
                                Notification.objects.create(user=user_obj, from_user=request.user,
                                                            skigit_id=video.skigit_id.id, msg_type='share',
                                                            message=f_nt_message)
            response_data['is_success'] = True
            response_data['message'] = 'Skigit Share Successfully'
            response_data['date'] = get_time_delta(datetime.datetime.utcnow(), time_zone)
        #
        # except ObjectDoesNotExist:
        #     response_data['is_success'] = False
    return JsonResponse(response_data)


@login_required(login_url='/')
def email_share_friends(request):
    response_data = {}
    if request.is_ajax() and request.method == 'POST':
        # try:
            em = []
            email = request.POST.get('email_list', None)
            video_id = request.POST.get('video_id', None)
            if VideoDetail.objects.filter(id=int(video_id)).exists():
                video = VideoDetail.objects.get(id=int(video_id))
                mail_body = "<center><label><h3 style='color:#1C913F;font-family: "+"Proza Libre"+", sans-serif;'>" \
                        "You gotta chek this out!<h3></label></center>\r\n\r\n<p><center>" \
                        "<a href='http://skigit.com?id="+str(video_id)+"'style='text-decoration:none;color:#0386B8;margin: 10px auto;display: table;font-size:16px;font-family: "+"Proza Libre"+", sans-serif;'>"+video.title +"</a>" \
                        "</center></p>\r\n<p style='text-align:justyfy;'>"+video.why_rocks+"</p>\r\n" \
                        "<p><center><img src='http://skigit.com/static/skigit/images/shair.png' style='width:165px;' class='img-responsive'></center></p>"
                if email:
                    em = email.split(',')
                    for mail_id in em:
                        send_email(request.user.username+' Shared an Awesome Skigit with You!', mail_body, mail_id, '', EMAIL_HOST_VIDEO)
                response_data['is_success'] = True
                response_data['message'] = 'Skigit Shared Successfully'
            else:
                response_data['is_success'] = False
        #         response_data['message'] = 'Trying to share skigit is not found.'
        # except ObjectDoesNotExist:
        #     response_data['is_success'] = False
        #     response_data['message'] = 'Skigit Share failed'
    return JsonResponse(response_data)


@payment_required
@require_filled_profile
def skigit_search_view(request, template='pages/skigit_search.html',
                       page_template='pages/search_body.html'):

    if request.method == 'GET':

        like_dict = []
        friend_list = []
        ski_share_list = []
        if request.user.is_authenticated():

            if Friend.objects.filter(Q(to_user=request.user.id) | Q(from_user=request.user.id), status=1).exists():
                f_list = Friend.objects.filter(Q(to_user=request.user.id) | Q(from_user=request.user.id), status=1)
                from_user_list = f_list.exclude(from_user=request.user.id).values_list('from_user',
                                                                                       flat=True).distinct()
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
            video_likes = Like.objects.filter(user_id=request.user.id, status=True)
            for likes in video_likes:
                like_dict.append(likes.skigit_id)
        vid = VideoDetail.objects.select_related('skigit_id').filter(status=1, is_active=True).order_by('-updated_date')
        serializer = VideoDetailSerializer(vid, many=True)
        for vid_data in vid:
            sharObj = Share.objects.filter(skigit_id=vid_data, is_active=True, user=request.user.id).order_by('to_user', '-pk').distinct('to_user')
            for sh in sharObj:
                ski_share_list.append(
                    {'share_date': sh.created_date, 'username': sh.to_user.username, 'vid': sh.skigit_id_id})
        context = {
            'video_detail': serializer.data,
            'video_likes': like_dict,
            'friend_list': friend_list,
            'order_value': '1',
            'togal_val': '1',
            'skigit_list': ski_share_list,
            'users': get_all_logged_in_users()
        }
        # if request.is_ajax():
        #     template = page_template
        return render(request, template, context)

    if request.method == 'POST':
        togal_val = None
        like_dict = []
        friend_list = []
        ski_share_list = []
        if request.user.is_authenticated():

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
            video_likes = Like.objects.filter(user_id=request.user.id, status=True)
            for likes in video_likes:
                like_dict.append(likes.skigit_id)
        search_text = request.POST.get('searchBox', None)
        if search_text:
            profile = Profile.objects.filter(Q(company_title__icontains=search_text))
            if profile:
                for p in profile:
                    vid = VideoDetail.objects.select_related(
                        'skigit_id').filter(Q(skigit_id__user__id=p.id) |
                                            Q(skigit_id__user__username__icontains=search_text) |
                                            Q(title__icontains=search_text), status=1, is_active=True
                                            ).order_by('-updated_date')
                    serializer = VideoDetailSerializer(vid, many=True)
                    for vid_data in vid:
                        sharObj = Share.objects.filter(skigit_id=vid_data, is_active=True,
                                                       user=request.user.id).order_by('to_user', '-pk').distinct(
                            'to_user')
                        for sh in sharObj:
                            ski_share_list.append(
                                {'share_date': sh.created_date, 'username': sh.to_user.username,
                                 'vid': sh.skigit_id_id})
            else:
                vid = VideoDetail.objects.select_related(
                    'skigit_id').filter(Q(title__icontains=search_text) |
                                        Q(skigit_id__user__username__icontains=search_text),
                                        status=1, is_active=True).order_by('-updated_date')
                serializer = VideoDetailSerializer(vid, many=True)
                for vid_data in vid:
                    sharObj = Share.objects.filter(skigit_id=vid_data, is_active=True,
                                                   user=request.user.id).order_by('to_user', '-pk').distinct(
                        'to_user')
                    for sh in sharObj:
                        ski_share_list.append(
                            {'share_date': sh.created_date, 'username': sh.to_user.username,
                             'vid': sh.skigit_id_id})
            context = {
                'video_detail': serializer.data,
                'video_likes': like_dict,
                'friend_list': friend_list,
                'search_text': search_text,
                'order_value': '1',
                'togal_val': '1',
                'skigit_list': ski_share_list,
                'users': get_all_logged_in_users()
            }
            # if request.is_ajax():
            #     template = page_template
            return render(request, template, context)
        else:

            vid = VideoDetail.objects.select_related('skigit_id').filter(status=1, is_active=True).order_by('-updated_date')
            serializer = VideoDetailSerializer(vid, many=True)
            for vid_data in vid:
                sharObj = Share.objects.filter(skigit_id=vid_data, is_active=True,
                                               user=request.user.id).order_by('to_user', '-pk').distinct(
                    'to_user')
                for sh in sharObj:
                    ski_share_list.append(
                        {'share_date': sh.created_date, 'username': sh.to_user.username,
                         'vid': sh.skigit_id_id})
            context = {
                'video_detail': serializer.data,
                'video_likes': like_dict,
                'friend_list': friend_list,
                'search_text': search_text,
                'order_value': '1',
                'togal_val': '1',
                'skigit_list': ski_share_list,
                'users': get_all_logged_in_users()
            }
            # if request.is_ajax():
            #     template = page_template
            return render(request, template, context)


def search_ordering_skigit(request, order=None,
                           template='pages/skigit_search.html',
                           page_template='pages/search_body.html'):
    search_text = None
    like_dict = []
    friend_list = []
    ski_share_list = []
    if request.user.is_authenticated():

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
        video_likes = Like.objects.filter(user_id=request.user.id, status=True)
        for likes in video_likes:
            like_dict.append(likes.skigit_id)

    order = order.split('&')
    if len(order) == 2 and (order[0]).strip() == '1':
        ordering = '-created_date'
        order_by = '2-%s' % order[1]
        togal_val = '2'
        search_text = (order[1]).strip()
    elif len(order) == 2 and (order[0]).strip() == '2':
        ordering = 'created_date'
        order_by = '1-%s' % (order[1]).strip()
        search_text = (order[1]).strip()
        togal_val = '1'
    elif (order[0]).strip() == '2':
        ordering = 'created_date'
        order_by = '1'
        togal_val = '1'
    elif (order[0]).strip() == '1':
        ordering = '-created_date'
        order_by = '2'
        togal_val = '2'

    if search_text:
        profile = Profile.objects.filter(Q(company_title__icontains=search_text))
        if profile:
            for p in profile:
                vid = VideoDetail.objects.select_related(
                    'skigit_id').filter(Q(skigit_id__user__id=p.id) |
                                        Q(skigit_id__user__username__icontains=search_text) |
                                        Q(title__icontains=search_text), status=1, is_active=True
                                        ).order_by(ordering)
                serializer = VideoDetailSerializer(vid, many=True)
                for vid_data in vid:
                    sharObj = Share.objects.filter(skigit_id=vid_data, is_active=True,
                                                   user=request.user.id).order_by('to_user', '-pk').distinct(
                        'to_user')
                    for sh in sharObj:
                        ski_share_list.append(
                            {'share_date': sh.created_date, 'username': sh.to_user.username,
                             'vid': sh.skigit_id_id})
        else:
            vid = VideoDetail.objects.select_related(
                'skigit_id').filter(Q(title__icontains=search_text) |
                                    Q(skigit_id__user__username__icontains=search_text),
                                    status=1, is_active=True).order_by(ordering)
            serializer = VideoDetailSerializer(vid, many=True)
            for vid_data in vid:
                sharObj = Share.objects.filter(skigit_id=vid_data, is_active=True,
                                               user=request.user.id).order_by('to_user', '-pk').distinct(
                    'to_user')
                for sh in sharObj:
                    ski_share_list.append(
                        {'share_date': sh.created_date, 'username': sh.to_user.username,
                         'vid': sh.skigit_id_id})
        context = {
            'video_detail': serializer.data,
            'video_likes': like_dict,
            'friend_list': friend_list,
            'search_text': search_text,
            'order_value': order_by,
            'togal_val': togal_val,
            'skigit_list': ski_share_list,
            'users': get_all_logged_in_users()
        }
        return render(request, template, context)
    else:
        vid = VideoDetail.objects.select_related('skigit_id').filter(status=1, is_active=True).order_by(ordering)
        serializer = VideoDetailSerializer(vid, many=True)
        for vid_data in vid:
            sharObj = Share.objects.filter(skigit_id=vid_data, is_active=True,
                                           user=request.user.id).order_by('to_user', '-pk').distinct(
                'to_user')
            for sh in sharObj:
                ski_share_list.append(
                    {'share_date': sh.created_date, 'username': sh.to_user.username,
                     'vid': sh.skigit_id_id})
        context = {
            'video_detail': serializer.data,
            'video_likes': like_dict,
            'friend_list': friend_list,
            'search_text': search_text,
            'order_value': order_by,
            'togal_val': togal_val,
            'skigit_list': ski_share_list,
            'users': get_all_logged_in_users()
        }
        # if request.is_ajax():
        #     template = page_template
        return render(request, template, context)


def skigit_count_update(request):
    response_data = {}
    if request.is_ajax() and request.method == 'POST':
        try:
            video_id = request.POST.get('skigit_id', None)
            if VideoDetail.objects.filter(id=int(video_id)).exists():
                vid = VideoDetail.objects.get(id=int(video_id))
                vid.view_count = vid.view_count + 1
                vid.save()
                response_data['view_count'] = vid.view_count
                response_data['is_success'] = True
                response_data['message'] = 'view count updated'
        except ObjectDoesNotExist:
            response_data['is_success'] = False
    return JsonResponse(response_data)


@xframe_options_exempt
def embed_skigit(request, video):
    if VideoDetail.objects.filter(skigit_id__video_id=video, is_active=True, status=1).exists():
        video_id = video
    else:
        video_id = None

    image_url = request.GET.get('href', None)
    return render(request, 'includes/skigit_embed.html', locals())


def sort_by_date(request, cat_slug, order_by, template='sk_cat/category_bash.html',
                 page_template='sk_cat/category_body.html'):

    like_dict = []
    share_dict = []
    plug_dict = []
    ski_share_list = []
    video_detail = []
    like_skigit = []
    friend_list = []

    category_current = Category.objects.get(cat_slug=cat_slug)

    if order_by == '1':
        order_by = 2
        videos = VideoDetail.objects.filter(category=category_current, status=1, is_active=True).order_by('-created_date')
    else:
        order_by = 1
        videos = VideoDetail.objects.filter(category=category_current, status=1, is_active=True).order_by('created_date')
    vid_latest_uploaded = videos[0]

    for vid in videos:
        like_count = Like.objects.filter(skigit=vid.skigit_id, status=True).count()
        like_dict.append({'id': vid.id, 'count': like_count})
        video_share = Share.objects.filter(skigit_id=vid, is_active=True).count()
        share_dict.append({'id': vid.id, 'count': video_share})
        video_plug = VideoDetail.objects.filter(plugged_skigit=vid.skigit_id, is_plugged=True, status=1).count()
        plug_dict.append({'id': vid.id, 'count': video_plug})
        sharObj = Share.objects.filter(skigit_id=vid, is_active=True, user=request.user.id).order_by(
            'to_user', '-pk').distinct('to_user')
        for sh in sharObj:
            ski_share_list.append(
                {'share_date': sh.created_date, 'username': sh.to_user.username, 'vid': sh.skigit_id_id})
        if vid.made_by:
            us_profile = Profile.objects.get(user=vid.made_by)
            if us_profile.logo_img.filter(is_deleted=False).all().count() > 0:
                vid.default_business_logo = us_profile.logo_img.filter(is_deleted=False).all()[0]
            else:
                vid.default_business_logo = ''
        else:
            vid.default_business_logo = ''
        video_detail.append(vid)

    video_likes = Like.objects.filter(user_id=request.user.id, status=True)
    for likes in video_likes:
        like_skigit.append(likes.skigit_id)

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
    context = {
        'page_template': page_template,
        'category_current': category_current,
        'video_detail': video_detail,
        'vid_latest_uploaded': vid_latest_uploaded,
        'friend_list': friend_list,
        'video_share': share_dict,
        'video_plug': plug_dict,
        'video_likes': like_skigit,
        'like_count': like_dict,
        'skigit_list': ski_share_list,
        'order': order_by,
        'order_title': 1,
        'order_views': 1,
        'order_random': 1,
        'order_likes': 1,
        'page_type': 'sort_date',
        'users': get_all_logged_in_users()
    }

    if request.is_ajax():
        template = page_template
    return render(request, template, context)


def sort_by_title(request, cat_slug, order_by, template='sk_cat/category_bash.html',
                 page_template='sk_cat/category_body.html'):

    like_dict = []
    share_dict = []
    plug_dict = []
    ski_share_list = []
    video_detail = []
    like_skigit = []
    friend_list = []

    category_current = Category.objects.get(cat_slug=cat_slug)

    if order_by == '1':
        order_by = 2
        videos = VideoDetail.objects.filter(category=category_current, status=1, is_active=True).order_by('-title')
    else:
        order_by = 1
        videos = VideoDetail.objects.filter(category=category_current, status=1, is_active=True).order_by('title')
    vid_latest_uploaded = videos.first

    for vid in videos:
        like_count = Like.objects.filter(skigit=vid.skigit_id, status=True).count()
        like_dict.append({'id': vid.id, 'count': like_count})
        video_share = Share.objects.filter(skigit_id=vid, is_active=True).count()
        share_dict.append({'id': vid.id, 'count': video_share})
        video_plug = VideoDetail.objects.filter(plugged_skigit=vid.skigit_id, is_plugged=True, status=1).count()
        plug_dict.append({'id': vid.id, 'count': video_plug})
        sharObj = Share.objects.filter(skigit_id=vid, is_active=True, user=request.user.id).order_by(
            'to_user', '-pk').distinct('to_user')
        for sh in sharObj:
            ski_share_list.append(
                {'share_date': sh.created_date, 'username': sh.to_user.username, 'vid': sh.skigit_id_id})
        if vid.made_by:
            us_profile = Profile.objects.get(user=vid.made_by)
            if us_profile.logo_img.filter(is_deleted=False).all().count() > 0:
                vid.default_business_logo = us_profile.logo_img.filter(is_deleted=False).all()[0]
            else:
                vid.default_business_logo = ''
        else:
            vid.default_business_logo = ''
        video_detail.append(vid)

    video_likes = Like.objects.filter(user_id=request.user.id, status=True)
    for likes in video_likes:
        like_skigit.append(likes.skigit_id)

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
    context = {
        'page_template': page_template,
        'category_current': category_current,
        'video_detail': video_detail,
        'vid_latest_uploaded': vid_latest_uploaded,
        'friend_list': friend_list,
        'video_share': share_dict,
        'video_plug': plug_dict,
        'video_likes': like_skigit,
        'like_count': like_dict,
        'skigit_list': ski_share_list,
        'order': 1,
        'order_title': order_by,
        'order_views': 1,
        'order_random': 1,
        'order_likes': 1,
        'page_type': 'sort_title',
        'users': get_all_logged_in_users()
    }

    if request.is_ajax():
        template = page_template
    return render(request, template, context)


def sort_by_views(request, cat_slug, order_by, template='sk_cat/category_bash.html',
                 page_template='sk_cat/category_body.html'):

    like_dict = []
    share_dict = []
    plug_dict = []
    ski_share_list = []
    video_detail = []
    like_skigit = []
    friend_list = []

    category_current = Category.objects.get(cat_slug=cat_slug)

    if order_by == '1':
        order_by = 2
        videos = VideoDetail.objects.filter(category=category_current, status=1, is_active=True).order_by('-view_count')
    else:
        order_by = 1
        videos = VideoDetail.objects.filter(category=category_current, status=1, is_active=True).order_by('view_count')
    vid_latest_uploaded = videos.first

    for vid in videos:
        like_count = Like.objects.filter(skigit=vid.skigit_id, status=True).count()
        like_dict.append({'id': vid.id, 'count': like_count})
        video_share = Share.objects.filter(skigit_id=vid, is_active=True).count()
        share_dict.append({'id': vid.id, 'count': video_share})
        video_plug = VideoDetail.objects.filter(plugged_skigit=vid.skigit_id, is_plugged=True, status=1).count()
        plug_dict.append({'id': vid.id, 'count': video_plug})
        sharObj = Share.objects.filter(skigit_id=vid, is_active=True, user=request.user.id).order_by(
            'to_user', '-pk').distinct('to_user')
        for sh in sharObj:
            ski_share_list.append(
                {'share_date': sh.created_date, 'username': sh.to_user.username, 'vid': sh.skigit_id_id})
        if vid.made_by:
            us_profile = Profile.objects.get(user=vid.made_by)
            if us_profile.logo_img.filter(is_deleted=False).all().count() > 0:
                vid.default_business_logo = us_profile.logo_img.filter(is_deleted=False).all()[0]
            else:
                vid.default_business_logo = ''
        else:
            vid.default_business_logo = ''
        video_detail.append(vid)

    video_likes = Like.objects.filter(user_id=request.user.id, status=True)
    for likes in video_likes:
        like_skigit.append(likes.skigit_id)

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
    context = {
        'page_template': page_template,
        'category_current': category_current,
        'video_detail': video_detail,
        'vid_latest_uploaded': vid_latest_uploaded,
        'friend_list': friend_list,
        'video_share': share_dict,
        'video_plug': plug_dict,
        'video_likes': like_skigit,
        'like_count': like_dict,
        'skigit_list': ski_share_list,
        'order': 1,
        'order_title': 1,
        'order_likes': 1,
        'order_random': 1,
        'order_views': order_by,
        'page_type': 'sort_views',
        'users': get_all_logged_in_users()
    }

    if request.is_ajax():
        template = page_template
    return render(request, template, context)


def sort_by_likes(request, cat_slug, order_by, template='sk_cat/category_bash.html',
                 page_template='sk_cat/category_body.html'):

    like_dict = []
    share_dict = []
    plug_dict = []
    ski_share_list = []
    video_detail = []
    like_skigit = []
    friend_list = []

    category_current = Category.objects.get(cat_slug=cat_slug)
    videos = VideoDetail.objects.filter(category=category_current, status=1, is_active=True)

    for vid in videos:
        like_count = Like.objects.filter(skigit=vid.skigit_id, status=True).count()
        vid.like_count = like_count
        like_dict.append({'id': vid.id, 'count': like_count})
        video_share = Share.objects.filter(skigit_id=vid, is_active=True).count()
        share_dict.append({'id': vid.id, 'count': video_share})
        video_plug = VideoDetail.objects.filter(plugged_skigit=vid.skigit_id, is_plugged=True, status=1).count()
        plug_dict.append({'id': vid.id, 'count': video_plug})
        sharObj = Share.objects.filter(skigit_id=vid, is_active=True, user=request.user.id).order_by(
            'to_user', '-pk').distinct('to_user')
        for sh in sharObj:
            ski_share_list.append(
                {'share_date': sh.created_date, 'username': sh.to_user.username, 'vid': sh.skigit_id_id})
        if vid.made_by:
            us_profile = Profile.objects.get(user=vid.made_by)
            if us_profile.logo_img.filter(is_deleted=False).all().count() > 0:
                vid.default_business_logo = us_profile.logo_img.filter(is_deleted=False).all()[0]
            else:
                vid.default_business_logo = ''
        else:
            vid.default_business_logo = ''
        video_detail.append(vid)

    video_likes = Like.objects.filter(user_id=request.user.id, status=True)
    for likes in video_likes:
        like_skigit.append(likes.skigit_id)

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
    if order_by == '1':
        order_by = 2
        video_detail.sort(key=operator.attrgetter('like_count'), reverse=True)
    else:
        order_by = 1
        video_detail.sort(key=operator.attrgetter('like_count'), reverse=False)
    vid_latest_uploaded = video_detail[0]
    context = {
        'page_template': page_template,
        'category_current': category_current,
        'video_detail': video_detail,
        'vid_latest_uploaded': vid_latest_uploaded,
        'friend_list': friend_list,
        'video_share': share_dict,
        'video_plug': plug_dict,
        'video_likes': like_skigit,
        'like_count': like_dict,
        'skigit_list': ski_share_list,
        'order': 1,
        'order_title': 1,
        'order_views': 1,
        'order_random': 1,
        'order_likes': order_by,
        'page_type': 'sort_likes',
        'users': get_all_logged_in_users()
    }

    if request.is_ajax():
        template = page_template
    return render(request, template, context)


def sort_by_random(request, cat_slug, template='sk_cat/category_bash.html',
                   page_template='sk_cat/category_body.html'):

    like_dict = []
    share_dict = []
    plug_dict = []
    ski_share_list = []
    video_detail = []
    like_skigit = []
    friend_list = []

    category_current = Category.objects.get(cat_slug=cat_slug)
    videos = VideoDetail.objects.filter(category=category_current, status=1, is_active=True).order_by('?')
    vid_latest_uploaded = videos.first

    for vid in videos:
        like_count = Like.objects.filter(skigit=vid.skigit_id, status=True).count()
        vid.like_count = like_count
        like_dict.append({'id': vid.id, 'count': like_count})
        video_share = Share.objects.filter(skigit_id=vid, is_active=True).count()
        share_dict.append({'id': vid.id, 'count': video_share})
        video_plug = VideoDetail.objects.filter(plugged_skigit=vid.skigit_id, is_plugged=True, status=1).count()
        plug_dict.append({'id': vid.id, 'count': video_plug})
        sharObj = Share.objects.filter(skigit_id=vid, is_active=True, user=request.user.id).order_by(
            'to_user', '-pk').distinct('to_user')
        for sh in sharObj:
            ski_share_list.append(
                {'share_date': sh.created_date, 'username': sh.to_user.username, 'vid': sh.skigit_id_id})
        if vid.made_by:
            us_profile = Profile.objects.get(user=vid.made_by)
            if us_profile.logo_img.filter(is_deleted=False).all().count() > 0:
                vid.default_business_logo = us_profile.logo_img.filter(is_deleted=False).all()[0]
            else:
                vid.default_business_logo = ''
        else:
            vid.default_business_logo = ''
        video_detail.append(vid)

    video_likes = Like.objects.filter(user_id=request.user.id, status=True)
    for likes in video_likes:
        like_skigit.append(likes.skigit_id)

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

    context = {
        'page_template': page_template,
        'category_current': category_current,
        'video_detail': video_detail,
        'vid_latest_uploaded': vid_latest_uploaded,
        'friend_list': friend_list,
        'video_share': share_dict,
        'video_plug': plug_dict,
        'video_likes': like_skigit,
        'like_count': like_dict,
        'skigit_list': ski_share_list,
        'order': 1,
        'order_title': 1,
        'order_views': 1,
        'order_likes': 1,
        'page_type': 'sort_random',
        'users': get_all_logged_in_users()
    }

    if request.is_ajax():
        template = page_template
    return render(request, template, context)


def ajax_remove_images(request):
    response_data = {'status_code': 404, 'is_success': False, 'message': 'Error into Remove Profile/Coupan Image..'}
    if request.is_ajax() and request.method == 'POST':
        try:
            img = request.POST.get('image_type', None)
            if img == 'profile':
                Profile.objects.filter(user=request.user).update(profile_img=None)
                response_data['is_success'] = True
                response_data['image_type'] = 'profile'
                response_data['message'] = 'Profile image removed successfully!'
                response_data['status_code'] = 200
            elif img == 'coupan':
                Profile.objects.filter(user=request.user).update(coupan_image=None)
                response_data['is_success'] = True
                response_data['status_code'] = 200
                response_data['image_type'] = 'coupan'
                response_data['message'] = 'Coupan removed successfully! '
            else:
                response_data['is_success'] = False
                response_data['message'] = 'Image type was profile or coupan.'
                response_data['status_code'] = 200
        except Exception:
            response_data['is_success'] = False
            response_data['message'] = 'Image type was profile or coupan.'
            response_data['status_code'] = 200
    return JsonResponse(response_data)
