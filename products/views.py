from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.contrib import messages
from django.db.models import Q  # generates a search query
from .models import Product, Category

# Create your views here.


def all_products(request):
    """ A View to show all products also will Sort and Search Queries """

    # Set a default for query and category in case page loaded without a search
    query = None
    categories = None
    # Set sort and direction to none for case when not used
    sort = None
    direction = None

    # Get all the products
    products = Product.objects.all()
    # Get all the categories
    all_categories = Category.objects.all()

    if request.GET:
        # Handle to sort
        if 'sort' in request.GET:
            sortkey = request.GET['sort']  # Create the sortkey variable
            # Make a copy of it and call it sort, which we'll use later to
            # construct current_sorting = f'{sort}_{direction}
            sort = sortkey
            # If the field we want to sort on is 'name'
            if sortkey == 'name':
                # Let's actually sort (i.e. order_by) on one called
                # 'lower_name', in order to ensure it doesn't order
                # Z before a just because the Z is uppercase
                sortkey = 'lower_name'
                # Annotate all the products w/ a new field,
                # lower_name=Lower('name') and sort based on it
                products = products.annotate(lower_name=Lower('name'))

            # here we set the category to order by category name
            if sortkey == 'category':
                sortkey = 'category__name'

            if 'direction' in request.GET:
                direction = request.GET['direction']
                if direction == 'desc':
                    sortkey = f'-{sortkey}'

            # Here we tell the template how to order the products
            # --> this becomes products.order_by('whatever the value of
            # sortkey is')
            products = products.order_by(sortkey)

        # Check for category in GET
        if 'category' in request.GET:
            # if it is, split it into commas
            categories = request.GET['category'].split(',')
            # use categories list to filter the products down to only products
            # with a category name in the categories list
            products = products.filter(category__name__in=categories)
            # also we will get the categories so we can display which category
            # has been selected by the user. We need to import category for
            # this though, setup a variable above
            # So which category is in the categories list.
            categories = all_categories.filter(name__in=categories)


        if 'q' in request.GET:
            query = request.GET['q']
            # If the query is blank
            if not query:
                messages.error(request, 'You didnt enter any search criteria!')
                return redirect(reverse('products'))
            #  Import Q to use the of functionality
            #  Also the i makes the query case insensitive
            queries = Q(name__icontains=query) | Q(description__icontains=query)
            # Pass the query to the filter method to get results.
            products = products.filter(queries)

    # if no sorting has been selected this will return None_None
    current_sorting = f'{sort}_{direction}'

    # Put the products into the context
    context = {
        'products': products,
        # return the search term for displaying
        'search_term': query,
        # return a list of chosen categories
        'current_categories': categories,
        # if no sorting has been selected this will return None_None
        'current_sorting': current_sorting,

    }
    return render(request, 'products/products.html', context)


def product_detail(request, product_id):
    """ A View to return a products' details """

    # Get all the products
    product = get_object_or_404(Product, pk=product_id)

    # Put the products into the context
    context = {
        'product': product,
    }

    return render(request, 'products/product_detail.html', context)
