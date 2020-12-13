from django import forms
from .widgets import CustomClearableFileInput
from .models import Product, Category


# ProductForm() which will extend the built in forms.model form.
class ProductForm(forms.ModelForm):

    # inner metaclass that defines the model and the fields we want to include
    class Meta:
        model = Product
        fields = '__all__'

    image = forms.ImageField(label='Image',
                             required=False,
                             widget=CustomClearableFileInput)

    # override the init method to make some changes to the fields
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # We'll want the categories to show up in the form using their friendly
        # name. So let's get all the categories
        categories = Category.objects.all()

        # And create a list of tuples of the friendly names associated with
        # their category ids. This special syntax is called the list
        # comprehension, and is just a shorthand way of creating a for loop
        # that adds items to a list.
        friendly_names = [(c.id, c.get_friendly_name()) for c in categories]

        # Now that we have the friendly names, let's update the category field
        # on the form. To use those for choices instead of using the id. The
        # effect of this will be seen in the select box that gets generated
        # in the form. Instead of seeing the category ID or the name field
        # we'll see the friendly name.

        self.fields['category'].choices = friendly_names
        # Finally I'll just iterate through the rest of these fields
        # and set some classes on them to make them match the theme of the
        # rest of our store.
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'border-black rounded-0'