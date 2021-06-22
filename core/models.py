from datetime import datetime

from django.contrib.auth.models import User
from django.db import models
from django.db.models import permalink
from django.utils import timezone


class BaseModel(models.Model):
    """ Base model with attributes for all other models
    """

    created_date = models.DateTimeField('created_date', default=timezone.now)
    updated_date = models.DateTimeField('updated_date', default=timezone.now)
    created_by = models.ForeignKey(
        User,
        models.SET_NULL,
        verbose_name='created by',
        null=True, blank=True, related_name='+'
    )
    updated_by = models.ForeignKey(
        User,
        models.SET_NULL,
        verbose_name='updated by',
        null=True, blank=True, related_name='+'
    )

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.updated_on = datetime.now()

        super(BaseModel, self).save(*args, **kwargs)


class Category(BaseModel):
    """ Comment: Category Model
    """
    cat_name = models.CharField(
        max_length=100,
        unique=True
    )
    cat_slug = models.SlugField(
        max_length=100,
        unique=True
    )
    is_active = models.BooleanField(
        default=True
    )

    def __str__(self):
        return self.cat_name

    @permalink
    def get_absolute_url(self):
        """ Returns: Full url path of Category Slug
        """
        return 'category_detail_view', None, {'cat_slug': self.cat_slug}

    class Meta:
        index_together = ('cat_name', 'cat_slug', 'is_active')
        verbose_name = "Category"
        verbose_name_plural = "Categories"


class SubjectCategory(BaseModel):
    """ Comment: Subject Category Model
    """

    sub_cat_name = models.CharField(
        max_length=150,
        unique=True
    )
    sub_cat_slug = models.SlugField(
        max_length=150,
        unique=True
    )
    is_active = models.BooleanField(
        default=True
    )

    def __str__(self):
        return self.sub_cat_name

    @permalink
    def get_absolute_url(self):
        """
            Returns: Full url of Sub Category Slug
        """
        return 'awesome_things_category', None, {'sub_cat_slug': self.sub_cat_slug}

    class Meta:
        index_together = ('sub_cat_name', 'sub_cat_slug', 'is_active')
        verbose_name = "Subject Category"
        verbose_name_plural = "Subject Categories"


class GeneralSiteData(models.Model):
    bug_category_url = models.TextField(blank=True, null=True)

    def __str__(self):
        return '{}'.format(self.id)

    class Meta:
        verbose_name = "General Site Data"
        verbose_name_plural = "General Site Data"