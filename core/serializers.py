from rest_framework import serializers
from django.conf import settings

from core.models import Category, SubjectCategory

class CategorySerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ('id', 'cat_name', 'cat_slug', 'image')

    def get_image(self, obj):
        category_image_dict = {'dramaskigit': '{0}images/animation/50/PNG/Drama-Wacki_4x4.png'.format(settings.STATIC_URL),
                               'vibraskigit': '{0}images/animation/50/PNG/Vibraskigit_4x4.png'.format(settings.STATIC_URL),
                               'demoskigit': '{0}images/animation/50/PNG/Demo_4x4.png'.format(settings.STATIC_URL),
                               'wackiskigit': '{0}images/animation/50/PNG/Wacki_4x4.png'.format(settings.STATIC_URL),
                               'selfieskigit': '{0}images/animation/50/PNG/Selfie_4x4.png'.format(settings.STATIC_URL)}
        image_value = category_image_dict[obj.cat_slug] if obj.cat_slug in category_image_dict else ''
        return image_value

class SubjectCategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = SubjectCategory
        fields = ('id', 'sub_cat_name', 'sub_cat_slug')


class UrlSerializer(serializers.Serializer):
    """
    Get all urls throughout the project especially in Bug report management!
    """

    name = serializers.CharField(allow_blank=True)
    url = serializers.CharField(allow_blank=True)

    class Meta:
        fields = ('name', 'url')
