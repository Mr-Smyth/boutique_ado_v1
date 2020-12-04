from django.shortcuts import render, redirect, reverse, HttpResponse


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
    # Handle size
    size = None
    if 'product_size' in request.POST:
        size = request.POST['product_size']
    # get the bag variable in session storage, or inializing it to an
    # empty dictionary if it doesnt already exist
    bag = request.session.get('bag', {})

    # change structure of bag to handle sizes
    if size:
        # if the item id is in the bag already
        if item_id in list(bag.keys()):
            # if the item is in the bag and the item has the same size as the
            # one we are adding
            if size in bag[item_id]['items_by_size'].keys():
                # then just increment the quantity
                bag[item_id]['items_by_size'][size] += quantity
            # else just grab the size and set the quantity
            else:
                bag[item_id]['items_by_size'][size] = quantity
        else:
            bag[item_id] = {'items_by_size': {size: quantity}}
    else:
        # now we have a bag object(dict), we can stuff the item_id into it
        # if the item is in the bag already - increment the qty for the item
        if item_id in list(bag.keys()):
            bag[item_id] += quantity
        # else add the item to the bag as a key and set the quantity as its
        # value
        else:
            bag[item_id] = quantity

    # put the bag variable into the session, which itself is just a python
    # dictionary
    request.session['bag'] = bag
    print(request.session['bag'])
    return redirect(redirect_url)


def adjust_bag(request, item_id):
    """ Adjust the quantities of a specified product in the shopping bag """

    # get the qty from the form
    quantity = int(request.POST.get('quantity'))
    # Handle size
    size = None
    if 'product_size' in request.POST:
        size = request.POST['product_size']
    # get the bag variable in session storage, or inializing it to an
    # empty dictionary if it doesnt already exist
    bag = request.session.get('bag', {})

    # This is coming from a form on the shopping bag page which will contain
    # the new quantity the user wants in the bag. So the plan is that if the
    # quantity is > 0 we will want to set the quantity accordingly.
    # Otherwise we will just remove the item
    if size:
        if quantity > 0:
            # drill into the bag - item_id - items by size dictionary and set
            # the size equal to the quantity, this is because in this
            # dictionary we keep track of quantity by size of a product
            bag[item_id]['items_by_size'][size] = quantity
        else:
            # then the quantity is 0 - delete the item
            del bag[item_id]['items_by_size'][size]
            # if thats the only size they had - delete the whole item too
            if not bag[item_id]['items_by_size']:
                bag.pop(item_id)

        # if there is no size - remove entirely using pop
    else:
        if quantity > 0:
            bag[item_id] = quantity
        else:
            # then the quantity is 0 - delete the item
            bag.pop(item_id)

    # put the bag variable into the session, which itself is just a python
    # dictionary
    request.session['bag'] = bag
    # redirect back to the shopping bag - use reverse
    return redirect(reverse('view_bag'))


def remove_from_bag(request, item_id):
    """ Remove the item from the shopping bag """

    # wrap in a try and return any exceptions in e
    try:
        # Handle size
        size = None

        if 'product_size' in request.POST:
            size = request.POST['product_size']
        # get the bag variable in session storage, or inializing it to an
        # empty dictionary if it doesnt already exist
        bag = request.session.get('bag', {})

        # If the user is removing a size, then we only want to remove only that
        # size
        if size:
            # then delete that size
            del bag[item_id]['items_by_size'][size]
            print("Ive just deleted a size")
            # if thats the only size they had - delete the whole item too
            if not bag[item_id]['items_by_size']:
                bag.pop(item_id)

        # if there is no size - remove entirely using pop
        else:
            bag.pop(item_id)

        # put the bag variable into the session, which itself is just a python
        # dictionary
        request.session['bag'] = bag
        # return a 200 respose to indicate success
        return HttpResponse(status=200)
    except Exception as e:
        return HttpResponse(status=500)
