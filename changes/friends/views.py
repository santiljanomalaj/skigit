
from django.http import HttpResponse
from django.views.decorators.clickjacking import xframe_options_exempt
from urllib.request import urlopen
from django.shortcuts import render
from sorl.thumbnail import get_thumbnail
from friends.models import *
from skigit.models import Profile, VideoDetail
from social.models import Follow, Share
from core.utils import json_response, require_filled_profile, payment_required
from django.contrib.auth.models import User
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from heapq import merge
from django.contrib.sessions.models import Session
from django.utils import timezone
from skigit_project import settings
from PIL import Image
from datetime import datetime
from datetime import timedelta
import uuid
import pytz
import json


def web_push_notifications(m_type, to_user, frm_user, ski_id=None, f_nt_message=None):
    """
    Function definition for Notification
    :param m_type: Notification Type <Basis of this differentiate the Notification>
    :param to_user: Notification Receiver User
    :param frm_user: Notification Sent after activity by User
    :param ski_id: Video (Skigit ID) Reference
    :param f_nt_message: Notification Messages by Notification type
    """

    if not Notification.objects.filter(msg_type=m_type, user=to_user, skigit_id=ski_id,
                                       from_user=frm_user).exists():
        Notification.objects.create(msg_type=m_type, user=to_user, skigit_id=ski_id, from_user=frm_user,
                                    message=f_nt_message)
    else:
        new_type = '%s_deleted' % m_type
        Notification.objects.filter(msg_type=m_type, user=to_user,
                                    from_user=frm_user, skigit_id=ski_id).update(msg_type=new_type, is_view=True,
                                                                                 is_read=True, is_active=False)
        Notification.objects.filter(msg_type=new_type, from_user=frm_user, skigit_id=ski_id,
                                    user=to_user).delete()
        Notification.objects.create(msg_type=m_type, user=to_user, from_user=frm_user, skigit_id=ski_id,
                                    message=f_nt_message)


def notification_settings(user, notification_type):
    """
        Notification Settings
    """
    try:
        notify = Profile.objects.filter(user__id=int(user)).values(notification_type)
        return notify[0][notification_type]
    except Exception as e:
        message = e.message
        return None


def get_localize_date(utc_dt, time_zone):
    """
    Function definition for Localizing the Time <UTC to Local Time Conversion function>
    :param utc_dt: Date in UTC (Universal Time Conversion format)(UTC+0:00)
    :param time_zone: Localization Time in Name eg: (Asia/Calcutta) (UTC+5:30)
    :return: Returns localization Date
    """
    local_tz = pytz.timezone(time_zone)
    local_dt = utc_dt.replace(tzinfo=pytz.utc).astimezone(local_tz)
    return local_tz.normalize(local_dt)


def get_time_delta(before_date, time_zone):
    """
    Function Definition for Time Difference between two DateTime (Date)
    :param before_date: Date Which we Can subtract
    :param time_zone: Localization Time in Name eg: (Asia/Calcutta) (UTC+5:30)
    :return: Returns Difference between two date and Time. <In hours/Minute/Seconds/Date with time>
    """
    end_date = get_localize_date(before_date, time_zone)
    after_date = get_localize_date(datetime.utcnow(), time_zone)
    yesterday = get_localize_date((datetime.utcnow() - timedelta(days=1)), time_zone)
    current_day = after_date.day
    prev_day = yesterday.day
    custom_day = before_date.day
    current_week = after_date.isocalendar()[1]
    custom_week = before_date.isocalendar()[1]
    date_diff = after_date - end_date
    day = date_diff.days
    sec = date_diff.seconds
    minute = date_diff.seconds / 60
    hours = minute / 60

    if day == 0 and sec <= 60 and custom_day == current_day:
        return 'Just now'
    elif day == 0 and sec >= 60 and minute <= 59 and custom_day == current_day:
        return '%s minute ago' % int(minute)
    elif day == 0 and minute >= 60 and hours < 24 and custom_day == current_day:
        return '%s hours ago' % int(hours)
    elif day == 1 or custom_day == prev_day and not day == 0:
        return 'Yesterday at %s' % end_date.strftime('%I:%M %p')
    elif 6 >= day >= 2 and current_week == custom_week:
        return '%s at %s' % (end_date.strftime("%a"), end_date.strftime('%I:%M %p'))
    else:
        return '%s %s at %s' % (end_date.strftime("%b"), end_date.strftime("%d"),
                                end_date.strftime('%I:%M %p'))


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


@login_required(login_url='/')
@payment_required
@require_filled_profile
def friendsinvite(request, template='friends/friends_invite.html',
                  page_template='friends/friends_invite_body.html'):
    """
    :param request:
    :param template:
    :param page_template:
    :return:
    """
    friend_list = []
    follow_list = []
    if User.objects.filter(id=request.user.id, is_active=True).exists():
        if Friend.objects.filter(from_user=request.user.id, status='1').exists():
            friends = Friend.objects.filter(from_user=request.user.id, status='1').order_by('-from_user__first_name')
            for friend in friends:
                user_profile = User.objects.get(id=friend.to_user.id)
                ps = Profile.objects.get(user=user_profile)
                name = user_profile.get_full_name()
                follow_count = Follow.objects.exclude(follow=request.user.id).filter(follow=user_profile.id,
                                                                                     status=True).count()
                if ps.profile_img:
                    l_img = get_thumbnail(ps.profile_img, '100x100', quality=99, format='PNG').url
                else:
                    l_img = '/static/skigit/detube/images/noimage_user.jpg'
                friend_list.append({'user': user_profile.id, 'name': name, 'profile_img': l_img,
                                    'status': friend.status, 'username': user_profile.username, 'count': follow_count})
        if Friend.objects.filter(to_user=request.user.id, status='1').exists():
            friends = Friend.objects.filter(to_user=request.user.id, status='1').order_by('-from_user__first_name')
            for friend in friends:
                user_profile = User.objects.get(id=friend.from_user.id)
                ps = Profile.objects.get(user=user_profile)
                name = user_profile.get_full_name()
                follow_count = Follow.objects.exclude(follow=request.user.id).filter(follow=user_profile.id,
                                                                                     status=True).count()
                if ps.profile_img:
                    l_img = get_thumbnail(ps.profile_img, '100x100', quality=99, format='PNG').url
                else:
                    l_img = '/static/skigit/detube/images/noimage_user.jpg'
                friend_list.append({'user': user_profile.id, 'name': name, 'profile_img': l_img,
                                    'status': friend.status, 'username': user_profile.username, 'count': follow_count})
        friend_list = sorted(friend_list, key=lambda k: k['name'])
        follow_list = Follow.objects.exclude(follow=request.user.id).values_list('follow',
                                                                                 flat=True).filter(user=request.user.id,
                                                                                                   status=True)
        context = {
            'friend_list': friend_list,
            'follow_list': follow_list
        }

        if request.is_ajax():
            template = page_template
        return render(request, template, context)


@login_required(login_url='/')
def friendsinvitesearch(request):
    """
        Internal Skigit Friends Invitations Search by using First and Last name.
    """
    search_list = []
    response_data = {'result': False, 'search_list': search_list}
    if request.method == 'POST' and request.is_ajax():
        search = request.POST.get('search_text', None)
        for term in search.split():
            query_result = User.objects.exclude(id=request.user.id).filter(
                Q(Q(first_name__icontains=term) | Q(last_name__icontains=term) |
                  Q(email=term) | Q(username__icontains=term)), is_active=True).order_by('first_name')
            for qs in query_result:
                ps = Profile.objects.get(user=qs)
                if Friend.objects.filter(from_user=request.user, to_user=qs.id).exists():
                    friend = Friend.objects.get(from_user=request.user, to_user=qs.id)
                    status = friend.status
                    if friend.status == '1':
                        title = "Friends"
                    elif friend.status == '3':
                        title = "Invite"
                    else:
                        title = "Invitation Sent"
                elif Friend.objects.filter(from_user=qs.id, to_user=request.user).exists():
                    friend = Friend.objects.get(to_user=request.user, from_user=qs.id)
                    status = friend.status
                    if friend.status == '1':
                        title = "Friends"
                    elif friend.status == '3':
                        title = "Invite"
                    else:
                        title = "Accept"
                else:
                    status = '3'
                    title = 'Invite'
                qs.name = qs.get_full_name()
                if ps.profile_img:
                    qs.l_img = get_thumbnail(ps.profile_img, '24x24', quality=99, format='PNG').url
                else:
                    qs.l_img = '/static/skigit/detube/images/noimage_user.jpg'
                search_list.append({'uid': qs.id, 'username': qs.username, 'name': qs.name, 'image': qs.l_img,
                                    'status': status, 'title': title})
                response_data['result'] = True
        response_data['search_list'] = sorted(map(dict, set(tuple(x.items()) for x in search_list)),
                                              key=lambda k: k['name'])
    return json_response(response_data)


@login_required(login_url='/')
def internalInviteRequest(request):
    """
        Internal Friends Invite Request registrations
    """
    response_data = {'result': False}
    if request.method == 'POST' and request.is_ajax():
        f_nt_message = ""
        f_nt_message += "Wanna new friend? "
        f_nt_message += request.user.username
        f_nt_message += " wants to be friends With you."
        user_obj = User.objects.get(id=request.POST.get('to_user', None), is_active=True)
        notify = Profile.objects.filter(user=request.user).values('plug_notify')
        if user_obj:
            if not Friend.objects.filter(from_user=request.user, to_user=user_obj).exists():
                friend = Friend()
                friend.from_user = request.user
                friend.to_user = user_obj
                friend.status = '0'
                friend.save()

                if notification_settings(user_obj.id, 'friends_request_notify') == True:
                    if not Notification.objects.filter(msg_type='friends', user=user_obj, from_user=request.user).exists():
                        Notification.objects.create(user=user_obj, from_user=request.user, msg_type='friends',
                                                    message=f_nt_message)
            elif Friend.objects.filter(from_user=request.user, to_user=user_obj).exists():
                Friend.objects.filter(from_user=request.user, to_user=user_obj).update(status='0')
                if notification_settings(user_obj.id, 'friends_request_notify') == True:
                    if not Notification.objects.filter(msg_type='friends', user=user_obj, from_user=request.user).exists():
                        Notification.objects.create(user=user_obj, from_user=request.user, msg_type='friends',
                                                    message=f_nt_message)
            response_data['result'] = True
    return json_response(response_data)


@login_required(login_url='/')
def approveFriendRequest(request):
    """

    :param request:
    :return:
    """
    response_data = {'result': False}

    if request.method == 'POST' and request.is_ajax():
        user_obj = User.objects.get(id=request.POST.get('to_user', None), is_active=True)
        f_nt_message = " "
        f_nt_message += "Sure, let's be friends! "
        f_nt_message += request.user.username
        f_nt_message += " has accepted your friendship."

        if Friend.objects.filter(from_user=user_obj, to_user=request.user, status=0).exists():
            Friend.objects.filter(from_user=user_obj, to_user=request.user).update(status='1')
            ps = Profile.objects.get(user=user_obj)
            name = user_obj.get_full_name()
            if ps.profile_img:
                l_img = get_thumbnail(ps.profile_img, '100x100', quality=99, format='PNG').url
            else:
                l_img = '/static/skigit/detube/images/noimage_user.jpg'
            follow_count = Follow.objects.exclude(follow=request.user.id).filter(follow=user_obj).count()
            response_data['result'] = True
            response_data['name'] = name
            response_data['image'] = l_img
            response_data['username'] = user_obj.username
            response_data['count'] = follow_count
            response_data['user_id'] = user_obj.id
            if notification_settings(user_obj.id,'friends_accept_notify') == True:
                if not Notification.objects.filter(msg_type='friends_accepted', user=user_obj,
                                                   from_user=request.user).exists():
                    Notification.objects.create(user=user_obj, from_user=request.user, msg_type='friends_accepted',
                                                message=f_nt_message)
    return json_response(response_data)


@login_required(login_url='/')
def rejectFriendRequest(request):
    """

    :param request:
    :return:
    """
    response_data = {'result': False}
    if request.method == 'POST' and request.is_ajax():
        user_obj = User.objects.get(id=request.POST.get('to_user', None), is_active=True)
        if Friend.objects.filter(from_user=user_obj, to_user=request.user).exists():
            Friend.objects.filter(from_user=user_obj, to_user=request.user).delete()
            response_data['result'] = True
            if Notification.objects.filter(msg_type='friends', from_user=user_obj, user=request.user).exists():
                Notification.objects.filter(from_user=user_obj, user=request.user,
                                            msg_type='friends').update(msg_type='un_friend')
                Notification.objects.filter(msg_type='un_friend').delete()
            if Notification.objects.filter(msg_type='friends_accepted', from_user=user_obj, user=request.user).exists():
                Notification.objects.filter(from_user=user_obj, user=request.user,
                                            msg_type='friends_accepted').update(msg_type='un_friend')
                Notification.objects.filter(msg_type='un_friend').delete()
        elif Friend.objects.filter(from_user=request.user, to_user=user_obj).exists():
            Friend.objects.filter(from_user=request.user, to_user=user_obj).delete()
            response_data['result'] = True
            if Notification.objects.filter(msg_type='friends', from_user=request.user, user=user_obj).exists():
                Notification.objects.filter(from_user=request.user, user=user_obj,
                                            msg_type='friends').update(msg_type='un_friend')
                Notification.objects.filter(msg_type='un_friend').delete()
            if Notification.objects.filter(msg_type='friends_accepted', from_user=request.user, user=user_obj).exists():
                Notification.objects.filter(from_user=request.user, user=user_obj,
                                            msg_type='friends_accepted').update(msg_type='un_friend')
                Notification.objects.filter(msg_type='un_friend').delete()
    return json_response(response_data)


@login_required(login_url='/')
def newFriendRequest(request):
    """

    :param request:
    :return:
    """
    response_data = {'result': False, 'messages': 'Invitation sent Fail. Please try again later'}
    if request.method == 'POST' and request.is_ajax():
        new_friend = request.POST.get('email', None)
        if not User.objects.filter(email=new_friend).exists():
            if not FriendInvitation.objects.filter(from_user=request.user, to_user_email=new_friend).exists():
                invite = FriendInvitation()
                invite.to_user_email = new_friend
                invite.from_user = request.user
                invite.save()
                response_data['result'] = True
                response_data['messages'] = "Invitation sent successfully."
            else:
                response_data['result'] = False
                response_data['messages'] = 'Invitation already sent.'
        else:
            response_data['result'] = False
            response_data['messages'] = 'Trying to invite user already registered with Skigit.'
    return json_response(response_data)


def friendNotifications(request):
    """

    :param request:
    :return:
    """
    friend_list = []
    response_data = {'result': False, 'messages': ' Error into Notification'}
    friend_request_notification = None
    if request.method == 'GET' and request.is_ajax():

        user = User.objects.get(pk=request.user.id, is_active=True)
        user_profile = Profile.objects.get(user=user)
        if Friend.objects.filter((Q(from_user=user) | Q(to_user=user)), is_read=False).exists():
            var1 = Friend.objects.filter(to_user=user, status=0, is_read=False).count()
            friend_request_notification = var1
            friends = Friend.objects.filter(to_user=user, status=0, is_read=False).order_by('-from_user__first_name')
            for friend in friends:
                us = User.objects.get(id=friend.from_user.id)
                ps = Profile.objects.get(user=us)
                name = us.get_full_name()
                if ps.profile_img:
                    l_img = get_thumbnail(ps.profile_img, '70x50', quality=99, format='PNG').url
                else:
                    l_img = None
                friend_list.append(
                    {'to_user': friend.from_user.id, 'name': name, 'profile_img': l_img, 'status': friend.status,
                     'username': us.username})
                friend_list = sorted(friend_list, key=lambda k: k['name'])
            response_data['friend_list'] = friend_list
            response_data['result'] = True
            response_data['messages'] = 'Received notification list'
        else:
            response_data['friend_list'] = friend_list
            response_data['result'] = False
            response_data['messages'] = 'There is no pending Notifications.'

    return json_response(response_data)

def friendNotificationsCount(request):
    """

    :param request:
    :return:
    """
    response_data = {'result': False, 'messages': ' Error into Notification count', 'count': 0}
    if request.method == 'GET' and request.is_ajax() and request.user.is_authenticated:
        user = User.objects.get(pk=request.user.id, is_active=True)
        if Friend.objects.filter((Q(from_user=user) | Q(to_user=user)), is_read=False).exists():
            friend_count = Friend.objects.filter(to_user=user, status=0, is_read=False).count()
            response_data['count'] = friend_count
            response_data['result'] = True
            response_data['messages'] = '%s Friend Invitation pending' % friend_count
        else:
            response_data['count'] = 0
            response_data['result'] = False
            response_data['messages'] = '0 Friend Invitation pending'
    return json_response(response_data)


@login_required(login_url='/')
def friendssharesearch(request):
    """
       Share Skigit to Friends by Searching Username.
    """
    search_list = []
    friends_list = []
    ski_share_list = []
    response_data = {'result': False, 'search_list': search_list}
    if request.method == 'POST' and request.is_ajax():
        search = request.POST.get('search_text', None)
        video_id = request.POST.get('video_id', None)
        time_zone = request.POST.get('time_zone', None)
        if not len(search) is 0:
            if Friend.objects.filter(Q(from_user=request.user.id) | Q(to_user=request.user.id), status='1'):
                friends_object = Friend.objects.filter(Q(from_user=request.user.id) | Q(to_user=request.user.id),
                                                       status='1')
                from_user_list = friends_object.exclude(from_user__id=request.user.id).values_list('from_user__id',
                                                                                                   flat=True).distinct()
                to_user_list = friends_object.exclude(to_user__id=request.user.id).values_list('to_user__id',
                                                                                               flat=True).distinct()
                friends_list = list(merge(from_user_list, to_user_list))

            for term in search.split():
                query_result = User.objects.exclude(id=request.user.id).filter(
                    Q(Q(first_name__icontains=term) | Q(last_name__icontains=term) |
                      Q(email=term) | Q(username__icontains=term)),
                    id__in=friends_list, is_active=True).order_by('first_name')

                for qs in query_result:
                    ps = Profile.objects.get(user=qs)
                    share_obj = Share.objects.filter(skigit_id__id=video_id, is_active=True,
                                                     to_user=qs, user=request.user).last()
                    if share_obj:
                        share_date = get_time_delta(share_obj.created_date, time_zone),
                    else:
                        share_date = ''
                    if ps.profile_img:
                        l_img = get_thumbnail(ps.profile_img, '24x24', quality=99, format='PNG').url
                    else:
                        l_img = '/static/skigit/detube/images/noimage_user.jpg'
                    search_list.append({'uid': qs.id,
                                        'username': qs.username,
                                        'name': qs.get_full_name(),
                                        'image': l_img,
                                        'share_date': share_date})
                response_data['result'] = True
                response_data['search_list'] = sorted(map(dict, set(tuple(x.items()) for x in search_list)),
                                                      key=lambda k: k['name'])
        else:
            friend_list = []
            if Friend.objects.filter(Q(to_user=request.user.id) | Q(from_user=request.user.id), status=1).exists():
                f_list = Friend.objects.filter(Q(to_user=request.user.id) | Q(from_user=request.user.id), status=1)
                from_user_list = f_list.exclude(from_user=request.user.id).values_list('from_user',
                                                                                       flat=True).distinct()
                to_user_list = f_list.exclude(to_user=request.user.id).values_list('to_user', flat=True).distinct()
                fr_list = list(merge(from_user_list, to_user_list))
                friends_detail = Profile.objects.filter(user__id__in=fr_list).order_by('user__username')
                for friends in friends_detail:
                    share_obj = Share.objects.filter(skigit_id__id=video_id,
                                                     is_active=True,
                                                     to_user=friends.user,
                                                     user=request.user).order_by('to_user', '-pk').distinct('to_user')
                    if share_obj:
                        for sh in share_obj:
                            share_date = get_time_delta(sh.created_date, time_zone),
                    else:
                        share_date = ''

                    if friends.profile_img:
                        l_img = get_thumbnail(friends.profile_img, '35x35', quality=99, format='PNG').url
                    else:
                        l_img = '/static/skigit/detube/images/noimage_user.jpg'
                    friend_list.append({'uid': friends.user.id, 'username': friends.user.username,
                                        'name': friends.user.get_full_name(), 'image': l_img,
                                        'share_date': share_date})
                response_data['result'] = True
                response_data['search_list'] = sorted(map(dict, set(tuple(x.items()) for x in friend_list)),
                                                      key=lambda k: k['name'])
    return json_response(response_data)


@login_required(login_url='/')
def share_skigit_date(request):
    """
        Share Skigit View
    """
    response_data = {'is_success': False, 'message': 'Error into ajax call of skigit record.'}
    if request.is_ajax() and request.method == 'POST':
        friend_list = []
        time_zone = request.POST.get('time_zone', None)
        video_id = request.POST.get('video_id', None)
        share_obj = Share.objects.exclude(
            to_user=request.user.id).filter(skigit_id__id=video_id, is_active=True, user=request.user.id
                                            ).order_by('to_user', '-pk').distinct('to_user')
        if share_obj:
            for sh in share_obj:
                share_date = get_time_delta(sh.created_date, time_zone)
                friend_list.append({'id': sh.to_user.id, 'video_id': int(video_id), 'username': sh.to_user.username,
                                    'name': sh.user.get_full_name(), 'share_date': share_date})
            response_data['is_success'] = True
            response_data['message'] = 'Share dates found.'
            response_data['share_data'] = friend_list
        else:
            response_data['is_success'] = False
            response_data['message'] = 'Share dates not found.'
    return json_response(response_data)


def get_all_logged_in_users():
    """
        Logged in users list view
    """
    uid_list = []
    user_list1 = []
    # Query all non-expired sessions
    # use timezone.now() instead of datetime.now() in latest versions of Django
    sessions = Session.objects.filter(expire_date__gte=timezone.now())
    # Build a list of user ids from that query
    for session in sessions:
        data = session.get_decoded()
        uid_list.append(data.get('_auth_user_id', None))
        uObj = User.objects.filter(id__in=uid_list)
        for u in uObj:
            user_list1.append(u.username.encode('utf8'))
    user_list1 = list(set(user_list1))
    return user_list1


def notifications_ajax(request):
    """
        Notification Skigit. <Snapdragon Notification>
    """
    response_data = {'is_success': False, 'message': 'Fail Error in to Notification Ajax Call'}
    if request.is_ajax() and request.method == 'POST':
        time_zone = request.POST.get('time_zone', '')
        notification_list = []
        plug_message = []
        parent_title = skigi_id = child_skigi_id = parent_skigi_id = child_title = None
        if Notification.objects.filter(user=request.user, is_read=False).exists():
            Notification.objects.filter(msg_type__icontains='_deleted').delete()
            start_date = datetime.now() - timedelta(days=30)
            end_date = datetime.now()
            Notification.objects.filter(user=request.user, is_read=False).update(is_view=True)
            notify_obj = Notification.objects.filter(user=request.user, created_date__range=(start_date, end_date),
                                                     is_read=False, is_active=True).order_by('-created_date')
            for notify in notify_obj:
                created_date = get_time_delta(notify.created_date, time_zone)
                if notify.skigit_id and Video.objects.filter(id=int(notify.skigit_id)).exists():
                    video = Video.objects.get(id=int(notify.skigit_id))
                    vid_title = video.title
                    ski_id = notify.skigit_id
                    if VideoDetail.objects.filter(skigit_id=int(notify.skigit_id)).exists():
                        video_detail = VideoDetail.objects.get(skigit_id=int(notify.skigit_id))
                        skigi_id = video_detail.id
                else:
                    vid_title = None
                    ski_id = None
                if notify.msg_type == 'plug_primary':
                    if not(str(notify.message).find("*@p*")) == -1:
                        plug_message = int((notify.message).split("*@p*")[-1])
                        plug_detail = Video.objects.filter(id=int(plug_message)).values_list('title', flat=True)
                        parent_title = plug_detail[0]
                        video_de = VideoDetail.objects.get(title=plug_detail[0])
                        parent_skigi_id = video_de.id
                    elif not(str(notify.message).find("*@c*")) == -1:
                        plug_message = int((notify.message).split("*@c*")[-1])
                        plug_detail = Video.objects.filter(id=int(plug_message)).values_list('title', flat=True)
                        child_title = plug_detail[0]
                        video_de = VideoDetail.objects.get(title=plug_detail[0])
                        child_skigi_id = video_de.id
                    else:
                        plug_message = None
                notification_list.append({'message': notify.message, 'user': notify.user.id, 'vid_title': vid_title,
                                          'username': notify.user.username, 'from_user': notify.from_user.id,
                                          'from_username': notify.from_user.username, 'is_read': notify.is_read,
                                          'msg_type': notify.msg_type, 'skigit_id': ski_id, 'date': created_date,
                                          'parent_title': parent_title, 'child_title': child_title,
                                          'parent_child_id': plug_message, 'child_skigi_id': child_skigi_id,
                                          'parent_skigi_id': parent_skigi_id, 'play_back_id': skigi_id})
            response_data['is_success'] = True
            response_data['message'] = 'Successfully get the notification list'
            response_data['notify_list'] = notification_list
        else:
            response_data['is_success'] = False
            response_data['message'] = 'No notifications to display!'
    return json_response(response_data)


def remove_notify_ajax(request):
    """
    Delete Notification Skigit. <Snapdragon Notification Remove>
    :param request:
    :return:
    """
    response_data = {'is_success': False, 'message': 'Fail Error in to Delete Notification Ajax Call'}
    if request.is_ajax() and request.method == 'POST':
        msg_type = request.POST.get('msg_type', '')
        to_user = request.POST.get('to_user', '')
        from_user = request.POST.get('from_user', '')
        skigit_id = request.POST.get('skigit_id', '')
        t_user = User.objects.get(pk=int(to_user))
        f_user = User.objects.get(pk=int(from_user))
        if not msg_type == 'friends' and not msg_type == 'friends_accepted':
            if Notification.objects.filter(user=t_user, skigit_id=int(skigit_id),
                                           from_user=f_user, msg_type=msg_type).exists():
                Notification.objects.filter(user=t_user, skigit_id=int(skigit_id),
                                            from_user=f_user, msg_type=msg_type).update(msg_type='deleted_msg')
                Notification.objects.filter(msg_type='deleted_msg').delete()
                response_data['is_success'] = True
                response_data['message'] = 'Notification Removed.'
            else:
                response_data['is_success'] = False
                response_data['message'] = 'Notification Failed to Removed.'
        else:
            if Notification.objects.filter(user=t_user, from_user=f_user, msg_type=msg_type).exists():
                Notification.objects.filter(user=t_user, from_user=f_user,
                                            msg_type=msg_type).update(msg_type='deleted_msg')
                Notification.objects.filter(msg_type='deleted_msg').delete()
                response_data['is_success'] = True
                response_data['message'] = 'Notification Removed.'
            else:
                response_data['is_success'] = False
                response_data['message'] = 'Notification Failed to Removed.'
    return json_response(response_data)


def internal_embed_ajax(request):
    """
    Internal Embed
    :param request: Ajax Request Call
    :return: Embed Success Message
    """
    response_data = {'is_success': False, 'message': 'Skigit failed to Embed in Profile Page. Please try again later'}
    if request.method == 'POST' and request.is_ajax():
        type = request.POST.get('type', '')
        vid_id = int(request.POST.get('skigit_id', ''))
        from_id = int(request.POST.get('from_id', ''))
        to_id = int(request.POST.get('to_id', ''))

        if Video.objects.filter(id=vid_id).exists():
            video = Video.objects.get(id=vid_id)
            to_user = User.objects.get(pk=to_id)
            from_user = User.objects.get(pk=from_id)

            if type == 'internal':
                if not Embed.objects.filter(from_user=from_user, to_user=to_user,
                                            skigit_id=video, embed_type='0').exists():
                    Embed.objects.create(from_user=from_user, to_user=to_user, skigit_id=video,
                                         embed_count=1)
                    response_data['is_success'] = True,
                    response_data['message'] = 'Skigit Embed Successful'
                else:
                    embed_id = Embed.objects.get(from_user=from_user, to_user=to_user, skigit_id=video, embed_type='0')
                    Embed.objects.filter(from_user=from_user, to_user=to_user, skigit_id=video,
                                         embed_type='0').update(is_embed=True, embed_count=int(embed_id.embed_count)+1)
                    response_data['is_success'] = True,
                    response_data['message'] = 'Skigit Embed Successful'
            else:
                response_data['is_success'] = False,
                response_data['message'] = 'Skigit failed to Embed in Profile Page.' \
                                           ' Video matching query does not exists'
    return json_response(response_data)


def remove_embed_ajax(request):
    """
    Un Embed Skigit
    :param request:
    :return:
    """
    response_data = {'is_success': False, 'message': 'Skigit failed to Embed in Profile Page. Please try again later'}
    if request.method == 'POST' and request.is_ajax():
        skigit_id = int(request.POST.get('skigit_id', None))
        video = VideoDetail.objects.get(id=skigit_id)
        Embed.objects.filter(to_user=request.user, skigit_id__id=video.skigit_id.id, embed_type='0').update(is_embed=False)
        response_data['is_success'] = False,
        response_data['message'] = 'successfully removed internal embed skigit'
    return json_response(response_data)


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


@login_required(login_url='/')
@xframe_options_exempt
@payment_required
@require_filled_profile
def wall_post_skigit24x36(request):
    """
        Skigit Wall Poster View for size 24x36
    """
    user = request.user
    poster = None
    if WallPoster.objects.exists():
        wall_post = WallPoster.objects.all()[0]
        skigit_logo = request.build_absolute_uri(wall_post.skigit_logo.url)
        header_image = request.build_absolute_uri(wall_post.header_image.url)
        poster_1 = request.build_absolute_uri(wall_post.poster_1.url)
        poster_2 = request.build_absolute_uri(wall_post.poster_2.url)
        if PosterBusinessLogo.objects.filter(user=request.user).exists():
            if PosterBusinessLogo.objects.filter(user=request.user, wall_post=wall_post).exists():
                poster = PosterBusinessLogo.objects.get(user=request.user, wall_post=wall_post)
            else:
                PosterBusinessLogo.objects.filter(user=request.user).update(wall_post=wall_post)
                poster = PosterBusinessLogo.objects.get(user=request.user, wall_post=wall_post)
        else:
            profile = Profile.objects.get(user=request.user)
            if profile.logo_img.exists():
                b_logo_url = profile.logo_img.filter(is_deleted=False)[0].logo
            PosterBusinessLogo.objects.create(user=request.user, wall_post=wall_post, b_logo=request.build_absolute_uri(b_logo_url.url))
            poster = PosterBusinessLogo.objects.filter(user=request.user, wall_post=wall_post)
        if PosterBusinessLogo.objects.filter(user=request.user, wall_post=wall_post).exists():
            poster_obj = PosterBusinessLogo.objects.get(user=request.user, wall_post=wall_post)
    return render(request, 'template/brochure24x36.html', locals())


@login_required(login_url='/')
@xframe_options_exempt
@payment_required
@require_filled_profile
def wall_post_skigit18x24(request):
    """
        Skigit Wall Poster View for size 18x24
    """
    user = request.user
    poster = None
    if WallPoster.objects.exists():
        wall_post = WallPoster.objects.all()[0]
        skigit_logo = request.build_absolute_uri(wall_post.skigit_logo.url)
        header_image = request.build_absolute_uri(wall_post.header_image.url)
        poster_1 = request.build_absolute_uri(wall_post.poster_1.url)
        poster_2 = request.build_absolute_uri(wall_post.poster_2.url)
        if PosterBusinessLogo.objects.filter(user=request.user).exists():
            if PosterBusinessLogo.objects.filter(user=request.user, wall_post=wall_post).exists():
                poster = PosterBusinessLogo.objects.get(user=request.user, wall_post=wall_post)
            else:
                PosterBusinessLogo.objects.filter(user=request.user).update(wall_post=wall_post)
                poster = PosterBusinessLogo.objects.get(user=request.user, wall_post=wall_post)
        else:
            profile = Profile.objects.get(user=request.user)
            if profile.logo_img.exists():
                b_logo_url = profile.logo_img.filter(is_deleted=False)[0].logo
            PosterBusinessLogo.objects.create(user=request.user, wall_post=wall_post, b_logo=request.build_absolute_uri(b_logo_url.url))
            poster = PosterBusinessLogo.objects.filter(user=request.user, wall_post=wall_post)
        if PosterBusinessLogo.objects.filter(user=request.user, wall_post=wall_post).exists():
            poster_obj = PosterBusinessLogo.objects.get(user=request.user, wall_post=wall_post)
    return render(request, 'template/brochure18x24.html', locals())


@login_required(login_url='/')
@payment_required
@require_filled_profile
def wall_poster_preview(request):
    """
        Wall Poster Preview
    """
    user = request.user
    poster = None
    wall_post_exists = False
    if WallPoster.objects.exists():
        wall_post_exists = True
        wall_post = WallPoster.objects.all()[0]
        skigit_logo = request.build_absolute_uri(wall_post.skigit_logo.url)
        header_image = request.build_absolute_uri(wall_post.header_image.url)
        poster_1 = request.build_absolute_uri(wall_post.poster_1.url)
        poster_2 = request.build_absolute_uri(wall_post.poster_2.url)
        if PosterBusinessLogo.objects.filter(user=request.user).exists():
            if PosterBusinessLogo.objects.filter(user=request.user, wall_post=wall_post).exists():
                poster = PosterBusinessLogo.objects.get(user=request.user, wall_post=wall_post)
            else:
                PosterBusinessLogo.objects.filter(user=request.user).update(wall_post=wall_post)
                poster = PosterBusinessLogo.objects.get(user=request.user, wall_post=wall_post)
        else:
            profile = Profile.objects.get(user=request.user)
            if profile.logo_img.exists():
                b_logo_url = profile.logo_img.filter(is_deleted=False)[0].logo
            PosterBusinessLogo.objects.create(user=request.user, wall_post=wall_post, b_logo=request.build_absolute_uri(b_logo_url.url))
            poster = PosterBusinessLogo.objects.filter(user=request.user, wall_post=wall_post)
        if PosterBusinessLogo.objects.filter(user=request.user, wall_post=wall_post).exists():
            poster_obj = PosterBusinessLogo.objects.get(user=request.user, wall_post=wall_post)
    return render(request, 'template/wallpreview.html', locals())


@login_required(login_url='/')
def get_b_logo(request):
    """
        Get business Logo for Wall poster and Brochures View
    """
    all_business_logo = []
    try:
        profile = Profile.objects.filter(user=request.user)
        for prof in profile:
            if prof.logo_img.filter(is_deleted=False).all():
                all_logo_obj = prof.logo_img.filter(is_deleted=False).all()
                for l_obj in all_logo_obj:
                    tmp = [l_obj.id, request.build_absolute_uri(l_obj.logo.url)]
                    all_business_logo.append(tmp)
                    del tmp
        data = {'all_business_logo': all_business_logo}
    except Exception as e:
        data = {'error': e.message, 'all_business_logo': all_business_logo}

    return HttpResponse(json.dumps(data), content_type="application/json")


@login_required(login_url='/')
def set_b_logo(request):
    response_data = {'is_success': False, 'message': 'Error into set new logo to wall post.. try later!'}
    if request.is_ajax() and request.method == 'POST':
        logo_url = request.POST.get('b_logo', None)
        if logo_url:
            PosterBusinessLogo.objects.filter(user=request.user).update(b_logo=logo_url)
            response_data['is_success'] = True
            response_data['message'] = 'New Logo set successfully'
        else:
            response_data['is_success'] = False
            response_data['message'] = 'New logo set failed. Image not Found'
    return json_response(response_data)


@login_required(login_url='/')
def set_brochure_logo(request):
    """
        Update business Logo for Wall poster and Brochures View
    """
    response_data = {'is_success': False, 'message': 'Error into set new logo to wall post.. try later!'}
    if request.is_ajax() and request.method == 'POST':
        logo_url = request.POST.get('b_logo', None)
        if logo_url:
            BrochureBLogo.objects.filter(user=request.user).update(b_logo=logo_url)
            response_data['is_success'] = True
            response_data['message'] = 'New Logo set successfully'
        else:
            response_data['is_success'] = False
            response_data['message'] = 'New logo set failed . Image not Found'
    return json_response(response_data)


@login_required(login_url='/')
@payment_required
@require_filled_profile
def brochure_preview(request):
    """
         Brochures Preview View
    """
    user = request.user
    brochure_exists = False
    if Brochure.objects.exists():
        brochure_exists = True
        brochure = Brochure.objects.all()[0]
        poster_1 = request.build_absolute_uri(brochure.poster_1.url)
        if BrochureBLogo.objects.filter(user=request.user).exists():
            if BrochureBLogo.objects.filter(user=request.user, brochure=brochure).exists():
                poster = BrochureBLogo.objects.get(user=request.user, brochure=brochure)
            else:
                BrochureBLogo.objects.filter(user=request.user).update(brochure=brochure)
                poster = BrochureBLogo.objects.get(user=request.user, brochure=brochure)
        else:
            profile = Profile.objects.get(user=request.user)
            if profile.logo_img.exists():
                b_logo_url = profile.logo_img.filter(is_deleted=False)[0].logo
                BrochureBLogo.objects.create(user=request.user, brochure=brochure, b_logo=request.build_absolute_uri(b_logo_url.url))
            poster = BrochureBLogo.objects.filter(user=request.user, brochure=brochure)
        if BrochureBLogo.objects.filter(user=request.user, brochure=brochure).exists():
            poster_obj = BrochureBLogo.objects.get(user=request.user, brochure=brochure)

    return render(request, 'template/viewbrochure.html', locals())


@login_required(login_url='/')
@payment_required
@require_filled_profile
@xframe_options_exempt
def brochure_print(request):
    """
        Brochures Print Template View
    """

    user = request.user
    brochure_exists = False
    if Brochure.objects.exists():
        brochure_exists = True
        brochure = Brochure.objects.all()[0]
        poster_1 = request.build_absolute_uri(brochure.poster_1.url)
        if BrochureBLogo.objects.filter(user=request.user).exists():
            if BrochureBLogo.objects.filter(user=request.user, brochure=brochure).exists():
                poster = BrochureBLogo.objects.get(user=request.user, brochure=brochure)
            else:
                BrochureBLogo.objects.filter(user=request.user).update(brochure=brochure)
                poster = BrochureBLogo.objects.get(user=request.user, brochure=brochure)
        else:
            profile = Profile.objects.get(user=request.user)
            if profile.logo_img.exists():
                b_logo_url = profile.logo_img.filter(is_deleted=False)[0].logo
                BrochureBLogo.objects.create(user=request.user, brochure=brochure,
                                             b_logo=request.build_absolute_uri(b_logo_url.url))
            poster = BrochureBLogo.objects.filter(user=request.user, brochure=brochure)
        if BrochureBLogo.objects.filter(user=request.user, brochure=brochure).exists():
            poster_obj = BrochureBLogo.objects.get(user=request.user, brochure=brochure)
    return render(request, 'template/brochureiframe.html', locals())
