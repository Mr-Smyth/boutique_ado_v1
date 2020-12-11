
// get the value of the country field when the page loads and store it in a variable
let countrySelected = $('#id_default_country').val();

// Remember that the value will be an empty string if the first option is selected. So to determine if that's selected we can use this as a boolean
// so if country selected is false
if(!countrySelected) {
    // we want it to be that grey colour
    $('#id_default_country').css('color', '#aab7c4');
};
$('#id_default_country').change(function() {
    countrySelected = $(this).val();
    if(!countrySelected) {
        $(this).css('color', '#aab7c4');
    } else {
        $(this).css('color', '#000');
    }
});