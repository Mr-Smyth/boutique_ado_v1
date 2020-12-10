from django.shortcuts import (
    render, redirect, reverse, get_object_or_404, HttpResponse
)
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.conf import settings

from .forms import OrderForm
from .models import Order, OrderLineItem
from products.models import Product
from bag.contexts import bag_contents

import stripe
import json


@require_POST
def cache_checkout_data(request):
    """
    What's gonna happen here is before we call the confirm card payment method
    in the stripe JavaScrip. we'll make a post request to this view and give
    it the client secret from the payment intent. If we split that at the word
    secret the first part of it will be the payment intent Id, so I'll store
    that in a variable called pid.
    Then I'll set up stripe with the secret key so we can modify the payment
    intent. To do it all we have to do is call stripe.PaymentIntent.modify
    give it the pid, and tell it what we want to modify in our case we'll add
    some metadata.

     """
    try:
        pid = request.POST.get('client_secret').split('_secret')[0]
        stripe.api_key = settings.STRIPE_SECRET_KEY
        stripe.PaymentIntent.modify(pid, metadata={
            'bag': json.dumps(request.session.get('bag', {})),
            'save_info': request.POST.get('save_info'),
            'username': request.user,
        })
        return HttpResponse(status=200)
    except Exception as e:
        messages.error(request, ('Sorry, your payment cannot be '
                                 'processed right now. Please try '
                                 'again later.'))
        return HttpResponse(content=e, status=400)


def checkout(request):

    # create variables for the public and secret keys
    stripe_public_key = settings.STRIPE_PUBLIC_KEY
    stripe_secret_key = settings.STRIPE_SECRET_KEY

    # Handle POST from checkout form
    if request.method == 'POST':
        # get the shopping bag
        bag = request.session.get('bag', {})

        # put the form data into a dictionary
        # this is because of no save info button on the form, but we can save
        # the info from the form inside form_data
        form_data = {
            'full_name': request.POST['full_name'],
            'email': request.POST['email'],
            'phone_number': request.POST['phone_number'],
            'country': request.POST['country'],
            'postcode': request.POST['postcode'],
            'town_or_city': request.POST['town_or_city'],
            'street_address1': request.POST['street_address1'],
            'street_address2': request.POST['street_address2'],
            'county': request.POST['county'],
        }

        # create an order_form  and pass it into our OrderForm from .forms
        order_form = OrderForm(form_data)

        # if the order is valid
        if order_form.is_valid():
            # save the order
            # prevent multiple save events from being executed on the database by adding (commit=False)
            order = order_form.save(commit=False)

            # update the view to add the extra 2 fields that deal with
            # duplicating orders, when the form is submitted
            # here we are getting the client_secret back from the hidden
            # element in the checkout.html
            pid = request.POST.get('client_secret').split('_secret')[0]
            order.stripe_pid = pid
            # we already have the shopping bag here ??????????
            # so adding that to the model is simple
            # dump it to a JSON string
            # and set it on the order (prefix.order)
            order.original_bag = json.dumps(bag)
            # save the order
            order.save()

            # Now iterate over the bag items, to create each line item of the
            # order
            for item_id, item_data in bag.items():
                try:
                    # first get the product id out of the bag
                    product = Product.objects.get(id=item_id)
                    # if the id is an integer then we know we are working
                    # with an item that does not have sizes - so the quantity
                    # below will just be the item data
                    if isinstance(item_data, int):
                        order_line_item = OrderLineItem(
                            order=order,
                            product=product,
                            quantity=item_data,
                        )
                        order_line_item.save()

                    # Otherwise if the item has sizes
                    else:
                        # we will iterate through each size and create a line
                        # item accordingly
                        for size, quantity in item_data['items_by_size'].items(
                        ):
                            order_line_item = OrderLineItem(
                                order=order,
                                product=product,
                                quantity=quantity,
                                product_size=size,
                            )
                            order_line_item.save()
                # finally in the weird case that item isnt found
                except Product.DoesNotExist:
                    # add an error message
                    messages.error(request, (
                        "One of the products in your bag wasn't "
                        "found in our database. "
                        "Please call us for assistance!")
                    )
                    # delete the empty order
                    order.delete()
                    # return the user to the shopping bag
                    return redirect(reverse('view_bag'))

            # Save the info to the user's profile if all is well
            request.session['save_info'] = 'save-info' in request.POST
            return redirect(reverse('checkout_success',
                                    args=[order.order_number]))
        else:
            messages.error(request, ('There was an error with your form. '
                                     'Please double check your information.'))
    # Handle GET
    else:
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
        # •	multiply the total x 100 and round it to 0  decimal places using
        # the round function - this is because stripe will require the
        # amount to charge as an integer
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

        # END OF GET HANDLER ------

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


def checkout_success(request, order_number):
    """
    Handle successful checkouts
    """

    # check to see if user wanted to save their information by getting that
    # from the session just like we get the shopping bag - this will be needed
    # later for whaen we create profiles
    save_info = request.session.get('save_info')

    # use the order number to get the order created in the previous view -
    # which we will send back to the template
    order = get_object_or_404(Order, order_number=order_number)
    # then create a success message to let the user know everything worked
    # and that we will send an email
    messages.success(request, f'Order successfully processed! \
        Your order number is {order_number}. A confirmation \
        email will be sent to {order.email}.')

    # then delete the users shopping bag from the session, as it will no longer
    # be needed for this session
    if 'bag' in request.session:
        del request.session['bag']

    # set template and context
    template = 'checkout/checkout_success.html'
    context = {
        'order': order,
    }
    # render the template
    return render(request, template, context)
