from django import forms
from .models import UserProfile


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        # render all fields except for the user field - as that should never
        # change
        exclude = ('user',)

    def __init__(self, *args, **kwargs):
        """
        Add placeholders and classes, remove auto-generated
        labels and set autofocus on first field

        ** Almost an exact match for checkout form ***
        """
        # call the defaul init method to set the form up as it would be by
        # default.
        super().__init__(*args, **kwargs)
        # create a dictionary of placeholders - which will show up in the form
        # fields rather than having clunky looking labels and empty text boxes
        # in the template
        placeholders = {
            # make these field names match the model
            'default_phone_number': 'Phone Number',
            'default_postcode': 'Postal Code',
            'default_town_or_city': 'Town or City',
            'default_street_address1': 'Street Address 1',
            'default_street_address2': 'Street Address 2',
            'default_county': 'County, State or Locality',
        }

        # autofocus on default phone number
        self.fields['default_phone_number'].widget.attrs['autofocus'] = True

        # then iterate through the forms fields to add a * to any required
        # fields on the model
        for field in self.fields:
            if field != 'default_country':
                if self.fields[field].required:
                    placeholder = f'{placeholders[field]} *'
                else:
                    placeholder = placeholders[field]
                self.fields[field].widget.attrs['placeholder'] = placeholder
            self.fields[field].widget.attrs['class'] = ('border-black '
                                                        'rounded-0 '
                                                        'profile-form-input')
            self.fields[field].label = False