# get our forms from django and the order model

from django import forms
from .models import Order


class OrderForm(forms.ModelForm):
    class Meta:
        # tell django which model it will be associated with
        model = Order
        # which fields to render - no need to render automatically calculated
        # fields
        fields = ('full_name', 'email', 'phone_number',
                  'street_address1', 'street_address2',
                  'town_or_city', 'postcode', 'country',
                  'county',)

    # init method of the form:
    def __init__(self, *args, **kwargs):
        """
        Add placeholders and classes, remove auto-generated
        labels and set autofocus on first field
        """
        # call the defaul init method to set the form up as it would be by
        # default.
        super().__init__(*args, **kwargs)
        # create a dictionary of placeholders - which will show up in the form
        # fields rather than having clunky looking labels and empty text boxes
        # in the template
        placeholders = {
            'full_name': 'Full Name',
            'email': 'Email Address',
            'phone_number': 'Phone Number',
            'country': 'Country',
            'postcode': 'Postal Code',
            'town_or_city': 'Town or City',
            'street_address1': 'Street Address 1',
            'street_address2': 'Street Address 2',
            'county': 'County',
        }

        # set the autofocus to true in the full name field - so the cursor
        # will start in the full name field
        self.fields['full_name'].widget.attrs['autofocus'] = True

        # then iterate through the forms fields to add a * to any required
        # fields on the model
        for field in self.fields:
            if self.fields[field].required:
                placeholder = f'{placeholders[field]} *'
            else:
                # then set the placeholder attribute from the dictionary above
                placeholder = placeholders[field]
            self.fields[field].widget.attrs['placeholder'] = placeholder

            # add the stripe-style-input css class - we will add to later
            self.fields[field].widget.attrs['class'] = 'stripe-style-input'

            # remove the form fields labels as we do not need them now the
            # placeholders are set
            self.fields[field].label = False
