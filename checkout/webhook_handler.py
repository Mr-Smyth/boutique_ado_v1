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
            content=f'Webhook received: {event["type"]}',
            status=200)
