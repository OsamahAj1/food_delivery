document.addEventListener('DOMContentLoaded', () => {

    // get cart sum
    const cart = document.querySelector('#cart');
    if (cart) {
        fetch("/sum_cart")
            .then(response => response.json())
            .then(result => {

                // if there error log it
                if (result.error !== undefined) {
                    console.log(result.error);
                }

                // if there is no error display cart sum
                else {
                    cart.innerHTML = result.sum;
                }
            });
    }


    // Add to cart

    const add_button = document.querySelectorAll(".add-button")
    if (add_button) {

        // listen for clicking on add to cart button
        add_button.forEach(button => {

            // when button is clicked
            button.onclick = () => {

                // get csrf token
                const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

                // get n and food_id and message field
                const n = button.nextElementSibling.value;
                const food_id = button.previousElementSibling.value;
                const message = button.nextElementSibling.nextElementSibling;

                // post request to api to add item to cart
                fetch(`/add_cart/${food_id}`, {
                    method: "POST",
                    headers: { 'X-CSRFToken': csrftoken },
                    body: JSON.stringify({
                        n: n
                    })
                })
                    .then(response => response.json())
                    .then(result => {

                        // if there error display it
                        if (result.error !== undefined) {
                            message.innerHTML = result.error;
                            message.className = "text-danger";
                        }

                        // if there is no error
                        else {
                        
                            // update cart number
                            cart.innerHTML = parseInt(cart.innerHTML) + parseInt(n);

                            // show success message
                            message.innerHTML = result.success;
                            message.className = "text-success";
                        }
                    });
            }
        });
    }


    // Update cart

    const update_input = document.querySelectorAll('.update-number-input');
    if (update_input) {
        
        // listen for changing number
        update_input.forEach(input => {
            
            // when input is changed
            input.addEventListener('input', () => {
                
                // get csrf token
                const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

                // get cart_id and message field and sum price
                const cart_id = input.previousElementSibling.value;
                const message = input.nextElementSibling;
                const sum_price = document.querySelector(`#sum-price-${cart_id}`);
                const cart = document.querySelector('#sum-price-cart');

                // post request to api to update n
                fetch(`/update_cart/${cart_id}`, {
                    method: "POST",
                    headers: { 'X-CSRFToken': csrftoken },
                    body: JSON.stringify({
                        n: input.value
                    })
                })
                    .then(response => response.json())
                    .then(result => {

                        // if there is error display it
                        if (result.error !== undefined) {
                            message.innerHTML = result.error;
                            message.className = "text-danger";
                        }

                        // if there is no error
                        else {

                            // remove error message
                            message.innerHTML = "";
                            message.className = "";

                            // update sum price and cart
                            sum_price.innerHTML = result.sum_price;
                            cart.innerHTML = `$${parseFloat(result.sum_cart).toFixed(2)}`;
                        }
                    });
            });
        });
    }

    
    // Remove from cart

    const remove_button = document.querySelectorAll('.remove-button');
    if (remove_button) {
        
        // listen for click
        remove_button.forEach(button => {
            
            // when button is clicked
            button.onclick = () => {
                
                // get csrf token
                const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

                // get cart_id and message field and elemnt user want to remove
                const cart_id = button.previousElementSibling.value;
                const message = button.nextElementSibling;
                const cart_item = document.querySelector(`#cart-item-${cart_id}`);

                // post request to API to delete cart item
                fetch(`/remove_cart/${cart_id}`, {
                    method: "POST",
                    headers: { 'X-CSRFToken': csrftoken },
                })
                    .then(response => response.json())
                    .then(result => {

                        // if there is error display it
                        if (result.error !== undefined) {
                            message.innerHTML = result.error;
                            message.className = "text-danger";
                        }

                        // if there is no error
                        else {

                            // remove error message
                            message.innerHTML = "";
                            message.className = "";

                            // play remove animation
                            cart_item.style.animationPlayState = 'running';

                            // when animation played
                            cart_item.addEventListener('animationend', () => {
                                
                                // remove cart_item
                                cart_item.remove();

                                // update sum_cart
                                cart.innerHTML = result.sum_cart;

                                // if result is 0 hide place order div and show empty message
                                if (result.sum_cart < 1) {
                                    
                                    document.querySelector('#place-order').style.display = "none";
                                    document.querySelector('#empty').innerHTML = `<h3 class="text-center text-info">Cart is empty go to <a href="/home">home page</a> to add items.</h3>`
                                }
                            });
                        }
                    });
            }
        });
    }


    // Order status

    const order_id = document.querySelector('#order_id');
    const order = document.querySelector('#order');
    const send_order = document.querySelector('#send-btn');
    const cancel_order = document.querySelector('#cancel-order-form');
    const wait = document.querySelector('#order-status-wait');
    const info = document.querySelector('#delivery-info');

    if (send_order) {

        info.style.display = 'none';

        // send order
        const publicSocket = new WebSocket(
            'ws://'
            + window.location.host
            + '/ws/'
            + 'place/index/'
        );

        // when send button clicked
        send_order.onclick = e => {

            wait.style.animationPlayState = 'running';
            wait.style.display = 'block';

            // remove cancel and send
            cancel_order.remove();
            send_order.remove();

            publicSocket.send(JSON.stringify({
                'order_id': order_id.value,
                'res_img': document.querySelector('#res-img').src,
                'res_name': document.querySelector('#res-name').innerHTML,
                'res_adr': document.querySelector('#res-adr').value,
                'res_id': document.querySelector('#res-id').value,
                'order': document.querySelector('#order-order').innerHTML,
                'sum_order': document.querySelector('#sum-order').innerHTML,
                'user_adr': document.querySelector('#user-adr').value,
            }));
        }
    }

    if (order) {

        const acceptSocket = new WebSocket(
            'ws://'
            + window.location.host
            + '/ws/'
            + 'accept/'
            + order_id.value
            + '/'
        );

        acceptSocket.onmessage = e => {

            wait.remove();
            info.style.display = 'flex';
         
            const data = JSON.parse(e.data);

            document.querySelector('#delivery-image').src = data.del_img;
            document.querySelector('#delivery-name').innerHTML = data.del_name;
            document.querySelector('#delivery-car').innerHTML = data.del_car;
            document.querySelector('#delivery-number').innerHTML = data.del_number;

        }

    }
});