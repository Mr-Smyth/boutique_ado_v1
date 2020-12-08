from django.shortcuts import render, redirect, reverse
from django.contrib import messages
from django.conf import settings

from .forms import OrderForm
from bag.contexts import bag_contents

import stripe


def checkout(request):

    # create variables for the public and secret keys
    stripe_public_key = settings.STRIPE_PUBLIC_KEY
    stripe_secret_key = settings.STRIPE_SECRET_KEY

    # firstly get the bag from the session
    bag = request.session.get('bag', {})
    if not bag:
        # if there is nothing in the bag - add an error message
        messages.error(request, "There's nothing in your bag at the moment")
        # redirect back to the products page
        return redirect(reverse('products'))

    # get the current bags contents using our bag_contents function
    current_bag = bag_contents(request)
    # get the grand total from our current_bag
    total = current_bag['grand_total']
    # •	multiply the total x 100 and round it to 0  decimal places using the
    # round function - this is because stripe will require the amount to
    # charge as an integer
    stripe_total = round(total * 100)

    # set the secret key on stripe
    stripe.api_key = stripe_secret_key
    # setup the payment intent - give it the amount and the currency
    intent = stripe.PaymentIntent.create(
        amount=stripe_total,
        currency=settings.STRIPE_CURRENCY,
    )

    print(intent)

    # create a new instance of our order form (forms.py)
    order_form = OrderForm()

    # Create a reminder in case we forget to set our public key
    if not stripe_public_key:
        messages.warning(request, ('Stripe public key is missing. '
                                   'Did you forget to set it in '
                                   'your environment?'))

    # create the template
    template = 'checkout/checkout.html'

    # create the context creating the order form
    context = {
        'order_form': order_form,
        'stripe_public_key': stripe_public_key,
        'client_secret': intent.client_secret,
    }

    # render the whole lot out
    return render(request, template, context)
