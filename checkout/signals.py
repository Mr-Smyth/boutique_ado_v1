# import post_save and post_delete to handle actions after these events
from django.db.models.signals import post_save, post_delete
# receiver allows receiving of these signals
from django.dispatch import receiver

# we will need the orderLineItem Model as we will be listening for signals
# from there
from .models import OrderLineItem


# use receiver decorator to activate this fuction each time a post_save signal
# is sent
@receiver(post_save, sender=OrderLineItem)
def update_on_save(sender, instance, created, **kwargs):
    """
    Update order total on lineitem update/create

    Now the plan is that we iterate over the shopping bag and add each item to
    the checkout – updating the totals along the way. We have the method to
    update the total already in the models.py (update_total). We just need a
    way to call it each time a product is added to the order.

    To accomplish this we can use a built in feature called signals.

    sender: orderLineItem
    instance: the instance of the model that sent it
    created: a boolean to indicate if its a new instance or one being updated
    **kwargs: key word arguments

    """
    # instance.order refers to the order this specific line is related to
    # And call the update total method on it
    instance.order.update_total()


# To handle when something is deleted - basically same as above
@receiver(post_delete, sender=OrderLineItem)
def update_on_delete(sender, instance, **kwargs):
    """
    Update order total on lineitem delete
    """
    instance.order.update_total()
