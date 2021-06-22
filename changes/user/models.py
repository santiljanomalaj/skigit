from datetime import datetime, timedelta

from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
from django.core.cache import cache
from django.utils import timezone

from core.models import BaseModel

from django_countries.fields import CountryField


class BusinessLogo(BaseModel):
    """ Comment: Business Logo Model
    """
    logo = models.ImageField(
        upload_to="skigit/logo/%y/%m/%d",
        blank=True,
        null=True
    )
    is_deleted = models.BooleanField(
        default=False,
        blank=False
    )


class ProfileImg(BaseModel):
    profile_img = models.ImageField(upload_to="skigit/profile/%y/%m/%d",
                                    blank=True, null=True)
    is_active = models.BooleanField(default=True)


class ExtraProfileImage(BaseModel):
    profile_img = models.ImageField(upload_to="skigit/profile/%y/%m/%d",
                                    blank=True, null=True)
    is_active = models.BooleanField(default=True)


class ProfileUrl(models.Model):
    disc1 = models.CharField(max_length=30, blank=True, null=True)
    url1 = models.URLField(blank=True, null=True)
    disc2 = models.CharField(max_length=30, blank=True, null=True)
    url2 = models.URLField(blank=True, null=True)
    disc3 = models.CharField(max_length=30, blank=True, null=True)
    url3 = models.URLField(blank=True, null=True)
    disc4 = models.CharField(max_length=30, blank=True, null=True)
    url4 = models.URLField(blank=True, null=True)
    disc5 = models.CharField(max_length=30, blank=True, null=True)
    url5 = models.URLField(blank=True, null=True)
    user = models.ForeignKey(User, related_name="User")


class Profile(BaseModel):
    GENDER_MALE = 0
    GENDER_FEMALE = 1

    INCENTIVE_NO = 0
    INCENTIVE_YES = 1

    PAYMENT_CHOICES = (
        ('0', 'PayPal'),
        ('1', 'Credit/Debit Card'),
    )

    GENDER_CHOICES = [(GENDER_MALE, 'Male'), (GENDER_FEMALE, 'Female')]
    INCENTIVE_CHOICES = [(INCENTIVE_NO, 'No'), (INCENTIVE_YES, 'Yes')]
    LANGUAGE_CHOICES = [('', 'Select Language'), ("ENG", "English"),
                        ("SPN", "Spanish"), ("FR", "French"),
                        ("CH", "Chinese"), ("ARB", "Arabic"), ("HND", "Hindi"),
                        ("RSN", "Russian"),
                        ("PRT", "Portuguese"), ("JPN", "Japanese"),
                        ("GRM", "German"), ("TUR", "Turkish"),
                        ("VTM", "Vietnamese"), ("THI", "Thai"),
                        ("DCH", "Dutch")]

    BUSINESS_TYPE_CHOICES = [('', 'Select Business Type'), ('MD', 'Media'),
                             ('PRF', 'Professional')]

    NOTIFICATION_NO = 0
    NOTIFICATION_YES = 1
    NOTIFICATION_CHOICES = [(NOTIFICATION_NO, 'No'), (NOTIFICATION_YES, 'Yes')]

    PROFILE_SECURITY_SEARCH_YES = 1
    PROFILE_SECURITY_SEARCH_NO = 0

    SECURITY_SEARCH_CHOICES = [(PROFILE_SECURITY_SEARCH_NO, 'No'),
                               (PROFILE_SECURITY_SEARCH_YES, 'Yes')]

    user = models.OneToOneField(User)
    phone_num = models.CharField(max_length=10, blank=True)
    gender = models.IntegerField(choices=GENDER_CHOICES, verbose_name="Gender",
                                 blank=True, null=True)
    profile_img = models.ImageField(upload_to="skigit/profile/",
                                    verbose_name="Add a personal photo",
                                    blank=True, null=True)
    extra_profile_img = models.ManyToManyField(ExtraProfileImage, blank=True)
    logo_img = models.ManyToManyField(BusinessLogo, blank=True)
    incentive = models.IntegerField(choices=INCENTIVE_CHOICES,
                                    verbose_name="Incentive", blank=True,
                                    null=True)
    skigit_incentive = models.TextField(verbose_name="Skigit Incentive",
                                        blank=True, null=True)
    incetive_val = models.IntegerField('Incentive value($USD)', blank=True,
                                       null=True)
    redemoption_instrucations = models.TextField(
        verbose_name="Redemoption Instrucations", blank=True, null=True)
    coupan_code = models.CharField(max_length=100, verbose_name="Coupan Code",
                                   blank=True, null=True)
    coupan_image = models.ImageField(upload_to="skigit/coupan/",
                                     verbose_name="Add coupan image",
                                     blank=True, null=True)
    contact_name = models.CharField(max_length=100, verbose_name="Contact Name",
                                    blank=True, null=True)
    contact_email = models.EmailField(verbose_name="Contact Email", blank=True,
                                      null=True)
    contact_phone = models.CharField(max_length=12,
                                     verbose_name="Contact Phone", blank=True,
                                     null=True)
    biller_name = models.CharField(max_length=100, verbose_name="Biller Name",
                                   blank=True, null=True)
    biller_address1 = models.CharField(max_length=100,
                                       verbose_name="Biller Address1",
                                       blank=True, null=True)
    biller_address2 = models.CharField(max_length=100,
                                       verbose_name="Biller Address2",
                                       blank=True, null=True)
    payment_method = models.CharField('Payment Type', max_length=1,
                                      choices=PAYMENT_CHOICES, default='0')
    payment_email = models.EmailField(verbose_name="Contact Email for payment",
                                      blank=True, null=True)
    payment_user_name = models.CharField(max_length=35,
                                         verbose_name="Name for payment setup",
                                         blank=True, null=True)
    cover_img = models.OneToOneField(ProfileImg, blank=True, null=True)
    about_me = models.TextField(verbose_name="About Me", blank=True, null=True)
    birthdate = models.DateField(verbose_name="Date of Birth", blank=True,
                                 null=True)
    language = models.CharField(choices=LANGUAGE_CHOICES, max_length=200,
                                verbose_name="Language", blank=True, null=True)
    country = CountryField(blank_label='Select country', blank=True, null=True)
    state = models.CharField(max_length=30, verbose_name="State", blank=True,
                             null=True)
    city = models.CharField(max_length=30, verbose_name="City", blank=True,
                            null=True)
    zip_code = models.BigIntegerField(verbose_name="Zip Code", blank=True,
                                      null=True)
    # Notification Settings
    like_notify = models.BooleanField('Like Notification', default=True,
                                      blank=False, null=False)
    follow_un_follow_notify = models.BooleanField(
        'Follow/ Un follow Notification', default=True, blank=False, null=False)
    friends_request_notify = models.BooleanField('Friend Request Notification',
                                                 default=True, blank=False,
                                                 null=False)
    friends_accept_notify = models.BooleanField('Friend Accept Notification',
                                                default=True, blank=False,
                                                null=False)
    plug_notify = models.BooleanField('Plug Notification', default=True,
                                      blank=False, null=False)
    un_plug_notify = models.BooleanField('Un Plug Notification', default=True,
                                         blank=False, null=False)
    skigit_notify = models.BooleanField('Skigit Upload Notification',
                                        default=True, blank=False, null=False)
    share_notify = models.BooleanField('Share Skigit Notification',
                                       default=True, blank=False, null=False)
    activation_key = models.CharField(max_length=100, blank=True, null=True)
    key_expires = models.DateTimeField(default=timezone.now)
    company_title = models.CharField(max_length=200,
                                     verbose_name="Company Title", blank=True,
                                     null=True)
    search_profile_security = models.IntegerField(
        choices=SECURITY_SEARCH_CHOICES, verbose_name="Security Search",
        blank=False, default=NOTIFICATION_YES)
    business_type = models.CharField(choices=BUSINESS_TYPE_CHOICES,
                                     max_length=300,
                                     verbose_name="Business Type", blank=True,
                                     null=True)

    # Video, Payment, Copyright Management For Staff or Admin User.
    video_management_rights = models.BooleanField('Video Management',
                                                  default=False, blank=True)
    payment_management_rights = models.BooleanField('Payment Management',
                                                    default=False, blank=True)
    copyright_investigation_rights = models.BooleanField('Copyright Management',
                                                         default=False,
                                                         blank=True)
    inappropriate_rights = models.BooleanField('Inappropriate Management',
                                               default=False, blank=True)
    bug_rights = models.BooleanField('Bug Management', default=False,
                                     blank=True)
    email_sent = models.BooleanField('Mail Sent', default=False, blank=True)

    def greet(self):
        return {
            self.GENDER_MALE: 'Hi, boy',
            self.GENDER_FEMALE: 'Hi, girl.'
        }[self.gender]

    def last_seen(self):
        return cache.get('seen_%s' % self.user.username)

    def online(self):
        if self.last_seen():
            now = datetime.now()
            if now > self.last_seen() + timedelta(
                    seconds=settings.USER_ONLINE_TIMEOUT):
                return False
            else:
                return True
        else:
            return False

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profile"

User.profile = property(lambda u: Profile.objects.get_or_create(user=u)[0])
