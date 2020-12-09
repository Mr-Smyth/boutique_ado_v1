# so we can provide a http response
from django.http import HttpResponse


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
        print(intent)

        return HttpResponse(
            content=(f'Webhook received: {event["type"]} | SUCCESS: '
                     'Created order in webhook'),
            status=200)

    def handle_payment_intent_payment_failed(self, event):
        """
        Handle the payment_intent.payment_failed webhook from Stripe
        """
        return HttpResponse(
            content=f'Webhook received: {event["type"]}',
            status=200)
