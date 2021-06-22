from datetime import date
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.contrib.auth.models import Group
from django.forms import extras
from datetime import datetime
from django import forms
from user.models import ProfileImg, Profile


class RegistrationForm(forms.Form):
    username = forms.RegexField(regex=r'^\w+$', widget=forms.TextInput(
        attrs=dict(required=True, max_length=30)
    ), label=_("Username"), error_messages={
        'invalid': _("This value must contain only letters, numbers and underscores.")})
    email = forms.EmailField(widget=forms.TextInput(
        attrs=dict(required=True, max_length=30)
    ), label=_("Email address"))
    password1 = forms.CharField(widget=forms.PasswordInput(
        attrs=dict(required=True, max_length=30, render_value=False)
    ), label=_("Password"))
    password2 = forms.CharField(widget=forms.PasswordInput(
        attrs=dict(required=True, max_length=30, render_value=False)
    ), label=_("Password (again)"))

    def clean_username(self):
        try:
            User.objects.get(
                username__iexact=self.cleaned_data['username']
            )
        except User.DoesNotExist:
            return self.cleaned_data['username']
        raise forms.ValidationError(_("The username already exists. "
                                      "Please try another one."))

    def clean_email(self):
        try:
            User.objects.get(
                email__iexact=self.cleaned_data['email']
            )
        except User.DoesNotExist:
            return self.cleaned_data['email']
        raise forms.ValidationError(_("This email is already in use. Please try another."))

    def clean(self):
        if 'password1' in self.cleaned_data and 'password2' in self.cleaned_data:
            if self.cleaned_data['password1'] != self.cleaned_data['password2']:
                raise forms.ValidationError(_("The two password fields "
                                              "did not match."))
        return self.cleaned_data


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        widgets = {
            'username': forms.TextInput(
                attrs={'placeholder': 'User Name', 'required': 'True'}
            ),

            'first_name': forms.TextInput(
                attrs={'placeholder': 'First Name', 'required': 'True'}
            ),
            'last_name': forms.TextInput(
                attrs={'placeholder': 'Last Name', 'required': 'True'}
            ),

            'email': forms.TextInput(
                attrs={'placeholder': 'E-mail Address ', 'required': 'True'}
            ),
            'password': forms.TextInput(attrs={
                'required': 'True', 'max_length': '30', 'render_value': 'False'
            }),
        }
        fields = ('username', 'email', 'first_name', 'last_name')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        username = self.cleaned_data.get('username')
        if email and User.objects.filter(email=email).exclude(username=username).exists():
            raise forms.ValidationError(u'User with this Email address already exists.')
        return email


class ProfileForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ProfileForm, self).__init__(*args, **kwargs)
        self.fields['gender'].choices = self.fields['gender'].choices[1:]

    current_year = datetime.now().year - 13
    birthdate = forms.DateField(widget=extras.SelectDateWidget(years=range(current_year, 1930, -1)))

    def clean_birthdate(self):
        # validate age. need to be more than 13 years old
        birthdate = self.cleaned_data['birthdate']
        today = date.today()
        age = today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))
        if age < 13:
            raise forms.ValidationError(u'You need to be at least 13 years of age to be a member of Skigit')
        else:
            return birthdate

    class Meta:
        model = Profile
        widgets = {
            'profile_img': forms.FileInput(
                attrs={'placeholder': 'Profile Picture'}
            ),
            'birthdate': forms.TextInput(
                attrs={'placeholder': 'Date Of Birth', 'required': 'True'}
            ),
            'zip_code': forms.TextInput(
                attrs={'placeholder': 'zip_code', 'required': 'True'}
            ),
            'gender': forms.RadioSelect(
                attrs={'placeholder': 'Gender', 'required': 'True'},
            ),
            'language': forms.Select(
                attrs={'placeholder': 'Language', 'required': 'True'}
            ),
            'country': forms.Select(
                attrs={'placeholder': 'country', 'required': 'True'}
            ),
            'state': forms.TextInput(
                attrs={'placeholder': 'state', 'required': 'True'}
            ),
            'city': forms.TextInput(
                attrs={'placeholder': 'city', 'required': 'True'}
            ),
            'about_me': forms.Textarea(
                attrs={'placeholder': 'About Me', 'rows': '4', 'required': 'True'}
            ),

        }
        fields = ('profile_img', 'gender', 'birthdate', 'about_me', 'language', 'country', 'state', 'city', 'zip_code',
                  'search_profile_security')


class SignupForm(forms.Form):
    pass

    def signup(self, request, user):
        user.is_active = False
        role = request.session.get('user_type')
        g = Group.objects.get(name=settings.GENERAL_USER)
        user.groups.add(g)
        user.save()


class BusinessUserProfileForm(forms.ModelForm):
    current_year = datetime.now().year - 13
    birthdate = forms.DateField(widget=extras.SelectDateWidget(years=range(current_year, 1930, -1)))
    contact_email = forms.EmailField(required=True, error_messages={'required': "This field required"})
    payment_email = forms.EmailField(required=True, error_messages={'required': "This field required"})

    def __init__(self, *args, **kwargs):
        super(BusinessUserProfileForm, self).__init__(*args, **kwargs)
        self.fields['gender'].choices = self.fields['gender'].choices[1:]
        self.fields['incentive'].choices = self.fields['incentive'].choices[1:]

    class Meta:
        model = Profile
        widgets = {
            'profile_img': forms.FileInput(
                attrs={'placeholder': 'Profile Picture'}
            ),
            'company_title': forms.TextInput(
                attrs={'placeholder': 'Company Title', 'required': 'True'}
            ),
            'zip_code': forms.TextInput(
                attrs={'placeholder': 'zip_code', 'required': 'True'}
            ),
            'gender': forms.RadioSelect(
                attrs={'placeholder': 'Gender', 'required': 'True'},
            ),
            'incentive': forms.RadioSelect(
                attrs={'placeholder': 'Incentive', 'required': 'True'},
            ),
            'language': forms.Select(
                attrs={'placeholder': 'Language', 'required': 'True'}
            ),
            'country': forms.Select(
                attrs={'placeholder': 'country', 'required': 'True',}
            ),
            'city': forms.TextInput(
                attrs={'placeholder': 'city', 'required': 'True'}
            ),
            'coupan_image': forms.FileInput(
                attrs={'placeholder': 'Coupan Image'}
            ),
            'contact_name': forms.TextInput(
                attrs={'placeholder': 'Contact Name', 'required': 'True'}
            ),
            'contact_phone': forms.TextInput(
                attrs={'placeholder': 'Contact Phone', 'required': 'True'}
            ),
            'incetive_val': forms.TextInput(
                attrs={'placeholder': 'Incentive value', "autocomplete": "off"}
            ),
            'payment_user_name': forms.TextInput(
                attrs={'placeholder': 'Payment Name', 'required': 'True'}
            ),
            'business_type':
                forms.Select(
                    attrs={'placeholder': 'business_type', 'required': 'True'}
                ),
            'payment_method': forms.RadioSelect(
                attrs={'placeholder': 'Payment Method', 'required': 'True'},
            )
        }

        fields = ('profile_img', 'company_title', 'gender', 'birthdate', 'about_me', 'language', 'country',
                  'state', 'city', 'zip_code', 'search_profile_security', 'incentive', 'skigit_incentive',
                  'redemoption_instrucations', 'coupan_code', 'incetive_val', 'contact_name', 'contact_email',
                  'contact_phone', 'biller_name', 'payment_method', 'biller_address1', 'biller_address2',
                  'payment_email',
                  'payment_user_name', 'business_type')


class ProfileNotificationForm(forms.ModelForm):
    class Meta:
        model = Profile
        widgets = {

            'like_notify': forms.CheckboxInput(),
            'follow_un_follow_notify': forms.CheckboxInput(),
            'friends_request_notify': forms.CheckboxInput(),
            'friends_accept_notify': forms.CheckboxInput(),
            'plug_notify': forms.CheckboxInput(),
            'un_plug_notify': forms.CheckboxInput(),
            'skigit_notify': forms.CheckboxInput(),
            'share_notify': forms.CheckboxInput(),

        }

        fields = ('like_notify', 'follow_un_follow_notify', 'friends_request_notify', 'friends_accept_notify',
                  'plug_notify', 'un_plug_notify', 'skigit_notify', 'share_notify')


class ProfileImgForm(forms.ModelForm):
    class Meta:
        model = ProfileImg
        widgets = {
            'profile_img': forms.FileInput(
                attrs={'placeholder': 'Cover Images', 'multiple': 'multiple'}
            ),
        }
        fields = ('profile_img',)
