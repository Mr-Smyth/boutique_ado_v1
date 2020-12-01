from django.shortcuts import render, redirect


def view_bag(request):
    """ A view that renders the bag contents page """

    return render(request, 'bag/bag.html')


def add_to_bag(request, item_id):
    """ Add a quantity of the specified product to the shopping bag """

    # get the qty from the form
    # we need to convert it to an int, as it will come from the form as a
    # string
    quantity = int(request.POST.get('quantity'))
    # Get the redirect url from the form so we know where to redirect to
    # once the form has been submitted
    redirect_url = request.POST.get('redirect_url')
    # get the bag variable in session storage, or inializing it to an
    # empty dictionary if it doesnt already exist
    bag = request.session.get('bag', {})

    # now we have a bag object(dict), we can stuff the item_id into it
    # if the item is in the bag already - increment the qty for the item
    if item_id in list(bag.keys()):
        bag[item_id] += quantity
    # else add the item to the bag as a key and set the quantity as its value
    else:
        bag[item_id] = quantity

    # put the bag variable into the session, which itself is just a python
    # dictionary
    request.session['bag'] = bag
    print(request.session['bag'])
    return redirect(redirect_url)
