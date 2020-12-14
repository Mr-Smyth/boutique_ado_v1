from django.urls import path
from . import views

urlpatterns = [
    path('', views.all_products, name='products'),
    # We'll need to update the product detail URL slightly to specify that
    # the product ID should be an integer. Since otherwise navigating to
    # products /add will interpret the string add as a product id. Which will
    # cause that view to throw an error. This happens because django will
    # always use the first URL it finds a matching pattern for. And in this
    # case unless we specify that product id is an integer django doesn't know
    # the difference between a product number and a string like, add. I'll
    # also add a trailing slash here as that's just good practice and I've
    # accidentally left it off.
    path('<int:product_id>/', views.product_detail, name='product_detail'),
    path('add/', views.add_product, name='add_product'),
]
