from django.shortcuts import render
from .models import Product

# Create your views here.


def all_products(request):
    """ A View to show all products also will Sort and Search Queries """

    # Get all the products
    products = Product.objects.all()

    # Put the products into the context
    context = {
        'products': products,
    }

    return render(request, 'products/products.html', context)
