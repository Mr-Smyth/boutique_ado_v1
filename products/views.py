from django.shortcuts import render, get_object_or_404
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


def product_detail(request, product_id):
    """ A View to return a products' details """

    # Get all the products
    product = get_object_or_404(Product, pk=product_id)

    # Put the products into the context
    context = {
        'product': product,
    }

    return render(request, 'products/product_detail.html', context)
