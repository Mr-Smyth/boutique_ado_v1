# Used to import the order number
import uuid

from django.db import models
from django.db.models import Sum
from django.conf import settings

from products.models import Product


# required fields
class Order(models.Model):
    # make sure the order number cannot be edited (editable = False)
    order_number = models.CharField(max_length=32, null=False, editable=False)
    full_name = models.CharField(max_length=50, null=False, blank=False)
    email = models.EmailField(max_length=254, null=False, blank=False)
    phone_number = models.CharField(max_length=20, null=False, blank=False)
    country = models.CharField(max_length=40, null=False, blank=False)
    postcode = models.CharField(max_length=20, null=True, blank=True)
    town_or_city = models.CharField(max_length=40, null=False, blank=False)
    street_address1 = models.CharField(max_length=80, null=False, blank=False)
    street_address2 = models.CharField(max_length=80, null=True, blank=True)
    county = models.CharField(max_length=80, null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)
    delivery_cost = models.DecimalField(max_digits=6, decimal_places=2, null=False, default=0)
    order_total = models.DecimalField(max_digits=10, decimal_places=2, null=False, default=0)
    grand_total = models.DecimalField(max_digits=10, decimal_places=2, null=False, default=0)
    # these two fields cope with the event where a shopper buys the same on
    # more than one occaision
    # this will be a text field that will contain the original shopping bag
    # that created it
    original_bag = models.TextField(null=False, blank=False, default='')
    # the payment intent Id is guaranteed to be unique
    stripe_pid = models.CharField(max_length=254, null=False, blank=False, default='')

    def _generate_order_number(self):
        """
        Generate a random, unique order number using UUID
        """
        return uuid.uuid4().hex.upper()

    def update_total(self):
        """
        Update grand total each time a line item is added,
        accounting for delivery costs.
        """
        # use the sub method inside the aggregate function accross all the
        # line item totals of this order
        # the default behaviour is to add a new field to the query set called
        # lineitem_total__sum, which we can then get, then set the order
        # total to that
        self.order_total = self.lineitems.aggregate(Sum('lineitem_total'))['lineitem_total__sum'] or 0
        # calculate the delivery charge
        if self.order_total < settings.FREE_DELIVERY_THRESHOLD:
            self.delivery_cost = self.order_total * settings.STANDARD_DELIVERY_PERCENTAGE / 100
        else:
            # delivery is €0, if over threshold
            self.delivery_cost = 0
        self.grand_total = self.order_total + self.delivery_cost
        self.save()

    # override the default save method
    def save(self, *args, **kwargs):
        """
        Override the original save method to set the order number
        if it hasn't been set already.
        """
        # if we do not yet have an order number
        if not self.order_number:
            # call the generate order number method above
            self.order_number = self._generate_order_number()
        # execute original save method
        super().save(*args, **kwargs)

    # add the standard string method, returning just the order number for the
    # order model.
    def __str__(self):
        return self.order_number

# this will be the fields for a single order - referencing the particular
# items in that order

# when a user checks out
# first use the info they put into the payment form to create an order instance
# Then we will iterate through the items in the shopping bag
# Creating an order line item for each one
# attaching it to the order
# updating the delivery cost, order total and grand total in order - above


class OrderLineItem(models.Model):
    # order will be a foreign key in the Order model - above.
    # It will use a related name so we can refer to it like
    # order.lineitems.all or .filter
    order = models.ForeignKey(Order, null=False, blank=False, on_delete=models.CASCADE, related_name='lineitems')
    # product will also be a forign key for the Order model above - so we can
    # access all the associated product line items
    product = models.ForeignKey(Product, null=False, blank=False, on_delete=models.CASCADE)
    # product_size - can be null and blank as some products have no sizes
    product_size = models.CharField(max_length=2, null=True, blank=True) # XS, S, M, L, XL
    quantity = models.IntegerField(null=False, blank=False, default=0)
    # make not editable!
    lineitem_total = models.DecimalField(max_digits=6, decimal_places=2, null=False, blank=False, editable=False)

    def save(self, *args, **kwargs):
        """
        Override the original save method to set the lineitem total
        and update the order total.
        """
        self.lineitem_total = self.product.price * self.quantity
        super().save(*args, **kwargs)

    # in the sku of the product, along with the order its part of,  for each
    # order line item
    def __str__(self):
        return f'SKU {self.product.sku} on order {self.order.order_number}'
