from django.shortcuts import render, redirect, reverse
from django.contrib import messages

from .forms import OrderForm


def checkout(request):

    # firstly get the bag from the session
    bag = request.session.get('bag', {})
    if not bag:
        # if there is nothing in the bag - add an error message
        messages.error(request, "There's nothing in your bag at the moment")
        # redirect back to the products page
        return redirect(reverse('products'))

    # create a new instance of our order form (forms.py)
    order_form = OrderForm()

    # create the template
    template = 'checkout/checkout.html'

    # create the context creating the order form
    context = {
        'order_form': order_form,
    }

    # render the whole lot out
    return render(request, template, context)
