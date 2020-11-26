from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.contrib import messages
from django.db.models import Q  # generates a search query
from .models import Product

# Create your views here.


def all_products(request):
    """ A View to show all products also will Sort and Search Queries """

    # Set a default for query in case page loaded without a search
    query = None

    # Get all the products
    products = Product.objects.all()

    if request.GET:
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

    # Put the products into the context
    context = {
        'products': products,
        # return the search term for displaying
        'search_term': query,
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
