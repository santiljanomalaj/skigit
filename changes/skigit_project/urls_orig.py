from django.conf.urls import include
from django.conf.urls import url
from django.conf.urls.static import static
from django.contrib import admin
from django.views.generic.base import TemplateView
from django.views.static import serve as view_static_server

from friends.views import wall_poster_preview, brochure_preview

from skigit.views import *
from skigit.socialauth import *
from skigit.utils import notify_admins
from django.contrib.auth.views import password_change, password_change_done
from admin_tools.dashboard.views import skigit_invoice, \
    skigit_invoice_detailview

admin.autodiscover()

about_us_patterns = [
    url(r'^$', aboust_us_view, name='aboust_us_view'),
    url(r'^faq/$', faq_view, name='faq_view'),
    url(r'^privacy_policy/$', privacy_policy_view, name='privacy_policy_view'),
    url(r'^terms_of_service/$', t_and_c_view, name='t_and_c_view'),
    url(r'^acceptable-use-policy/$', acceptable_use_policy_view, name='acceptable_use_policy_view'),
    url(r'^copyright_policy/$', copyright_policy_view, name='copyright_policy'),
    url(r'^skigit_for_business/$', skigit_for_business_view, name='skigit_for_business_view'),
    url(r'^business_terms_of_service/$', business_terms_of_service, name='business_terms_service'),
    url(r'^rules-for-your-company-skigit/$', rules_for_your_company_skigit, name='rules_company_skigit'),
]

guidelines_patterns = [
    url(r'^$', guidelines_view, name='guidelines_view'),
    url(r'^skigitology/$', skigitology_view, name='skigitology_view'),
    url(r'^skigit_length/$', skigit_length_view, name='skigit_length_view'),
    url(r'^making_your_skigit/$', making_your_skigit_view, name='making_your_skigit_view'),
    url(r'^allowed_video_formats/$', allowed_video_formats_view, name='allowed_video_formats_view'),
]

urlpatterns = [
    url(r'^loginpopup$', index, name='index'),
    url(r'^$', index, name='index'),
    url(r'^friends/', include('friends.urls')),
    url(r'^invoice/', include('invoices.urls')),
    url(r'^$', social_auth_login, name='social_user_profile'),
    url('', include('social.apps.django_app.urls', namespace='social')),
    url('', include('django.contrib.auth.urls', namespace='auth')),
    url(r'about_us/', include(about_us_patterns, namespace="about_us_url")),
    # url(r'^find-friends/', include('social_friends_finder.urls')),
    url(r'guidelines/', include(guidelines_patterns, namespace="guidelines_url")),
    url(r'^investors/$', investors_view, name='investors_view'),
    url(r'^register/$', register_type, name='register_type'),
    url(r'^social-login/(?P<social_type>\w+)/', social_login_type, name='social_login'),
    url(r'^register/confirm/(?P<activation_key>\w+)/', register_confirm, name='register_confirm'),
    url(r'^reset/confirm/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        reset_confirm, name='password_reset_confirm'),
    url(r'^reset/done/$', reset_done, name='reset_done'),
    url(r'^reset/success/$', reset_success, name='reset_success'),
    url(r'^reset/$', reset, name='reset'),
    url(r'^email_exits_check/$', email_exits_check, name='email_exits_check'),
    url(r'^_login/$', login_require, name='login_require'),
    url(r'^login_ajax/$', login_ajax, name='login_ajax'),
    url(r'^accounts/login/$', index,),
    url(r'^profile/$', view_user_profile, name='user_profile'),
    url(r'^profile_upload-target/$', profile_extra_image, name='profile_extra_image'),
    url(r'^business_logo_upload_target/$', business_logo, name='business_logo'),
    url(r'^profile_get_target/$', profile_get_target, name='profile_get_target'),
    url(r'^business_logo_get_target/$', business_logo_get_target, name='business_logo_get_target'),
    url(r'^delete_business_logo/$', delete_business_logo, name='delete_business_logo'),
    url(r'^delete_extra_profile_image/$', delete_extra_profile_image,
        name='delete_extra_profile_image'),
    url(r'^profile_pic/$', profile_pic, name='profile_pic'),
    url(r'^coupan_image_upload/$', coupan_image_upload, name='coupan_image_upload'),
    url(r'^profile/password_change/$', password_change, {
        'post_change_redirect': '/profile/password_change/done/'
    }, name="password_change"),
    url(r'^profile/password_change/done/$', notify_admins(password_change_done)),
    url(r'^profile/notifications/$', user_profile_notifications, name='user_profile_notifications'),
    url(r'^profile/deleteskigit/$', delete_skigit, name='delete_skigit'),
    url(r'^unplug-skigit/$', unplug_skigit, name='unplug_skigit'),
    url(r'^profile/deletelikedskigit/$', delete_liked_skigit, name='delete_liked_skigit'),
    url(r'^profile/deletefavskigit/$', delete_favorite_skigit, name='delete_favorite_skigit'),
    url(r'^profile/invoice/$', invoice_payment, name='user_payment_setup'),
    url(r'^profile/my_statistics/$', my_statistics, name='my_statistics'),
    url(r'^skigistats/$', all_statistic_count, name='my_skigistats'),
    url(r'^profile/delete/$', user_profile_delete, name='user_profile_delete'),
    url(r'^profile/(?P<username>[\w.@+-]+)/$', user_profile_display, name='user_profile_display'),
    url(r'^sperk/(?P<user>\d+)/(?P<logo>\d+)/$', sperk_profile, name='sperk_profile'),
    url(r'^logout/done/$', logout_user, name='logout_user'),
    url(r'^logout/$', logout_user, name='logout_page'),
    url(r'^admin_tools/', include('admin_tools.urls')),
    url(r'^admin/skigit-invoices/$', skigit_invoice, name='skigit_admin_invoice'),
    url(r'^admin/skigit-invoices/(?P<user_name>[\w.@+-]+)/$', skigit_invoice_detailview, name='user_invoice_view'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^skigit/', include('skigit.urls', namespace="skigit")),
    # for django-youtube
    url(r'^youtube/', include('skigit.urls', namespace='youtube')),
    # all auth
    url(r'^accounts/', include('allauth.urls')),
    url(r'^ytdemo/$', TemplateView.as_view(template_name='youtube/yt_index.html')),
    url(r'^accounts/profile/$', TemplateView.as_view(template_name='youtube/yt_profile.html')),
    url(r'^inappropriateskigit_status_save/$', inappropriateskigit_status_save,
        name='inappropriateskigit_status_save'),
    url(r'^vdo_thumbnail/get/$', get_youtube_video_thumbnail,
        name='get_youtube_video_thumbnail'),
    # Category View
    url(r'^category/(?P<cat_slug>[a-z]+)/sort-by-date/(?P<order_by>\d+)/$', sort_by_date,
        name='date_sort_view'),
    url(r'^category/(?P<cat_slug>[a-z]+)/sort-by-title/(?P<order_by>\d+)/$', sort_by_title,
        name='title_sort_view'),
    url(r'^category/(?P<cat_slug>[a-z]+)/sort-by-views/(?P<order_by>\d+)/$', sort_by_views,
        name='views_sort_view'),
    url(r'^category/(?P<cat_slug>[a-z]+)/sort-by-Likes/(?P<order_by>\d+)/$', sort_by_likes,
        name='like_sort_view'),
    url(r'^category/(?P<cat_slug>[a-z]+)/sort-by-random/$', sort_by_random,
        name='random_sort_view'),
    url(r'^category/$', category_view, name='category_view'),
    url(r'^category/(?P<cat_slug>[a-z]+)', category_detail_view, name='category_detail_view'),
    url(r'^awesomethings/$', awesome_things, name='awesome_things'),
    url(r'^awesomethings/(?P<sub_cat_slug>[\w.@+-]+).html', awesome_things_category,
        name='awesome_things_category'),
    # Inside Dropdown of logout
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
    url(r'^skigit_data/(?P<pk>\d+)/$', skigit_data, name='skigit_data'),
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
    # Get Embed Skigit
    url(r'^skigit-embed/(?P<video>[\w.@+-]+)/$', embed_skigit, name='embed_skigit'),
    url(r'^(?P<pk>\d+)/$', linked_in_share, name='linked_in_media_share'),
    url(r'^wall-poster-preview/$', wall_poster_preview, name='wall_poster_preview'),
    url(r'^brochure-preview/$', brochure_preview, name='brochure_preview'),
    # To get username in message popup box
    url(r'^get_username/$', get_username, name='get_username'),
    url(r'^sperk/$', sperks, name='sperks'),
    url(r'^bug-management/$', bug_management, name='bug_management'),
    url(r'^get-sperk/$', get_sperk, name='get_sperk'),
    url(r'^copyright-infringement/(?P<ski_id>\d+)/$', copyright, name='copyright_infringement'),
    url(r'^get_notification_count/$', get_user_notification, name='get_notification_count'),
    url(r'^tinymce/', include('tinymce.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT, show_indexes=True)

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [url(r'^__debug__/', include(debug_toolbar.urls)),]

    # urlpatterns += static(settings.STATIC_URL,
    #                       document_root=settings.STATIC_ROOT)
    #
    # urlpatterns += [
    #     url(r'^media/(?P<path>.*)$', view_static_server, {
    #         'document_root': settings.MEDIA_ROOT,
    #     }),
    # ]

