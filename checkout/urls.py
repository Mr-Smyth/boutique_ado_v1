from django.urls import path
from . import views
# the webhooks function will live in a file called webhooks.py so we will
# import the webhooks function from .webhooks

from .webhooks import webhook

urlpatterns = [
    path('', views.checkout, name='checkout'),
    # Take the order number as an argument from views.checkout_success
    path('checkout_success/<order_number>', views.checkout_success, name='checkout_success'),
    path('wh/', webhook, name='webhook'),
]