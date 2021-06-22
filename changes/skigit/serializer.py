
from django.core.exceptions import FieldError
from rest_framework import serializers
from skigit.models import VideoDetail, Profile, Like
from social.models import Share


class VideoDetailSerializer(serializers.ModelSerializer):

    category = serializers.SerializerMethodField()
    business_logo_url = serializers.SerializerMethodField()
    thumbnail = serializers.SerializerMethodField()
    username = serializers.SerializerMethodField()
    profile_imgs = serializers.SerializerMethodField()
    video_playback_id = serializers.SerializerMethodField()
    video_like = serializers.SerializerMethodField()
    video_plug = serializers.SerializerMethodField()
    video_share = serializers.SerializerMethodField()

    class Meta:
        model = VideoDetail
        fields = ('pk', 'id', 'title', 'category', 'made_by', 'business_logo',
                  'business_logo_url', 'thumbnail', 'username', 'bought_at_url',
                  'profile_imgs', 'skigit_id', 'video_playback_id', 'video_like',
                  'video_plug', 'video_share', 'view_count', 'created_date', 'updated_date')

    def get_business_logo_url(self, obj):
        if obj.made_by:
            if obj.business_logo:
                if obj.business_logo.is_deleted is False:
                    return obj.business_logo.logo.url
                else:
                    us_profile = Profile.objects.get(user=obj.made_by)
                    if us_profile.logo_img.filter(is_deleted=False).all().count() > 0:
                        return us_profile.logo_img.filter(is_deleted=False).all()[0].logo.url
            else:
                return ''
        return ''

    def get_thumbnail(self, obj):
        if obj:
            return obj.skigit_id.thumbnails.all()[0].url
        return ''

    def get_username(self, obj):
        if obj.skigit_id:
            return obj.skigit_id.user.username
        return ''

    def get_profile_imgs(self, obj):
        if obj:
            try:
                profile = Profile.objects.filter(
                    user_id=obj.skigit_id.user
                ).select_related('profile_img').first()
            except FieldError:
                profile = Profile.objects.filter(
                    user_id=obj.skigit_id.user
                ).select_related('cover_img').first()
            if profile.profile_img:
                return profile.profile_img.url
            elif profile.cover_img:
                return profile.cover_img.url
            return ''
        return ''

    def get_category(self, obj):
        if obj.category:
            return obj.category.cat_name
        return ''

    def get_video_playback_id(self, obj):
        if obj.skigit_id:
            return obj.skigit_id.video_id
        return ''

    def get_video_like(self, obj):
        if obj:
            return Like.objects.filter(skigit=obj.skigit_id, status=True).count()
        return '0'

    def get_video_plug(self, obj):
        if obj:
            return VideoDetail.objects.filter(plugged_skigit=obj.skigit_id,
                                              is_plugged=True, status=1).count()
        return '0'

    def get_video_share(self, obj):
        if obj:
            return Share.objects.filter(skigit_id=obj, is_active=True).count()
        return '0'
