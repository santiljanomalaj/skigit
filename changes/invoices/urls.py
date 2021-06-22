
from django.conf.urls import url
from invoices.views import *

urlpatterns = [
    url(r'^business-logo/$', business_logo_invoice, name='business_logo_invoice'),
    url(r'^web-link/$', business_weblink_invoice, name='business_web_link_invoice'),
    url(r'^post-social-network/$', business_post_invoice, name='business_post_invoice'),
    url(r'^external-embed-invoice/$', business_embed_invoice, name='business_embed_invoice'),
    url(r'^c-c-nonce/$', customer_create, name='customer_create_view'),
    url(r'^pay-pal-nonce/$', pay_pal_customer_create, name='customer_create_view'),
    url(r'^payment-method-remove/$', payment_method_remove, name='payment_method_remove'),
    url(r'^paypal-form/$', paypal_form, name='paypal_form'),
    url(r'^payment-invoice/$', payment_invoice, name='payment_invoice'),
    url(r'^pay-bill/$', paybills, name='pay_bill'),
]
