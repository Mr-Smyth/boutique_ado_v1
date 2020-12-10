# so we can provide a http response
from django.http import HttpResponse

from .models import Order, OrderLineItem
from products.models import Product

import json
import time


class StripeWH_Handler:
    """Handle Stripe webhooks"""

    # __init__ method is a setup method that is called everytime an instance
    # of the class is created
    def __init__(self, request):
        # assign the request as an attribute of the class, just in case we
        # need to access any of the attributes of the request coming from
        # stripe
        self.request = request

    def handle_event(self, event):
        """
        Handle a generic/unknown/unexpected webhook event

        Takes the event stripe is sending us and returns a http response -
        indicating that it was received
        """
        return HttpResponse(
            content=f'Unhandled Webhook received: {event["type"]}',
            status=200)

    def handle_payment_intent_succeeded(self, event):
        """
        Handle the payment_intent.succeeded webhook from Stripe
        """
        # the payment intent will be saved in a key called event.data.object
        # event being the event passed into the method
        intent = event.data.object

        # Now handle the situation where something goes wrong when the user
        # submits and the order does not get stored in the DB
        # We need to use the data returned inside the intent to create a form
        # and submit it as an order

        # lets get the payment id, the shopping bag and the users save info
        # preference from the metadata we added to the intent in the last
        # part
        pid = intent.id
        bag = intent.metadata.bag
        save_info = intent.metadata.save_info

        # also get the billing, shipping and grandtotal
        billing_details = intent.charges.data[0].billing_details
        shipping_details = intent.shipping
        grand_total = round(intent.charges.data[0].amount / 100, 2)

        # Clean data in the shipping details - this is to ensure the data is
        # in the same format as we want for our database - we will replace any
        # empty strings in the shipping details as None since stripe will store
        # them as blank strings - which is not the same as the null value we
        # want in the database
        for field, value in shipping_details.address.items():
            if value == "":
                shipping_details.address[field] = None

        # Most of the time when a user checks out, everything will go well and
        # the form will be submitted so the order should already be in our
        # database when we receive this webhook. The first thing then is to
        # check if the order exists already.

        # first lets assume the order does NOT exist
        order_exists = False

        # so we will attempt to get the order using the info in the patment
        # intent
        # create a variable called attempt = 1
        attempt = 1
        while attempt <= 5:
            try:
                # try to get the order - using the information in the payment
                # intent
                # use iexact field to get an exact match but case-insensitive
                order = Order.objects.get(
                    full_name__iexact=shipping_details.name,
                    # email only exists in billing details - so look there
                    email__iexact=billing_details.email,
                    phone_number__iexact=shipping_details.phone,
                    # should be inside an address key - see stripe_elements.js
                    country__iexact=shipping_details.address.country,
                    # should be inside an address key - see stripe_elements.js
                    postcode__iexact=shipping_details.address.postal_code,
                    # should be inside an address key - see stripe_elements.js
                    town_or_city__iexact=shipping_details.address.city,
                    # should be inside an address key - see stripe_elements.js
                    street_address1__iexact=shipping_details.address.line1,
                    # should be inside an address key - see stripe_elements.js
                    street_address2__iexact=shipping_details.address.line2,
                    # should be inside an address key - see stripe_elements.js
                    county__iexact=shipping_details.address.state,
                    # should be inside an address key - see stripe_elements.js
                    grand_total=grand_total,
                    original_bag=bag,
                    stripe_pid=pid,
                )

                # if the order is found - order-exists becomes True
                order_exists = True
                break
            # if the order is not found the try will break out into this
            # exception
            # this means that if any of the above exact fields are not found
            # the try will fail.
            except Order.DoesNotExist:
                # order_exists will remain false
                # attempt will increase to 2
                # use pythons time module to sleep for 1 second
                # then try again
                # in essence this will cause the webhook_handler to try 5
                # times over 5 seconds to search for the order - if no order
                # is present then it will break out of the while loop and
                # carry onto create the order
                attempt += 1
                time.sleep(1)

        if order_exists:
            # if the order is found - we will set order exists to True and
            # return a 200 response to stripe with a message that we have
            # verified the order already exists
            return HttpResponse(
                content=f'Webhook received: {event["type"]} | SUCCESS: Verified order already in database',
                status=200)
        else:
            # if the order does not exist then we will create it here in the
            # webhook
            order = None
            try:
                # we dont have a form to save in this webhook to create the
                # order - but we can do it hust as easily
                # with Order.objects.create() using all the data in the
                # payment intent - as it came from the form originally anyway
                order = Order.objects.create(
                    full_name=shipping_details.name,
                    email=billing_details.email,
                    phone_number=shipping_details.phone,
                    country=shipping_details.address.country,
                    postcode=shipping_details.address.postal_code,
                    town_or_city=shipping_details.address.city,
                    street_address1=shipping_details.address.line1,
                    street_address2=shipping_details.address.line2,
                    county=shipping_details.address.state,
                    original_bag=bag,
                    stripe_pid=pid,
                )
                # we still need to iterate through the bag, but this time we
                # will be getting the bag from the JSON data instead of
                # from the session
                for item_id, item_data in json.loads(bag).items():
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
                        for size, quantity in item_data['items_by_size'].items():
                            order_line_item = OrderLineItem(
                                order=order,
                                product=product,
                                quantity=quantity,
                                product_size=size,
                            )
                            order_line_item.save()
            # if anything goes wrong when creating the order in the above try
            # block - we will just delete the order if it was created and
            # return a 500 server error response to stripe - which will
            # automatically cause stripe to try again later
            except Exception as e:
                if order:
                    order.delete()
                return HttpResponse(
                    content=f'Webhook received: {event["type"]} | ERROR: {e}',
                    status=500)
        # if we get to this stage in the code - we know that it was successful,
        # so we should return a message to stripe indicating that
        return HttpResponse(
            content=f'Webhook received: {event["type"]} | SUCCESS: Created order in webhook',
            status=200)

    def handle_payment_intent_payment_failed(self, event):
        """
        Handle the payment_intent.payment_failed webhook from Stripe
        """
        return HttpResponse(
            content=f'Webhook received: {event["type"]}',
            status=200)
