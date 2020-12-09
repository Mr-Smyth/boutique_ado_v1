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

    // handling save info checkbox
    // get the value of the save info box, by looking at its checked attribute
    var saveInfo = Boolean($('#id-save-info').attr('checked'));
    // We can get the csrf token from the input element that django generates on our form -
    // which will have a name of scrfmiddlewaretoken
    var csrfToken = $('input[name="csrfmiddlewaretoken"]').val();
    // create a small object to pass the information to the new view
    // also pass the client secret for the patment intent
    // THE VIEW UPDATES THE PAYMENT INTENT
    var postData = {
        'csrfmiddlewaretoken': csrfToken,
        'client_secret': clientSecret,
        'save_info': saveInfo,
    };
    // create a variable for the new url
    var url = '/checkout/cache_checkout_data/';

    // post this data to the view
    // we want to post to the url(above) and we want to post the object(above)
    // add the .done and executing a callback function here to wait for a response 
    // that the payment intent was updated with the information
    // before calling the confirmed_payment method
    $.post(url, postData).done(function () {
        // Now send card info - securely - to stripe
        stripe.confirmCardPayment(clientSecret, {
        // confirm the payment method
        payment_method: {
            // provide the card to stripe
            card: card,
            // get the info from our form and using the trim method to trim off any white space
    
            // note- there is no point in adding a billing postal code, as the billing post 
            // code will come from the card element and stripe will override it even if we do add it
            billing_details: {
                name: $.trim(form.full_name.value),
                phone: $.trim(form.phone_number.value),
                email: $.trim(form.email.value),
                address:{
                    line1: $.trim(form.street_address1.value),
                    line2: $.trim(form.street_address2.value),
                    city: $.trim(form.town_or_city.value),
                    country: $.trim(form.country.value),
                    state: $.trim(form.county.value),
                }
            }
        },
        // we can also add shipping details with all the same fields except for email
        shipping: {
            name: $.trim(form.full_name.value),
            phone: $.trim(form.phone_number.value),
            address: {
                line1: $.trim(form.street_address1.value),
                line2: $.trim(form.street_address2.value),
                city: $.trim(form.town_or_city.value),
                country: $.trim(form.country.value),
                postal_code: $.trim(form.postcode.value),
                state: $.trim(form.county.value),
            }
        },
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
                <span>${result.error.message}</span>`;
                $(errorDiv).html(html);
    
                // if there is an error - we would need to re-enable the submit button
                $('#payment-form').fadeToggle(100);
                $('#loading-overlay').fadeToggle(100);
                card.update({ 'disabled': false});
                $('#submit-button').attr('disabled', false);
            } else {
                // so if the status of the payment intent comes back as succeeded
                if (result.paymentIntent.status === 'succeeded') {
                    // then lets submit the form
                    form.submit();
                }
            }
        });
    // tack on  failure function which will be triggered if our view sends a 400 back
    // request response, in that case we will just reload the page and show the user the error message from the view
    }).fail(function () {
        // just reload the page, the error will be in django messages
        location.reload();
    }) 
});