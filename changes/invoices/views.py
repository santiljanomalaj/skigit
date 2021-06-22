import ast
import datetime
from decimal import Decimal
from operator import itemgetter
from user.models import BusinessLogo, Profile, ProfileUrl

import braintree
import Crypto
from Crypto import Random
from Crypto.PublicKey import RSA
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.db.models.aggregates import Sum
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from rest_framework.views import APIView

from core.utils import get_user_type, json_response, payment_required, require_filled_profile
from invoices.models import *
from invoices.models import InvoiceBilling
# Create your views here.
from skigit_project import settings

braintree.Configuration.configure(
    braintree.Environment.Sandbox,
    merchant_id=settings.BRAINTREE_MERCHANT_ID,
    public_key=settings.BRAINTREE_PUBLIC_KEY,
    private_key=settings.BRAINTREE_PRIVATE_KEY
)


@staticmethod
def get_rsa_encryption(card_detail, bits=2048):
    """
        RSA Algorithm For Create Encrypted Private and Public key
    """
    random_generator = Random.new().read
    key = RSA.generate(bits, random_generator)
    public_key = key.publickey()  # pub key export for exchange
    encrypted = public_key.encrypt(card_detail, 128)
    # message to encrypt is in the above line 'encrypt this message'
    decrypted = key.decrypt(ast.literal_eval(str(encrypted)))
    return encrypted


def get_rsa_decryption(m):
    """
        RSA Algorithm For Create Decryption Private and Public key
    """
    pass


@csrf_protect
def business_logo_invoice(request):
    """
        Business Logo Invoice
    """
    response_data = {'is_success': False, 'message': 'Error in to Business Logo Invoice! Try again Later. '
                                                     'or Contact to Administrator'}

    if request.is_ajax() and request.method == 'POST':

        if get_user_type(request.user) == 'business':
            logo = request.POST.get('logo_id', None)
            busniesslogo = BusinessLogo.objects.get(id=int(logo), is_deleted=False)
            profile = Profile.objects.get(logo_img=busniesslogo)
            current_month = datetime.datetime.now().date().month
            current_year = datetime.datetime.now().date().year
            if VisitCharges.objects.exists():
                visitor = VisitCharges.objects.all()[0]
            else:
                VisitCharges.objects.create()
                visitor = VisitCharges.objects.all()[0]
            if not profile.user.username == request.user.username:
                if not BusinessLogoInvoice.objects.filter(user=request.user, logo_user=profile.user,
                                                          billing_month__month=current_month,
                                                          business_logo=busniesslogo,
                                                          billing_month__year=current_year
                                                          ).exists():

                    BusinessLogoInvoice.objects.create(user=request.user, logo_user=profile.user, logo_count=1,
                                                       billing_month=datetime.datetime.now().date(),
                                                       business_logo=busniesslogo)

                    b_invoice = BusinessLogoInvoice.objects.get(user=request.user, logo_user=profile.user,
                                                                billing_month=datetime.datetime.now().date(),
                                                                business_logo=busniesslogo)

                    BusinessLogoInvoice.objects.filter(user=request.user, logo_user=profile.user,
                                                       billing_month__month=current_month,
                                                       billing_month__year=current_year,
                                                       business_logo=busniesslogo
                                                       ).update(total_logo_count=1,
                                                                user_total_due=visitor.logo_charge,
                                                                logo_total_amount=visitor.logo_charge)

                    total_count = BusinessLogoInvoice.objects.filter(logo_user=profile.user,
                                                                     billing_month__month=current_month,
                                                                     billing_month__year=current_year
                                                                     ).aggregate(logo_t_count=Sum('logo_count')
                                                                                 )['logo_t_count']
                    t_count = int(total_count)
                    total_due = t_count * visitor.logo_charge
                    BusinessLogoInvoice.objects.filter(logo_user=profile.user, billing_month__month=current_month,
                                                       billing_month__year=current_year
                                                       ).update(total_logo_count=t_count, user_total_due=total_due)

                    total_amount = b_invoice.logo_count * visitor.logo_charge
                    response_data['is_success'] = True
                    response_data['message'] = "Current Month %s's Count %s and Due Amount is:%s" \
                                               % (str(b_invoice.billing_month.month), str(b_invoice.logo_count),
                                                  str(total_amount))
                else:
                    b_invoice = BusinessLogoInvoice.objects.get(user=request.user, logo_user=profile.user,
                                                                business_logo=busniesslogo,
                                                                billing_month__month=datetime.datetime.now().date().month,
                                                                billing_month__year=datetime.datetime.now().date().year)
                    count = b_invoice.logo_count + 1
                    total_amount = count * visitor.logo_charge
                    total_count = BusinessLogoInvoice.objects.filter(logo_user=profile.user,
                                                                     billing_month__month=datetime.datetime.now().date().month,
                                                                     billing_month__year=datetime.datetime.now().date().year
                                                                     ).aggregate(logo_t_count=Sum('logo_count'))[
                        'logo_t_count']
                    t_count = int(total_count) + 1
                    total_due = t_count * visitor.logo_charge
                    BusinessLogoInvoice.objects.filter(logo_user=profile.user,
                                                       billing_month__month=datetime.datetime.now().date().month,
                                                       billing_month__year=datetime.datetime.now().date().year
                                                       ).update(total_logo_count=t_count, user_total_due=total_due)

                    BusinessLogoInvoice.objects.filter(user=request.user, logo_user=profile.user,
                                                       business_logo=busniesslogo,
                                                       billing_month__month=datetime.datetime.now().date().month,
                                                       billing_month__year=datetime.datetime.now().date().year
                                                       ).update(logo_count=count, logo_total_amount=total_amount)
                    response_data['is_success'] = True
                    response_data['message'] = "Current Month %s's Count %s and Due Amount is:%s" \
                                               % (str(b_invoice.billing_month.month), str(count), str(total_amount))
            else:
                response_data['is_success'] = True
                response_data['message'] = 'Logo is uploaded by Current user- Charges are Not applicable'
        else:
            response_data['is_success'] = True
            response_data['message'] = ' %s is general user - (Note: Payment Not Applicable to General User)' \
                                       % request.user.username
    return json_response(response_data)


@csrf_protect
def business_weblink_invoice(request):
    """
        Business Web Link Invoice
    """
    response_data = {'is_success': False, 'message': 'Error in to Web Link Invoice! Try again Later'
                                                     ' or Contact to Administrator'}
    if request.is_ajax() and request.method == 'POST':
        web_user = request.POST.get('link_user', None)
        web_url = request.POST.get('web_link', None)
        profile = ProfileUrl.objects.get(user__id=int(web_user))
        if get_user_type(profile.user) == 'business':
            current_month = datetime.datetime.now().date().month
            current_year = datetime.datetime.now().date().year
            if VisitCharges.objects.exists():
                visitor = VisitCharges.objects.all()[0]
            else:
                VisitCharges.objects.create()
                visitor = VisitCharges.objects.all()[0]
            if not profile.user.username == request.user.username:
                if not WebLinkInvoice.objects.filter(user=request.user, web_link_user=profile.user, web_link=web_url,
                                                     billing_month__month=current_month,
                                                     billing_month__year=current_year).exists():
                    WebLinkInvoice.objects.create(user=request.user, web_link_user=profile.user, web_link=web_url,
                                                  billing_month=datetime.datetime.now().date(), link_count=1)
                    link_invoice = WebLinkInvoice.objects.get(user=request.user, web_link_user=profile.user,
                                                              web_link=web_url, billing_month__month=current_month,
                                                              billing_month__year=current_year)
                    link_due = link_invoice.link_count * visitor.link_charge
                    WebLinkInvoice.objects.filter(user=request.user, web_link_user=profile.user, web_link=web_url,
                                                  billing_month__month=current_month, billing_month__year=current_year
                                                  ).update(link_due_amount=link_due)
                    total_count = WebLinkInvoice.objects.filter(user=request.user, web_link_user=profile.user,
                                                                web_link=web_url, billing_month__month=current_month,
                                                                billing_month__year=current_year
                                                                ).aggregate(w_link_count=Sum('link_count')
                                                                            )['w_link_count']
                    t_count = int(total_count)
                    total_due = t_count * visitor.link_charge
                    WebLinkInvoice.objects.filter(user=request.user, web_link_user=profile.user, web_link=web_url,
                                                  billing_month__month=current_month, billing_month__year=current_year
                                                  ).update(link_total_count=t_count, link_total_due=total_due)

                    response_data['is_success'] = True
                    response_data['message'] = "Current Month %s's Count %s and Due Amount is:%s" \
                                               % (str(link_invoice.billing_month.month), str(t_count),
                                                  str(total_due))
                else:
                    link_invoice = WebLinkInvoice.objects.get(user=request.user, web_link_user=profile.user,
                                                              web_link=web_url, billing_month__month=current_month,
                                                              billing_month__year=current_year)
                    count = link_invoice.link_count + 1
                    total_amount = count * visitor.link_charge
                    total_count = WebLinkInvoice.objects.filter(user=request.user,
                                                                billing_month__month=current_month,
                                                                billing_month__year=current_year
                                                                ).aggregate(w_link_count=Sum('link_count')
                                                                            )['w_link_count']
                    WebLinkInvoice.objects.filter(user=request.user, web_link_user=profile.user, web_link=web_url,
                                                  billing_month__year=current_year
                                                  ).update(link_count=count, link_due_amount=total_amount)
                    t_count = int(total_count + 1)
                    total_due = t_count * visitor.link_charge
                    WebLinkInvoice.objects.filter(user=request.user,
                                                  billing_month__month=current_month, billing_month__year=current_year
                                                  ).update(link_total_count=t_count, link_total_due=total_due)

                    response_data['is_success'] = True
                    response_data['message'] = "Current Month %s's Count %s and Due Amount is:%s" \
                                               % (str(link_invoice.billing_month.month), str(t_count), str(total_due))
            else:
                response_data['is_success'] = True
                response_data['message'] = 'Web Link is uploaded by Current user- Charges are Not applicable'
        else:
            response_data['is_success'] = True
            response_data['message'] = ' %s is general user - (Note: Payment Not Applicable to General User)' \
                                       % request.user.username
    return json_response(response_data)


@csrf_protect
def business_post_invoice(request):
    """
        Business Post Invoice
    """
    response_data = {'is_success': False, 'message': 'Error in to Post Invoice! Try again Later '
                                                     'or Contact to Administrator.'}
    if request.is_ajax() and request.method == 'POST':
        ski_user = request.POST.get('skigit_user', None)
        ski_id = request.POST.get('skigit_id', None)
        social_type = request.POST.get('social_type', None)
        vid_obj = VideoDetail.objects.get(skigit_id__id=int(ski_id))

        if VisitCharges.objects.exists():
            visitor = VisitCharges.objects.all()[0]
        else:
            VisitCharges.objects.create()
            visitor = VisitCharges.objects.all()[0]
        current_month = datetime.datetime.now().date().month
        current_year = datetime.datetime.now().date().year
        current_date = datetime.datetime.now().date()

        if vid_obj.made_by:
            l_user = vid_obj.made_by
            if not l_user == request.user.username:
                if not PostInvoice.objects.filter(user=request.user, post_ski=vid_obj, logo_user=l_user,
                                                  social_network_type=social_type, billing_month__month=current_month,
                                                  billing_month__year=current_year).exists():
                    PostInvoice.objects.create(user=request.user, logo_user=l_user, post_ski=vid_obj,
                                               billing_month=current_date, social_network_type=social_type,
                                               post_count=1)
                    post_invoice = PostInvoice.objects.get(user=request.user, logo_user=l_user, post_ski=vid_obj,
                                                           social_network_type=social_type,
                                                           billing_month__month=current_month,
                                                           billing_month__year=current_year)
                    post_due = post_invoice.post_count * visitor.post_charge
                    PostInvoice.objects.filter(user=request.user, logo_user=l_user, post_ski=vid_obj,
                                               billing_month=current_date, post_count=1
                                               ).update(skigit_post_amount=post_due)
                    total_count = PostInvoice.objects.filter(logo_user=l_user,
                                                             billing_month__month=current_month,
                                                             billing_month__year=current_year
                                                             ).aggregate(post_ski_count=Sum('post_count')
                                                                         )['post_ski_count']
                    t_count = int(total_count)
                    total_due = t_count * visitor.post_charge
                    PostInvoice.objects.filter(logo_user=l_user, billing_month__month=current_month,
                                               billing_month__year=current_year).update(post_total_count=t_count,
                                                                                        post_total_amount=total_due)
                    response_data['is_success'] = True
                    response_data['message'] = "Social Post Current Month %s's Count %s and Due Amount is:%s" % \
                                               (str(post_invoice.billing_month.month), str(t_count), str(total_due))
                else:
                    post_invoice = PostInvoice.objects.get(user=request.user, post_ski=vid_obj,
                                                           logo_user=l_user,
                                                           social_network_type=social_type,
                                                           billing_month__month=current_month,
                                                           billing_month__year=current_year)
                    count = post_invoice.post_count + 1
                    total_amount = count * visitor.post_charge
                    total_count = PostInvoice.objects.filter(logo_user=l_user,
                                                             billing_month__month=current_month,
                                                             billing_month__year=current_year
                                                             ).aggregate(post_ski_count=Sum('post_count')
                                                                         )['post_ski_count']

                    PostInvoice.objects.filter(user=request.user, logo_user=l_user, post_ski=vid_obj,
                                               billing_month__month=current_month, billing_month__year=current_year
                                               ).update(post_count=count, skigit_post_amount=total_amount)

                    t_count = int(total_count + 1)
                    total_due = t_count * visitor.post_charge
                    PostInvoice.objects.filter(logo_user=l_user, billing_month__month=current_month,
                                               billing_month__year=current_year).update(post_total_count=t_count,
                                                                                        post_total_amount=total_due)
                    response_data['is_success'] = True
                    response_data['message'] = "Social Post Current Month %s's Count %s and Due Amount is:%s" \
                                               % (str(post_invoice.billing_month.month), str(t_count), str(total_due))
            else:
                response_data['is_success'] = True
                response_data['message'] = 'Skigit is property of Current user/ General user -' \
                                           ' Charges are not applicable.'
    return json_response(response_data)


def business_plug_invoice(request, plug_ski, plugin_user, ski_id, logo_user):
    """
        Business Plug-in Invoice
    """
    response_data = {'is_success': False,
                     'message': 'Error in to Post Invoice! Try again Later or Contact to Administrator.'}

    b_logo_user = User.objects.get(pk=int(logo_user))
    plug_user = User.objects.get(pk=int(plugin_user))
    vid_obj = VideoDetail.objects.get(id=int(ski_id))
    plug_obj = VideoDetail.objects.get(id=int(plug_ski))
    current_month = datetime.datetime.now().date().month
    current_year = datetime.datetime.now().date().year
    current_date = datetime.datetime.now().date()

    if VisitCharges.objects.exists():
        visitor = VisitCharges.objects.all()[0]
    else:
        VisitCharges.objects.create()
        visitor = VisitCharges.objects.all()[0]

    if not PluginInvoice.objects.filter(user=plug_user, skigit_user=b_logo_user, primary_ski=plug_obj,
                                        plugin_ski=vid_obj, billing_month__month=current_month,
                                        billing_month__year=current_year).exists():
        PluginInvoice.objects.create(user=plug_user, skigit_user=b_logo_user,
                                     plugin_ski=vid_obj, primary_ski=plug_obj, billing_month=current_date,
                                     plugin_count=1)
        plug_invoice = PluginInvoice.objects.get(user=plug_user, plugin_ski=vid_obj, primary_ski=plug_obj,
                                                 skigit_user=b_logo_user,
                                                 billing_month__month=current_month,
                                                 billing_month__year=current_year)
        plug_due = plug_invoice.plugin_count * visitor.plug_charge
        PluginInvoice.objects.filter(user=plug_user, skigit_user=b_logo_user, plugin_ski=vid_obj, primary_ski=plug_obj,
                                     billing_month=current_date, plugin_count=1
                                     ).update(current_plugin_amount=plug_due)
        total_count = PluginInvoice.objects.filter(skigit_user=b_logo_user,
                                                   billing_month__month=current_month,
                                                   billing_month__year=current_year
                                                   ).aggregate(plug_ski_count=Sum('plugin_count')
                                                               )['plug_ski_count']
        t_count = int(total_count)
        total_due = t_count * visitor.plug_charge
        PluginInvoice.objects.filter(skigit_user=b_logo_user, billing_month__month=current_month,
                                     billing_month__year=current_year).update(plugin_total_count=t_count,
                                                                              plugin_total_amount=total_due)
        response_data['is_success'] = True
        response_data['message'] = "Social Post Current Month %s's Count %s and Due Amount is:%s" % \
                                   (str(plug_invoice.billing_month.month), str(t_count), str(total_due))
    else:
        plug_invoice = PluginInvoice.objects.get(user=plug_user, plugin_ski=vid_obj, primary_ski=plug_obj,
                                                 skigit_user=b_logo_user, billing_month__month=current_month,
                                                 billing_month__year=current_year)
        count = plug_invoice.plugin_count + 1
        total_amount = count * visitor.plug_charge
        total_count = PluginInvoice.objects.filter(skigit_user=b_logo_user, billing_month__month=current_month,
                                                   billing_month__year=current_year
                                                   ).aggregate(plug_ski_count=Sum('plugin_count'))['plug_ski_count']

        PluginInvoice.objects.filter(user=plug_user, skigit_user=b_logo_user, primary_ski=plug_obj, plugin_ski=vid_obj,
                                     billing_month__month=current_month, billing_month__year=current_year
                                     ).update(plugin_count=count, current_plugin_amount=total_amount)

        t_count = int(total_count + 1)
        total_due = t_count * visitor.plug_charge
        PluginInvoice.objects.filter(skigit_user=b_logo_user, billing_month__month=current_month,
                                     billing_month__year=current_year).update(plugin_total_count=t_count,
                                                                              plugin_total_amount=total_due)
        response_data['is_success'] = True
        response_data['message'] = "Social Post Current Month %s's Count %s and Due Amount is:%s" \
                                   % (str(plug_invoice.billing_month.month),
                                      str(t_count), str(total_due))
    return json_response(response_data)


def business_share_invoice(visit_user, ski_id):
    """
        Business Share Invoice
    """
    response_data = {'is_success': False,
                     'message': 'Error in to Post Invoice! Try again Later or Contact to Administrator.'}
    v_user = User.objects.get(pk=int(visit_user))
    vid_obj = VideoDetail.objects.get(skigit_id__id=int(ski_id))
    if VisitCharges.objects.exists():
        visitor = VisitCharges.objects.all()[0]
    else:
        VisitCharges.objects.create()
        visitor = VisitCharges.objects.all()[0]
    current_month = datetime.datetime.now().date().month
    current_year = datetime.datetime.now().date().year
    current_date = datetime.datetime.now().date()

    if vid_obj.made_by:
        logo_user = vid_obj.made_by
        if not ShareInvoice.objects.filter(user=v_user, skigit_user=logo_user, share_ski=vid_obj,
                                           billing_month__month=current_month,
                                           billing_month__year=current_year).exists():
            ShareInvoice.objects.create(user=v_user, skigit_user=logo_user, share_ski=vid_obj,
                                        billing_month=current_date, share_count=1)
            share_invoice = ShareInvoice.objects.get(user=v_user, share_ski=vid_obj, skigit_user=logo_user,
                                                     billing_month__month=current_month,
                                                     billing_month__year=current_year)
            post_due = share_invoice.share_count * visitor.share_charge
            ShareInvoice.objects.filter(user=v_user, skigit_user=logo_user, share_ski=vid_obj,
                                        billing_month=current_date,
                                        share_count=1).update(skigit_share_amount=post_due)
            total_count = ShareInvoice.objects.filter(skigit_user=logo_user, billing_month__month=current_month,
                                                      billing_month__year=current_year
                                                      ).aggregate(post_ski_count=Sum('share_count'))['post_ski_count']
            t_count = int(total_count)
            total_due = t_count * visitor.post_charge
            ShareInvoice.objects.filter(skigit_user=logo_user, billing_month__month=current_month,
                                        billing_month__year=current_year).update(total_share_count=t_count,
                                                                                 share_total_amount=total_due)
            response_data['is_success'] = True
            response_data['message'] = "Social Post Current Month %s's Count %s and Due Amount is:%s" % \
                                       (str(share_invoice.billing_month.month), str(t_count), str(total_due))
        else:
            share_invoice = ShareInvoice.objects.get(user=v_user, share_ski=vid_obj, skigit_user=logo_user,
                                                     billing_month__month=current_month,
                                                     billing_month__year=current_year)
            count = share_invoice.share_count + 1
            total_amount = count * visitor.share_charge
            total_count = ShareInvoice.objects.filter(skigit_user=logo_user, billing_month__month=current_month,
                                                      billing_month__year=current_year
                                                      ).aggregate(share_ski_count=Sum('share_count'))['share_ski_count']

            ShareInvoice.objects.filter(user=v_user, skigit_user=logo_user, share_ski=vid_obj,
                                        billing_month__month=current_month, billing_month__year=current_year
                                        ).update(share_count=count, skigit_share_amount=total_amount)

            t_count = int(total_count + 1)
            total_due = t_count * visitor.share_charge
            ShareInvoice.objects.filter(skigit_user=logo_user, billing_month__month=current_month,
                                        billing_month__year=current_year
                                        ).update(total_share_count=t_count, share_total_amount=total_due)
            response_data['is_success'] = True
            response_data['message'] = "Social Post Current Month %s's Count %s and Due Amount is: %s" \
                                       % (str(share_invoice.billing_month.month), str(t_count), str(total_due))
    return json_response(response_data)


@csrf_protect
def business_embed_invoice(request):
    """
        Business Embed Invoice
    """
    response_data = {'is_success': False,
                     'message': 'Error in to Web Link Invoice! Try again Later or Contact to Administrator'}

    if request.is_ajax() and request.method == 'POST':
        ski_id = request.POST.get('skigit_id', None)
        vid_obj = VideoDetail.objects.get(id=int(ski_id))

        if VisitCharges.objects.exists():
            visitor = VisitCharges.objects.all()[0]
        else:
            VisitCharges.objects.create()
            visitor = VisitCharges.objects.all()[0]

        current_month = datetime.datetime.now().date().month
        current_year = datetime.datetime.now().date().year
        current_date = datetime.datetime.now().date()
        if get_user_type(request.user) == 'business':
            if not EmbedInvoice.objects.filter(user=request.user, skigit_user=vid_obj.skigit_id.user, embed_ski=vid_obj,
                                               billing_month__month=current_month, billing_month__year=current_year
                                               ).exists():
                EmbedInvoice.objects.create(user=request.user, skigit_user=vid_obj.skigit_id.user, embed_ski=vid_obj,
                                            billing_month=current_date, embed_count=1)
                embed_invoice = EmbedInvoice.objects.get(user=request.user, embed_ski=vid_obj,
                                                         skigit_user=vid_obj.skigit_id.user,
                                                         billing_month__month=current_month,
                                                         billing_month__year=current_year)
                embed_due = embed_invoice.embed_count * visitor.embed_charge
                EmbedInvoice.objects.filter(user=request.user, skigit_user=vid_obj.skigit_id.user, embed_ski=vid_obj,
                                            billing_month=current_date, embed_count=1
                                            ).update(skigit_embed_amount=embed_due)
                total_count = EmbedInvoice.objects.filter(skigit_user=vid_obj.skigit_id.user,
                                                          billing_month__month=current_month,
                                                          billing_month__year=current_year
                                                          ).aggregate(embed_ski_count=Sum('embed_count')
                                                                      )['embed_ski_count']
                t_count = int(total_count)
                total_due = t_count * visitor.embed_charge
                EmbedInvoice.objects.filter(user=request.user, billing_month__month=current_month,
                                            billing_month__year=current_year).update(embed_total_count=t_count,
                                                                                     embed_total_amount=total_due)
                response_data['is_success'] = True
                response_data['message'] = "Social Post Current Month %s's Count %s and Due Amount is:%s" % \
                                           (str(embed_invoice.billing_month.month), str(t_count), str(total_due))
            else:
                response_data['is_success'] = True
                response_data['message'] = "Already charges are apply for %s skigit for Current Month." % vid_obj.title

        return json_response(response_data)


def get_total_payable_amount(request):
    pass


def find_customer(request, token):
    """
        Fined Customer Already Set in Braintree Vault.

    Args:
        request: request method
        token: Customer token
    """
    customer = braintree.CreditCard.find(token)
    return customer


def find_pay_pal_customer(request, token):
    """
        Find Paypal Account Customer

    Args:
        request: request method
        token: customer token
    """
    customer = braintree.PaymentMethod.find(token)
    return customer


def client_token(request):
    """
        Generate a client Token for client
    """
    if not Invoice.objects.filter(user=request.user, type='CreditCard', is_deleted=False).exists():
        token = braintree.ClientToken.generate()
    else:
        invoice_obj = Invoice.objects.filter(user=request.user, type='CreditCard', is_deleted=False).first()
        token = braintree.ClientToken.generate({'customer_id': invoice_obj.customer_id})
    return token


def client_PayPal_token(request):
    """
        Generate a client Token for client

    Args:
        request: requested data
    """
    if not Invoice.objects.filter(user=request.user, type='PayPalAccount', is_deleted=False).exists():
        token = braintree.ClientToken.generate()
    else:
        invoice_obj = Invoice.objects.filter(user=request.user, type='PayPalAccount', is_deleted=False).first()
        token = braintree.ClientToken.generate({'customer_id': invoice_obj.customer_id})
    return token


@csrf_protect
def customer_create(request):
    """
        Braintree Vault Customer create
    """
    response_data = {'is_success': False, 'message': 'Error into Card Saving. Please Contact to Administrator.'}
    if request.is_ajax() and request.method == 'POST':
        if not Invoice.objects.filter(user=request.user, type='CreditCard', is_deleted=False).exists():
            nonce_from_the_client = request.POST.get('nonce', None)
            cardholder_name = request.POST.get('name_on_card', None)
            card_type = request.POST.get('type', None)
            if Profile.objects.filter(user=request.user).exists():
                profile_obj = Profile.objects.get(user=request.user)
                if profile_obj.biller_address1 and profile_obj.biller_address2:
                    address = '%s %s' % (str(profile_obj.biller_address1), str(profile_obj.biller_address2))
                elif profile_obj.biller_address1:
                    address = '%s' % str(profile_obj.biller_address1)
                elif profile_obj.biller_address1:
                    address = '%s' % str(profile_obj.biller_address2)
                else:
                    address = 'Address Not mention by user %s' % request.user.username

                result = braintree.Customer.create({
                    'first_name': request.user.first_name,
                    'last_name': request.user.last_name,
                    'company': profile_obj.company_title,
                    'email': request.user.email,
                    'credit_card': {
                        'cardholder_name': cardholder_name,
                        "payment_method_nonce": nonce_from_the_client,
                        'options': {
                            'verify_card': True,
                        },
                        'billing_address': {
                            'first_name': request.user.first_name,
                            'last_name': request.user.last_name,
                            'company': profile_obj.company_title,
                            'street_address': address,
                            'locality': profile_obj.city,
                            'region': profile_obj.state,
                            'postal_code': profile_obj.zip_code
                        },
                    },
                })
            else:

                result = braintree.Customer.create({
                    'first_name': request.user.first_name,
                    'last_name': request.user.last_name,
                    'email': request.user.email,
                    'credit_card': {
                        'cardholder_name': cardholder_name,
                        "payment_method_nonce": nonce_from_the_client,
                        'options': {
                            'verify_card': True,
                        },
                        'billing_address': {
                            'first_name': request.user.first_name,
                            'last_name': request.user.last_name,
                        },
                    },
                })

            if result.is_success:
                invoice_obj = None
                customer_transaction = find_customer(request, result.customer.payment_methods[0].token)
                last4 = '%4d' % int(customer_transaction.last_4)
                inv = Invoice.objects.create(user=request.user, customer_id=customer_transaction.customer_id,
                                             last_4=last4, first_6=customer_transaction.bin,
                                             credit_card_type=customer_transaction.card_type, type=card_type,
                                             c_image_url=customer_transaction.image_url,
                                             cardholder_name=customer_transaction.cardholder_name,
                                             customer_location=customer_transaction.customer_location,
                                             issuing_bank=customer_transaction.issuing_bank,
                                             country_of_issuance=customer_transaction.country_of_issuance,
                                             card_status=customer_transaction.verifications[0]['status'],
                                             payment_method_token=customer_transaction.token,
                                             merchant_account_id=customer_transaction.verifications[0][
                                                 'merchant_account_id'],
                                             cvv_response_code=customer_transaction.verifications[0][
                                                 'cvv_response_code'],
                                             currency_iso_code=customer_transaction.verifications[0][
                                                 'currency_iso_code'],
                                             processor_response_code=customer_transaction.verifications[0][
                                                 'processor_response_code'],
                                             unique_number_identifier=customer_transaction.unique_number_identifier,
                                             debit=customer_transaction.debit)
                if inv:
                    invoice_obj = Invoice.objects.get(user=request.user, type='CreditCard', is_deleted=False)
                    response_data['is_success'] = True
                    response_data['message'] = 'Card Information Successfully saved on Braintree Vault.'
                    response_data['invoice'] = {'issuing_bank': customer_transaction.issuing_bank,
                                                'card': str('%06d****%04d') % (
                                                    int(customer_transaction.bin), int(last4)),
                                                'credit_card_type': customer_transaction.card_type,
                                                'card_status': customer_transaction.verifications[0]['status'],
                                                'card_image': customer_transaction.image_url}
                else:
                    response_data['is_success'] = False
                    response_data['message'] = 'Card saved on Braintree Vault. but Retrieving data failed.'
            else:
                response_data['is_success'] = False
                for error in result.errors.for_object("customer").for_object("credit_card"):
                    response_data['message'] = error.message
                    response_data['error_code'] = error.code
                    response_data['error_attribute'] = error.attribute
        else:
            invoice_obj = Invoice.objects.get(user=request.user, type='CreditCard', is_deleted=False)
            response_data['is_success'] = True
            response_data['message'] = 'This Customer Already Exists With Card Details'
            response_data['invoice'] = {'issuing_bank': invoice_obj.issuing_bank,
                                        'card': str('%06d****%04d') % (
                                            int(invoice_obj.first_6), int(invoice_obj.last_4)),
                                        'credit_card_type': invoice_obj.credit_card_type,
                                        'card_status': invoice_obj.card_status,
                                        'card_image': invoice_obj.c_image_url}
    return json_response(response_data)


@csrf_protect
def pay_pal_customer_create(request):
    """
        Braintree Vault Customer create
    """

    response_data = {'is_success': False, 'message': 'Error into Card Saving. Please Contact to Administrator.'}
    if request.is_ajax() and request.method == 'POST':
        if not Invoice.objects.filter(user=request.user, type='PayPalAccount', is_deleted=False).exists():
            if Profile.objects.filter(user=request.user).exists():
                profile_obj = Profile.objects.get(user=request.user)
                if profile_obj.company_title:
                    company = profile_obj.company_title
                else:
                    company = None
            nonce_from_the_client = request.POST.get('nonce', None)
            card_type = request.POST.get('type', None)
            result = braintree.Customer.create({
                'first_name': request.user.first_name,
                'last_name': request.user.last_name,
                'company': company,
                'payment_method_nonce': nonce_from_the_client,
            })
            print(result, '*'*60)
            if result.is_success:
                invoice_obj = None
                customer_transaction = find_pay_pal_customer(request, result.customer.payment_methods[0].token)

                inv = Invoice.objects.create(user=request.user, customer_id=customer_transaction.customer_id,
                                             type=card_type, email=customer_transaction.email,
                                             billing_agreement_id=customer_transaction.billing_agreement_id,
                                             c_image_url=customer_transaction.image_url,
                                             payment_method_token=customer_transaction.token)
                if inv:
                    invoice_obj = Invoice.objects.get(user=request.user, type='PayPalAccount', is_deleted=False)
                    response_data['is_success'] = True
                    response_data['message'] = 'PayPal information Successfully saved on Braintree Vault.'
                    response_data['invoice'] = {'email': invoice_obj.email, 'type': invoice_obj.type,
                                                'card_image': invoice_obj.c_image_url}
                else:
                    response_data['is_success'] = False
                    response_data['message'] = 'PayPal information saved on Braintree Vault. Data missing.'
            else:
                response_data['is_success'] = False
                for error in result.errors.for_object("customer"):
                    response_data['message'] = error.message
                    response_data['error_code'] = error.code
                    response_data['error_attribute'] = error.attribute
        else:
            invoice_obj = Invoice.objects.get(user=request.user, type='PayPalAccount', is_deleted=False)
            response_data['is_success'] = True
            response_data['message'] = 'This Customer Already Exists With PayPalAccount Details'
            response_data['invoice'] = {'email': invoice_obj.email, 'type': invoice_obj.type,
                                        'card_image': invoice_obj.c_image_url}
    return json_response(response_data)


def payment_method_remove(request):
    """
        Payment Account Removal function

        Args:
            request: Request method
    """
    response_data = {'is_success': False, 'message': 'Error into removing card/paypal details.'}
    if request.method == 'POST' and request.is_ajax():
        try:
            account_type = request.POST.get('type', None)
            inv = Invoice.objects.filter(user=request.user, type=account_type, is_deleted=False).update(is_deleted=True)
            if inv:
                response_data['is_success'] = True
                response_data['message'] = '%s details removed successful' % (account_type)
        except Exception as e:
            response_data['is_success'] = False
            response_data['message'] = 'Exception in Payment Account Removal time. Failed to remove.'
    return json_response(response_data)


def paypal_form(request):
    return render(request, 'payment/paypal_form.html', locals())


def payment_invoice(request):
    return render(request, 'payment/invoice_card.html', locals())


@login_required
@payment_required
@csrf_exempt
def invoice_payment(request):
    """ Skigit Invoice Detail View
    """
    year = request.GET.get('year', 0)
    month = int(request.GET.get('month', 0))
    user = request.user.username
    month_list = ['January', 'February', 'March', 'April', 'May', 'Jun', 'July', 'August', 'September',
                  'October', 'November', 'December']
    business_invoices_list = []
    year_list = range(request.user.date_joined.year, datetime.datetime.now().year + 1)

    if not year:
        year = datetime.datetime.now().year
    month = datetime.datetime.now().month
    if not int(year) == datetime.datetime.now().year:
        if int(month) == 1:
            year = int(year)-1
        month = 12
    date = datetime.date(int(year), month, 1)

    if request.user.profile.payment_method == '0':
        inv = Invoice.objects.filter(user=request.user, type='PayPalAccount', is_deleted=False).first()
        card_type = inv.type
        card_detail = inv.email
        card_img = inv.c_image_url
    elif request.user.profile.payment_method == '1':
        inv = Invoice.objects.filter(user=request.user, type='CreditCard', is_deleted=False).first()
        card_type = inv.type
        card_detail = str('%06d*****%04d') % (int(inv.first_6), int(inv.last_4))
        card_img = inv.c_image_url
    else:
        card_type, card_detail,  card_img = None
    
    if request.user.date_joined.year == year:
        start_range = request.user.date_joined.month
    else:
        start_range = 1
    billinglist = []
    for i in range(start_range, month + 1 if not int(year) == datetime.datetime.now().year else month+1):
        total_amount = Decimal(0.0)
        b_logo_users = BusinessLogoInvoice.objects.filter(Q(logo_user__username=user), billing_month__year=year,
                                                          billing_month__month=i)
        b_link_users = WebLinkInvoice.objects.filter(Q(web_link_user__username=user), billing_month__year=year,
                                                     billing_month__month=i)
        b_plug_users = PluginInvoice.objects.filter(Q(skigit_user__username=user), billing_month__year=year,
                                                    billing_month__lt=date)
        b_post_users = PostInvoice.objects.filter(Q(logo_user__username=user),
                                                  billing_month__month=i, billing_month__year=year)
        b_share_users = ShareInvoice.objects.filter(Q(skigit_user__username=user), billing_month__year=year,
                                                    billing_month__month=i)
        b_embed_users = EmbedInvoice.objects.filter(Q(user__username=user), billing_month__year=year,
                                                    billing_month__month=i)
        if b_logo_users:
            total_amount += b_logo_users[0].user_total_due
        if b_link_users:
            total_amount += b_link_users[0].link_total_due
        if b_plug_users:
            total_amount += b_plug_users[0].plugin_total_amount
        if b_post_users:
            total_amount += b_post_users[0].post_total_amount
        if b_share_users:
            total_amount += b_share_users[0].share_total_amount
        if b_embed_users:
            total_amount += b_embed_users[0].embed_total_amount
        payment_recived = InvoiceBilling.objects.filter(user_id=request.user,
                                                        payed_amount=total_amount, pay_yr=year, pay_mnth=i)

        billinglist.append({'month_num': i, 'payment_recived': payment_recived.exists(),
                            'transaction_id': payment_recived.first().transaction_id if payment_recived.exists() else None,
                            'transaction_date': payment_recived.first().created_date.strftime("%b %d %Y") if payment_recived.exists() else None ,
                            'card_type': payment_recived.first().invoice.type if payment_recived.exists() else None,
                            'card_img': payment_recived.first().invoice.c_image_url if payment_recived.exists() else None,
                            'inv':payment_recived.first().invoice if payment_recived.exists() else None,
                            'card_detail': str('%06d*****%04d') % (int(payment_recived.first().invoice.first_6),
                                                                   int(payment_recived.first().invoice.last_4))
                            if payment_recived.exists() and payment_recived.first().invoice.type == 'CreditCard' else
                            payment_recived.first().invoice.email if payment_recived.exists() else None})
        payment_info = {
            'current_month': datetime.datetime.now().month,
            'year': year,
            'month': month_list[i - 1],
            'month_num': i,
            'total_amount': total_amount,
            'logo_detail': b_logo_users.first(),
            'link_detail': b_link_users.first(),
            'plug_detail': b_plug_users.first(),
            'post_detail': b_post_users.first(),
            'share_detail': b_share_users.first(),
            'embed_detail': b_embed_users.first(),
            'card_type': card_type,
            'card_detail': card_detail,
            'card_img':  card_img,
            'inv': inv,
        }
        business_invoices_list.append(payment_info)
    business_invoices_list = sorted(business_invoices_list, key=itemgetter('month_num'), reverse=True)
    return render(request, 'profile/payment_invoices.html', locals())


@payment_required
def paybills(request):
    """
        Paying Bill Method.
    """
    response_data = {'is_success': False, 'message': 'Error into Paying bill, please contact administrator'}
    if request.method == 'POST' and request.is_ajax():
        invoice_id = request.POST.get('inv_id', None)
        inv = Invoice.objects.filter(id=invoice_id).first()
        if inv:
            amount = request.POST.get('amount', 0)
            month = request.POST.get('month', 0)
            year = request.POST.get('year', 0)
            card_type = request.POST.get('type', None)
            if InvoiceBilling.objects.filter(user_id=request.user, invoice=inv, pay_amount=amount,
                                             payed_amount=Decimal(amount), pay_yr=year, pay_mnth=month).exists():
                response_data = {'is_success': True, 'message': 'Payment already recived.'}
                return json_response(response_data)

            result = braintree.Transaction.sale({
                "amount": amount,
                "payment_method_token": inv.payment_method_token,
                "options": {
                    "submit_for_settlement": False,
                }
            })

            if result.is_success:

                pay_method = None
                if inv.type == 'PayPalAccount':
                    pay_method = '0'
                elif inv.type == 'CreditCard':
                    pay_method = '1'

                InvoiceBilling.objects.create(user_id=request.user, invoice=inv, pay_amount=amount,
                                              payed_amount=Decimal(result.transaction.amount), pay_yr=year,
                                              pay_mnth=month, transaction_id=result.transaction.id,
                                              pay_method=pay_method, payment_status=True,
                                              created_date=datetime.datetime.now())

                response_data['is_success'] = True
                response_data['message'] = '$%s amount is received.' % Decimal(result.transaction.amount)
                response_data['transaction_id'] = result.transaction.id
                response_data['transaction_date'] = datetime.datetime.now().strftime("%b %d %Y")
            else:
                response_data['is_success'] = False
                for error in result.errors.deep_errors:
                    response_data['message'] = error.message
                    response_data['code'] = error.code
                    response_data['attribute'] = error.attribute
        else:
            response_data['is_success'] = False
            response_data['message'] = ''
    return json_response(response_data)
