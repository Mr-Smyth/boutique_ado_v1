from django.forms.widgets import ClearableFileInput
# used for translation - not really required - just do it to keep our custom
# class as close to the original as possible
from django.utils.translation import gettext_lazy as _


# create new class - which inherits the built in one
class CustomClearableFileInput(ClearableFileInput):
    # override the following with our own values
    clear_checkbox_label = _('Remove')
    initial_text = _('Current Image')
    input_text = _('')
    # inside the product apps, templates folder we need to create this
    # template -: custom_widget_templates/custom_clearable_file_input.html
    # making sure that its name and location matches what is in our class.
    template_name = 'products/custom_widget_templates/custom_clearable_file_input.html'
