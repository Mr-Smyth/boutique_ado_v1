from django.shortcuts import render, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import UserProfile
from .forms import UserProfileForm

from checkout.models import Order


def profile(request):
    """ Display the user's profile. """

    profile = get_object_or_404(UserProfile, user=request.user)

    if request.method == 'POST':
        # Create a new instance of the user profile form using the post data
        # and tell it the instance we're updating is the profile we've just
        # retrieved above.
        form = UserProfileForm(request.POST, instance=profile)

        # Then if the form is valid.
        if form.is_valid():
            # We save it
            form.save()
            # add a success message (so import messages!)
            messages.success(request, 'Profile updated successfully')
        else:
            # in the case where the form is not valid
            messages.error(request,
                           ('Update failed. Please ensure '
                            'the form is valid.'))

    # populate with users profile info
    form = UserProfileForm(instance=profile)

    # get the users orders - use the profile and the related name on the order
    # model to get the users orders and return them to the template
    orders = profile.orders.all()

    template = 'profiles/profile.html'
    context = {
        'form': form,
        'orders': orders,
        'on_profile_page': True,
    }

    return render(request, template, context)


def order_history(request, order_number):
    # get the order - so import order model at the top
    order = get_object_or_404(Order, order_number=order_number)

    # add a message
    messages.info(request, (
        f'This is a past confirmation for order number {order_number}. '
        'A confirmation email was sent on the order date.'
    ))

    # give it a template - use the checkout success template since that
    # template already has the layout for rendering a nice order confirmation
    template = 'checkout/checkout_success.html'

    # we will use the from_profile variable so that we can check how the user
    # got there - in this case its from the profile
    context = {
        'order': order,
        'from_profile': True,
    }

    return render(request, template, context)
