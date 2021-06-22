"""skigit_project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""

from user.views import (LoginView, LoginViewAPI, LogoutUser, RegisterConfirm, RegisterType, Reset, ResetConfirm,
                        UserProfile, UserProfileDisplay)

import notifications.urls
from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth.views import password_change, password_change_done
from django.views.generic.base import TemplateView
from django.views.static import serve as view_static_server

from core.utils import notify_admins
from core.views import index, SkigitBaseView
from invoices.views import *
# from skigit.views import (AwesomeThings, AwesomeThingsCategory, CategoryDetail, DirectUpload, GetSperk, SkigitData,
#                           user_profile_notifications, user_profile_delete, my_statistics, sperk_profile,
#                           ajax_skigit_plugin_link, ajax_skigit_plugin_video, skigit_count_update, get_user_notification)
from skigit.views import *
from sperks.views import Sperks

admin.autodiscover()

about_us_patterns = [
    url(r'^$', SkigitBaseView.as_view(template_name='static/about_us.html'),
        name='aboust_us_view'),
    url(r'^faq/$', SkigitBaseView.as_view(template_name='static/faq.html'),
        name='faq_view'),
    url(r'^privacy-policy/$', SkigitBaseView.as_view(template_name='static/privacy_policy.html'),
        name='privacy_policy_view'),
    url(r'^terms-of-service/$', SkigitBaseView.as_view(template_name='static/t_and_c.html'),
        name='t_and_c_view'),
    url(r'^acceptable-use-policy/$', SkigitBaseView.as_view(template_name='static/acceptable_use_policy.html'),
        name='acceptable_use_policy_view'),
    url(r'^copyright-policy/$', SkigitBaseView.as_view(template_name='static/copyright_policy.html'),
        name='copyright_policy'),
    url(r'^skigit-for-business/$', SkigitBaseView.as_view(template_name='static/skigit_for_business.html'),
        name='skigit_for_business_view'),
    url(r'^business-terms-of-service/$', SkigitBaseView.as_view(template_name='static/business_terms_of_service.html'),
        name='business_terms_service'),
    url(r'^rules-for-your-company-skigit/$',
        SkigitBaseView.as_view(template_name='static/rules_for_your_company_skigit.html'),
        name='rules_company_skigit'),
]

guidelines_patterns = [
    url(r'^$', SkigitBaseView.as_view(template_name='static/guidelines.html'),
        name='guidelines_view'),
    url(r'^skigitology/$', SkigitBaseView.as_view(template_name='static/skigitology.html'),
        name='skigitology_view'),
    url(r'^skigit-length/$', SkigitBaseView.as_view(template_name='static/skigit_length.html'),
        name='skigit_length_view'),
    url(r'^making-your-skigit/$', SkigitBaseView.as_view(template_name='static/making_your_skigit_view.html'),
        name='making_your_skigit_view'),
    url(r'^allowed-video_formats/$', SkigitBaseView.as_view(template_name='static/allowed_video_formats_view.html'),
        name='allowed_video_formats_view'),
]

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    # url(r'^$', Home.as_view(), name='index'),
    url(r'^$', index, name='index'),
    url(r'^friends/', include('friends.urls')),
    url(r'^invoice/', include('invoices.urls')),
    url(r'^api/v1/auth/login/$', LoginViewAPI.as_view(), name='login'),
    url(r'^login_ajax/$', LoginView.as_view(), name='login_ajax'),
    url(r'^register/$', RegisterType.as_view(), name='register_type'),
    url(r'^register/confirm/(?P<activation_key>\w+)/', RegisterConfirm.as_view(), name='register_confirm'),
    url(r'^reset/confirm/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        ResetConfirm.as_view(), name='password_reset_confirm'),
    url(r'^reset/done/$', SkigitBaseView.as_view(template_name='registration/password_reset_complete.html'),
        name='reset_done'),
    url(r'^reset/success/$', SkigitBaseView.as_view(template_name='registration/password_resets_done.html'),
        name='reset_success'),
    url(r'^reset/$', Reset.as_view(), name='reset'),
    url(r'^logout/done/$', LogoutUser.as_view(), name='logout_user'),
    url(r'^logout/$', LogoutUser.as_view(), name='logout_page'),

    url(r'about-us/', include(about_us_patterns, namespace="about_us_url")),
    url(r'guidelines/', include(guidelines_patterns, namespace="guidelines_url"), name="guidelines"),


    url(r'^category/(?P<cat_slug>[a-z]+)', CategoryDetail.as_view(), name='category_detail_view'),
    url(r'^awesomethings/$', AwesomeThings.as_view(), name='awesome_things'),
    url(r'^awesomethings/(?P<sub_cat_slug>[\w.@+-]+).html', AwesomeThingsCategory.as_view(),
        name='awesome_things_category'),

    url(r'^skigit_data/(?P<pk>\d+)/$', SkigitData.as_view(), name='skigit_data'),

    url(r'^sperk/$', Sperks.as_view(), name='sperks'),

    url(r'^sperk/(?P<user>\d+)/(?P<logo>\d+)/$', sperk_profile, name='sperk_profile'),

    url(r'^get-sperk/$', GetSperk.as_view(), name='get_sperk'),

    url(r'^profile/$', UserProfile.as_view(), name='user_profile'),

    # Plugin skigit
    url(r'^plugin/(?P<plug_id>[\w.@+-]+)/$', ajax_skigit_plugin_link, name='skigit_plugin'),
    url(r'^plugin-vid/(?P<plug_id>[\w.@+-]+)/$', ajax_skigit_plugin_video, name='skigit_plugin_video'),


    url(r'^view_count_update/$', skigit_count_update, name='view_count_update'),

    url(r'^youtube/direct-upload/?$', DirectUpload.as_view(), name="youtube_direct_upload"),
    # url(r'^youtube/link-upload/?$', LinkUpload.as_view(), name="youtube_link_upload"),
    # url(r'^youtube/remove-profile-pic/?$', RemoveImages.as_view(), name="remove_profile_pic"),

    url(r'^profile/password_change/$', password_change, {
        'post_change_redirect': '/profile/password_change/done/'
    }, name="password_change"),
    url(r'^profile/password_change/done/$', notify_admins(password_change_done)),
    url(r'^profile/notifications/$', user_profile_notifications, name='user_profile_notifications'),
    url(r'^profile/delete/$', user_profile_delete, name='user_profile_delete'),
    url(r'^profile/my_statistics/$', my_statistics, name='my_statistics'),
    url(r'^profile/invoice/$', invoice_payment, name='user_payment_setup'),

    # user profile
    url(r'^profile/(?P<username>[\w.@+-]+)/$', UserProfileDisplay.as_view(), name='user_profile_display'),


    url(r'^get_notification_count/$', get_user_notification, name='get_notification_count'),

    url(r'^my_skigits/$', my_skigits, name='my_skigits'),
    url(r'^my_skigits/(?P<user_id>[\w.@+-]+)/$', my_skigits_view, name='my_skigits_view'),
    url(r'^plugged_in_skigits/$', plugged_in_skigits, name='plugged_in_skigits'),
    url(r'^like/$', liked_skigits, name='liked_skigits'),
    url(r'^favorite/$', favorite_skigits, name='favorite_skigits'),
    url(r'^following/$', i_am_following_view, name='i_am_following'),
    # follow skigit on popup page
    url(r'^follow/$', i_am_following, name='i_am_following'),
    url(r'^unfollow/$', un_following, name='i_am_following'),
    url(r'^skigit_statistics/$', skigit_statistics, name='statistics'),
    # skigit Like/Unlike
    url(r'^view_count_update/$', skigit_count_update, name='view_count_update'),
    url(r'^skigit_i_like/$', skigit_i_like, name='skigit_like'),
    url(r'^skigit_i_unlike/$', skigit_i_unlike, name='skigit_unlike'),
    # favourite/un-favourite Skigit
    url(r'^my_favourites/$', my_favourite_skigit, name='my_favourite_skigit'),
    url(r'^un_favourites/$', un_favourite_skigit, name='un_favourite_skigit'),
    # Skigit View count
    url(r'^skigit_view_count/$', skigit_view_count, name='skigit_view_count'),
    url(r'^search_skigit/$', skigit_search_view, name='skigit_search'),
    url(r'^search_skigit/(?P<order>[\w.@&+-]+)$', search_ordering_skigit,
        name='skigit_search_ordering'),
    # Inappropriate skigit
    url(r'^skigit_inapp_reason/$', skigit_inapp_reason, name='skigit_inapp_reason'),
    # social share redirect url
    url(r'^social_redirect/(?P<video_id>[\w.@+-]+)/$', social_redirect, name="social_redirect"),
    url(r'^share-skigits/$', share_to_friends, name="share_skigit_to_friends"),
    url(r'^email-share-skigit/$', email_share_friends, name="share_skigit_friends"),
    # To display logo in skgit popup_page form
    url(r'^display_business_logo/$', display_business_logo, name='display_business_logo'),
    # Plugin skigit
    url(r'^plugin/(?P<plug_id>[\w.@+-]+)/$', ajax_skigit_plugin_link, name='skigit_plugin'),
    url(r'^plugin-vid/(?P<plug_id>[\w.@+-]+)/$', ajax_skigit_plugin_video,
        name='skigit_plugin_video'),
    url(r'^copyright-infringement/(?P<ski_id>\d+)/$', copyright, name='copyright_infringement'),
    # Get Embed Skigit


] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT, show_indexes=True)
