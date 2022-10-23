document.addEventListener('DOMContentLoaded', () => {

    // search

    const orders = document.querySelector('#orders');

    if (orders) {

        const ordersSocket = new WebSocket(
            'ws://'
            + window.location.host
            + '/ws/'
            + 'place/index/'
        );

        ordersSocket.onmessage = e => {

            const data = JSON.parse(e.data);

            // if there is new message
            if (data.order_id) {

                // create row
                const row = document.createElement('div');
                row.className = "order-row row";

                // insert data to it
                row.innerHTML = `<div class="col col-lg-2 col-sm-auto col-xs-auto"><img class="im-size" src=${data.res_img}></div>
                                            <div class="col col-lg-2 col-sm-auto col-xs-auto"><p>${data.res_name}</p></div>
                                            <div class="col col-lg-2 col-sm-auto col-xs-auto">
                                            <p class="text-break"><span class="text-info">FROM: </span>${data.res_adr}. <span class="text-info">TO: </span> ${data.user_adr}.</p>
                                            </div>
                                            <div class="col col-lg-2 col-sm-auto col-xs-auto"><p class="text-break" id="order-order-${data.order_id}">${data.order}</p></div>
                                            <div class="col col-lg-2 col-sm-auto col-xs-auto"><p id="sum-order-${data.order_id}">${data.sum_order}</p></div>
                                            <div class="col col-lg-2 col-sm-auto col-xs-auto">
                                            <button type="submit" class="accept-btn btn btn-success" data-order="${data.order_id}" data-res="${data.res_id}">Accept</button><span class="text-danger ms-3 fs-3"></span>
                                            </div>`;

                // append row to orders
                orders.prepend(row);
            }

        }


        document.addEventListener('click', btn => {
            if (btn.target.className === "accept-btn btn btn-success") {
                var error;

                const acceptSocket = new WebSocket(
                    'ws://'
                    + window.location.host
                    + '/ws/'
                    + 'accept/'
                    + btn.target.dataset.order
                    + '/'
                );
                acceptSocket.onopen = () => {

                    acceptSocket.send(JSON.stringify({
                        'del_id': document.querySelector('#del-id').value,
                        'del_name': document.querySelector('#del-name').value,
                        'del_img': document.querySelector('#del-img').value,
                        'del_car': document.querySelector('#del-car').value,
                        'del_number': document.querySelector('#del-number').value,
                    }));

                }

                acceptSocket.onmessage = e => {

                    const data = JSON.parse(e.data);

                    if (!data.error) {
                        const resSocket = new WebSocket(
                            'ws://'
                            + window.location.host
                            + '/ws/'
                            + 'res/'
                            + btn.target.dataset.res
                            + '/'
                        );
                        resSocket.onopen = () => {

                            resSocket.send(JSON.stringify({
                                'order_id': btn.target.dataset.order,
                                'del_name': document.querySelector('#del-name').value,
                                'order_order': document.querySelector(`#order-order-${btn.target.dataset.order}`).innerHTML,
                                'sum_order': document.querySelector(`#sum-order-${btn.target.dataset.order}`).innerHTML,
                            }));

                        }

                        resSocket.onmessage = e => {
                            window.location.replace('/delivery_person/live_order')
                        }
                    } else {
                        btn.target.nextElementSibling.innerHTML = "Error accepting order";
                    }
                }
            }
        });
    }


});