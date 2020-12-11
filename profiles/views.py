from django.shortcuts import render, get_object_or_404
from django.contrib import messages

from .models import UserProfile
from .forms import UserProfileForm


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
