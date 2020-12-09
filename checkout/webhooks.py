# need settings to get the webhook and the strip API secrets
from django.conf import settings
# needed so the exception handlers will work
from django.http import HttpResponse

# we need 2 decorators
# This makes the view require a POST and reject GET Requests
from django.views.decorators.http import require_POST
# csrf_exempt - because stripe will not send a csrf token like we would
# normally need
from django.views.decorators.csrf import csrf_exempt

# we need our webhook handler class
from checkout.webhook_handler import StripeWH_Handler

# we need stripe
import stripe


@require_POST
@csrf_exempt
def webhook(request):
    """Listen for webhooks from Stripe
    
    This is the webhook function that will take in a request

    The code here comes directly from stripe with some modifications.
    
    """
    # Setup
    # Setup the webhook secret, which we will use to verify that the webhook
    # actually came from stripe
    wh_secret = settings.STRIPE_WH_SECRET
    # setup  the stripe API Key
    stripe.api_key = settings.STRIPE_SECRET_KEY

    # Get the webhook data and verify its signature
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, wh_secret
        )
    except ValueError as e:
        # Invalid payload
        return HttpResponse(content=e, status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return HttpResponse(content=e, status=400)
    # A generic exception - to catch any exceptions other than the 2 stripe
    # has provided
    except Exception as e:
        return HttpResponse(content=e, status=400)

    # Set up a webhook handler by creating an instance of it and passing in
    # the request
    handler = StripeWH_Handler(request)

    # Map webhook events to relevant handler functions by creating a dictionary
    # called event map
    # the keys are the names of the webhooks coming from stripe
    # its values will be the actual methods inside the handler
    event_map = {
        'payment_intent.succeeded': handler.handle_payment_intent_succeeded,
        'payment_intent.payment_failed': handler.handle_payment_intent_payment_failed,
    }

    # Get the webhook type from Stripe - so this could be
    # payment_intent.succeeded or similar - and store it in the variable
    # event_type
    event_type = event['type']

    # find the correct handler by looking for a matching key for event_type
    # inside the event_map dictionary above. when a match is found assign its
    # value - the handler - to the event_handler variable
    # Use the generic one by default
    event_handler = event_map.get(event_type, handler.handle_event)

    # so at this point event_handler is nothing more than an alias for
    # whatever function we have pulled out of the event_map dictionary

    # Call the event handler with the event
    response = event_handler(event)
    return response
