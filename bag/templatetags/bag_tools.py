from django import template

# register this filter
register = template.Library()

# register filter as a template filter
@register.filter(name='calc_subtotal')
def calc_subtotal(price, quantity):
    """ takes in a price and qty and returns their product """
    return price * quantity
