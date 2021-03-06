from decimal import Decimal
from django.conf import settings
from django.shortcuts import get_object_or_404
from products.models import Product

def bag_contents(request):

    # some req variables
    bag_items = []
    total = 0
    product_count = 0
    # get the bag variable in session storage, or inializing it to an
    # empty dictionary if it doesnt already exist
    bag = request.session.get('bag', {})

    # iterate over the items in the bag in session storage
    for item_id, item_data in bag.items():
        # if the item_data is an int - then its the quantity
        if isinstance(item_data, int):
            # get the product
            product = get_object_or_404(Product, pk=item_id)
            # get the quantity * price and add it to the total variable
            total += item_data * product.price
            # Increment the product count by the quantity
            product_count += item_data
            # append the items id, quntity chosen and the complete product
            # object this will be habndy for accessing any elements of the
            # product such as the image
            bag_items.append({
                'item_id': item_id,
                'quantity': item_data,
                'product': product,
            })
        else:
            # then its the size/qty dict - loop over it
            product = get_object_or_404(Product, pk=item_id)
            for size, quantity in item_data['items_by_size'].items():
                total += quantity * product.price
                product_count += quantity
                bag_items.append({
                    'item_id': item_id,
                    'quantity': quantity,
                    'product': product,
                    'size': size,
                })

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
