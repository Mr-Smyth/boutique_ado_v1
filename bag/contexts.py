from decimal import Decimal
from django.conf import settings


def bag_contents(request):

    # some req variables
    bag_items = []
    total = 0
    product_count = 0

    # Give customer free delivery if over threshold
    # Use decimal when working with money, as its more accurate
    # float is susceptible to rounding errors
    if total < settings.FREE_DELIVERY_THRESHOLD:
        delivery = total * Decimal(settings.STANDARD_DELIVERY_PERCENTAGE / 100)
        free_delivery_delta = settings.FREE_DELIVERY_THRESHOLD - total
    else:
        delivery = 0
        free_delivery_delta = 0

    grand_total = delivery + total

    # Dictionary that we will return accross site
    context = {
        'bag_items': bag_items,
        'total': total,
        'product_count': product_count,
        'delivery': delivery,
        'free_delivery_delta': free_delivery_delta,
        'free_delivery_threshold': settings.FREE_DELIVERY_THRESHOLD,
        'grand_total': grand_total,
    }

    return context
