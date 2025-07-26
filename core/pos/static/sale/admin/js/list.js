var tblSale;
var input_date_range;

var sale = {
    list: function (all) {
        var parameters = {
            'action': 'search',
            'start_date': input_date_range.data('daterangepicker').startDate.format('YYYY-MM-DD'),
            'end_date': input_date_range.data('daterangepicker').endDate.format('YYYY-MM-DD'),
        };
        if (all) {
            parameters['start_date'] = '';
            parameters['end_date'] = '';
        }
        tblSale = $('#data').DataTable({
            autoWidth: false,
            destroy: true,
            deferRender: true,
            ajax: {
                url: pathname,
                type: 'POST',
                headers: {
                    'X-CSRFToken': csrftoken
                },
                data: parameters,
                dataSrc: ""
            },
            order: [[0, 'desc']],
            columns: [
                {data: "id"},
                {data: "employee.names"},
                {data: "subtotal_12"},
                {data: "total"}, 
                {data: "discount_value"},   
                {data: "paymentmethod.name"},
                {data: "transfermethods.name"},
                {data: "delivered"},
                {data: "payment"},
                {data: "id"},
            ],
            columnDefs: [
                {
                    targets: [-6, -7, -8],
                    class: 'text-center',
                    render: function (data, type, row) {
                        return '$' + parseFloat(data).toLocaleString('es-CL');
                    }
                },
                {
                    targets: [-2, -3, -4, -5],
                    class: 'text-center',
                },
                {
                    targets: [-2],
                    class: 'text-center',
                    render: function (data, type, row) {
                        const checked = row.payment ? 'checked' : '';
                        const disabled = row.payment ? 'disabled' : '';
                        return `
                            <div class="d-flex justify-content-center align-items-center" style="height: 100%;">
                                <div class="form-check form-switch m-0">
                                    <input class="form-check-input payment-switch" type="checkbox" data-id="${row.id}" ${checked} ${disabled}>
                                </div>
                            </div>
                        `;
                    }
                },
                {
                    targets: [-3],
                    class: 'text-center',
                    render: function (data, type, row) {
                        const checked = row.delivered ? 'checked' : '';
                        return `
                            <div class="d-flex justify-content-center align-items-center" style="height: 100%;">
                                <div class="form-check form-switch m-0">
                                    <input class="form-check-input delivered-switch" type="checkbox" data-id="${row.id}" ${checked}>
                                </div>
                            </div>
                        `;
                    }
                },
                {
                    targets: [-1],
                    class: 'text-center',
                    render: function (data, type, row) {
                        var buttons = '<a rel="detail" data-bs-toggle="tooltip" title="Detalle" class="btn btn-success btn-sm rounded-pill"><i class="fas fa-boxes"></i></a> ';
                        buttons += '<a href="' + pathname + 'delete/' + row.id + '/" data-bs-toggle="tooltip" title="Eliminar" class="btn btn-danger btn-sm rounded-pill"><i class="fas fa-trash"></i></a> ';
                        //buttons += '<a href="' + pathname + 'print/invoice/' + row.id + '/" target="_blank" data-bs-toggle="tooltip" title="Imprimir" class="btn btn-secondary btn-sm rounded-pill"><i class="fas fa-print"></i></a>';
                        return buttons;
                    }
                },
            ],
            rowCallback: function (row, data, index) {

            },
            initComplete: function (settings, json) {
                enable_tooltip();
            },
            footerCallback: function (row, data, start, end, display) {
                var api = this.api();

                // Sumar todos los valores de la columna "Total" (índice 3)
                var total = api
                    .column(3, { page: 'all' })
                    .data()
                    .reduce(function (a, b) {
                        return parseFloat(a) + parseFloat(b);
                    }, 0);

                // Mostrar el total en el pie de la tabla
                $(api.column(3).footer()).html('$' + total.toLocaleString('es-CL'));

                // Filtrar solo los pagos confirmados (payment === true)
                var totalPagado = data.reduce(function (acc, curr) {
                    if (curr.payment) {
                        return acc + parseFloat(curr.total);
                    }
                    return acc;
                }, 0);

                // Mostrar total general
                $(api.column(4).footer()).html('$' + total.toLocaleString('es-CL'));

                // Mostrar el total en el label grande arriba
                $('#lblTotal').text('$' + total.toLocaleString('es-CL'));
                $('#lblTotal_pago').text('$' + totalPagado.toLocaleString('es-CL'));
            }
        });
        $('#data thead th').css('background-color', '#ffffff');
    }
};

$(function () {
    input_date_range = $('input[name="date_range"]');

    $('#data tbody')
        .off()
        .on('click', 'a[rel="detail"]', function () {
            $('.tooltip').remove();
            var tr = tblSale.cell($(this).closest('td, li')).index();
            var row = tblSale.row(tr.row).data();
            $('#tblProducts').DataTable({
                autoWidth: false,
                destroy: true,
                ajax: {
                    url: pathname,
                    type: 'POST',
                    headers: {
                        'X-CSRFToken': csrftoken
                    },
                    data: {
                        'action': 'search_detail_products',
                        'id': row.id
                    },
                    dataSrc: ""
                },
                columns: [
                    {data: "product.short_name"},
                    {data: "price_with_vat"},
                    {data: "cant"},
                    {data: "subtotal"},
                    {data: "total_dscto"},
                    {data: "total"},
                ],
                columnDefs: [
                    {
                        targets: [-1, -2, -3, -5],
                        class: 'text-center',
                        render: function (data, type, row) {
                            return '$' + data.toFixed(2);
                        }
                    },
                    {
                        targets: [-4],
                        class: 'text-center',
                        render: function (data, type, row) {
                            return data;
                        }
                    }
                ],
                initComplete: function (settings, json) {

                }
            });
            $('#myModalDetail').modal('show');
        })

    input_date_range
        .daterangepicker({
                language: 'auto',
                startDate: new Date(),
                locale: {
                    format: 'YYYY-MM-DD',
                },
                autoApply: true,
            }
        )
        .on('change.daterangepicker apply.daterangepicker', function (ev, picker) {
            sale.list(false);
        });

    $('.drp-buttons').hide();

    sale.list(false);

    $('.btnSearchAll').on('click', function () {
        sale.list(true);
    });

    $('#data tbody').on('change', '.delivered-switch', function () {
        const saleId = $(this).data('id');
        const isChecked = $(this).is(':checked');

        fetch(pathname + 'delivered/' + saleId + '/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrftoken,
            }
        })
        .then(response => response.json())
        .then(data => {
            if (!data.success) {
                alert('Error al actualizar el estado de entrega.');
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
    });

    $('#data tbody').on('change', '.payment-switch', function () {
        const checkbox = $(this);
        const saleId = $(this).data('id');
        const isChecked = $(this).is(':checked');

        // Verificar si el checkbox "delivered" correspondiente está marcado
        const deliveredCheckbox = checkbox.closest('tr').find('.delivered-switch');
        const isDelivered = deliveredCheckbox.is(':checked');

        // Si no está entregado, no permitir marcar "payment"
        if (!isDelivered) {
            // Cancelar el cambio visual
            checkbox.prop('checked', false);

            return message_error('No se puede marcar como pagado hasta que sea entregado.');
        }

        // Solo permitir marcar (no desmarcar)
        if (isChecked) {
            // Deshabilitar inmediatamente para evitar cambios posteriores
            checkbox.prop('disabled', true);

            fetch(pathname + 'payment/' + saleId + '/', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrftoken,
                }
            })
            .then(response => response.json())
            .then(data => {
                if (!data.success) {
                    alert('Error al actualizar el estado de pago.');
                    // Revertir el cambio si hubo error
                    checkbox.prop('checked', false);
                    checkbox.prop('disabled', false);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                // Revertir también si hay error en la red
                checkbox.prop('checked', false);
                checkbox.prop('disabled', false);
            });
        } else {
            // Si intenta desmarcarlo, impedirlo
            checkbox.prop('checked', true);
        }
    });

});