/*
    Core logic/payment flow for this comes from here:
    https://stripe.com/docs/payments/accept-a-payment
    CSS from here: 
    https://stripe.com/docs/stripe-js
*/
/* get the public and client secret from the template - courtesy of postblockjs in checkout.html */
var stripe_public_key = $('#id_stripe_public_key').text().slice(1, -1);
var client_secret = $('#id_client_secret').text().slice(1, -1);

/* because of the stripe.js included in the base template all we need to do to setup stripe is
    create a variable using our stripe public key*/
var stripe = Stripe(stripe_public_key);

/* Now we can use that to create an instance of stripe elements to add a pre built credit card input to our form */
var elements = stripe.elements();

/* this is styling from the stripe js docs */
var style = {
    base: {
        color: '#000',
        fontFamily: '"Helvetica Neue", Helvetica, sans-serif',
        fontSmoothing: 'antialiased',
        fontSize: '16px',
        '::placeholder': {
            color: '#aab7c4'
        }
    },
    invalid: {
        color: '#dc3545',
        iconColor: '#dc3545'
    }
};
/* use the strip elements to create a card element and pass in above style*/
var card = elements.create('card', {style: style});

/* mount the card element to the div we created in the last video  */
card.mount('#card-element');