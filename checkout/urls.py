from django.urls import path
from . import views

urlpatterns = [
    path('', views.checkout, name='checkout'),
    # Take the order number as an argument from views.checkout_success
    path('checkout_success/<order_number>',
         views.checkout_success, name='checkout_success'),
]