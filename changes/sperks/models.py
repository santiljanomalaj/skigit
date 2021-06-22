from django.db import models
from django.utils.translation import ugettext as _

from core.models import BaseModel


class Donation(BaseModel):
    """ Comment: Donation Model
    """

    ngo_name = models.CharField(
        _('Organization Name'),
        max_length=200
    )
    url = models.URLField(
        'URL'
    )
    ngo_description = models.TextField(
        _('About'),
        blank=True,
        null=True
    )

    def __str__(self):
        return self.ngo_name

    class Meta(object):
        verbose_name = _('Donation')
        verbose_name_plural = _('Donation')


class Incentive(BaseModel):
    """ Comment: Incentive Model
    """
    title = models.CharField(
        max_length=200,
        blank=False,
        verbose_name=_("Incentive Title")
    )
    is_active = models.BooleanField(
        default=True
    )

    def __str__(self):
        return self.title
