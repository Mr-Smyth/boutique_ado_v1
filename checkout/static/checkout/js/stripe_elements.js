/*
    Core logic/payment flow for this comes from here:
    https://stripe.com/docs/payments/accept-a-payment
    CSS from here: 
    https://stripe.com/docs/stripe-js
*/
/* get the public and client secret from the template - courtesy of postblockjs in checkout.html */
var stripePublicKey = $('#id_stripe_public_key').text().slice(1, -1);
var clientSecret = $('#id_client_secret').text().slice(1, -1);

/* because of the stripe.js included in the base template all we need to do to setup stripe is
    create a variable using our stripe public key*/
var stripe = Stripe(stripePublicKey);

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

/* mount the card element to the div we created in the last video (in checkout.html) */
card.mount('#card-element');


// Handle realtime validation errors on the card element
// add an event listener to the card element
card.addEventListener('change', function (event) {
    
    // if there is an error
    var errorDiv = document.getElementById('card-errors');
    if (event.error) {
        var html = `
            <span class="icon" role="alert">
                <i class="fas fa-times"></i>
            </span>
            <span>${event.error.message}</span>
        `;
        $(errorDiv).html(html);
    // else theres no error
    } else {
        errorDiv.textContent = '';
    }
});

// Handle form submit - copied from stripe docs

// get the form element
var form = document.getElementById('payment-form');

// listen to the submit
form.addEventListener('submit', function(ev) {
    // prevent default action while we send card info to stripe
    ev.preventDefault();

    // before we send the info to stripe we want to disable the submit button to prevent multiple submissions
    card.update({ 'disabled': true});
    $('#submit-button').attr('disabled', true);
    $('#payment-form').fadeToggle(100);
    $('#loading-overlay').fadeToggle(100);

    // Now send card info - securely - to stripe
    stripe.confirmCardPayment(clientSecret, {
    // confirm the payment method
    payment_method: {
        // provide the card to stripe
        card: card,
    }
    // then execute this function on the result
    }).then(function(result) {
        if (result.error) {
            // Show error to your customer (e.g., insufficient funds)
            // display as we did above by putting the error directly into the card error div
            var errorDiv = document.getElementById('card-errors');
            var html = `
            <span class="icon" role="alert">
                <i class="fas fa-times"></i>
            </span>
            <span>${event.error.message}</span>`;
            $(errorDiv).html(html);

            // if there is an error - we would need to re-enable the submit button
            card.update({ 'disabled': false});
            $('#submit-button').attr('disabled', false);
        } else {
            // so if the status of the payment intent comes back as succeeded
            if (result.paymentIntent.status === 'succeeded') {
                // then lets submit the form
                form.onsubmit();
            }
        }
    });
});