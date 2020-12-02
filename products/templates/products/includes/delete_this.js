
increment = document.querySelector('.increment-qty');
increment.addEventListener("click", function(e){
    e.preventDefault;
    /* find closest input box */
    /* closest searches up the dom
        find searches down */
    /* so from the input element go up the tree to the closest input-group - 
        then drill down to find the first element with the class qty_input */
    let closestInput = increment.closest('.input-group').find('.qty_input')[0];
    let currentValue = parseInt(closestInput).value();
    closestInput.val(currentValue + 1);
});
