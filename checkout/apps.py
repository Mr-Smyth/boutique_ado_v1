from django.apps import AppConfig


class CheckoutConfig(AppConfig):
    name = 'checkout'

    # override ready method to import our signals module
    # with that done - everytime a line item is saved or deleted
    # our custom update total model method will be called, updating the order
    # totals automatically
    def ready(self):
        import checkout.signals
