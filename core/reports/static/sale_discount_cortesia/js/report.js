var input_date_range;
var current_date;
var tblReport;
var columns = [];

var report = {
    initTable: function () {
        tblReport = $('#tblReportDiscount').DataTable({
            autoWidth: false,
            destroy: true,
        });
        tblReport.settings()[0].aoColumns.forEach(function (value, index, array) {
            columns.push(value.sWidthOrig);
        });
    },

    list: function (all) {
        var parameters = {
            'action': 'search_report',
            'start_date': input_date_range.data('daterangepicker').startDate.format('YYYY-MM-DD'),
            'end_date': input_date_range.data('daterangepicker').endDate.format('YYYY-MM-DD'),
        };

        if (all) {
            parameters['start_date'] = '';
            parameters['end_date'] = '';
        }

        tblReport = $('#tblReportDiscount').DataTable({
            destroy: true,
            autoWidth: false,
            ajax: {
                url: pathname,
                type: 'POST',
                headers: {
                    'X-CSRFToken': csrftoken
                },
                data: parameters,
                dataSrc: ''
            },
            order: [[0, 'asc']],
            paging: true,
            ordering: true,
            dom: 'Bfrtip',

            // Botones
            buttons: [
                {
                    extend: 'excelHtml5',
                    text: ' <i class="fas fa-file-excel"></i> Descargar',
                    className: 'btn btn-success btn-sm mb-3'
                },
                {
                    extend: 'pdfHtml5',
                    text: '<i class="fas fa-file-pdf"></i> Descargar',
                    className: 'btn btn-danger btn-sm mb-3',
                    download: 'open',
                    orientation: 'landscape',
                    pageSize: 'LEGAL',
                    customize: function (doc) {
                        doc.styles = {
                            header: { fontSize: 18, bold: true, alignment: 'center' },
                            tableHeader: {
                                bold: true,
                                fontSize: 11,
                                color: 'white',
                                fillColor: '#2d4154',
                                alignment: 'center'
                            }
                        };
                        doc.content[1].table.widths = columns;
                        doc['footer'] = (function (page, pages) {
                            return {
                                columns: [
                                    { alignment: 'left', text: ['Fecha: ', {text: current_date}] },
                                    { alignment: 'right', text: ['Página ', {text: page.toString()}, ' de ', {text: pages.toString()}] }
                                ],
                                margin: 20
                            };
                        });
                    }
                }
            ],

            // COLUMNAS SEGÚN LA NUEVA VISTA
            columns: [
                { data: "id" },
                { data: "tipo_venta" },
                { data: "autorization_discount" },
                { data: "description" },
                { data: "subtotal_12" },
                { data: "discount_value" },
                { data: "employee_name" },
            ],

            // FORMATO DE COLUMNAS
            columnDefs: [
                {
                    targets: [-2, -3],
                    class: 'text-center',
                    render: function (data) {
                        return '$' + parseFloat(data).toFixed(2);
                    }
                }
            ]
        });

        $('#tblReport thead th').css('background-color', '#ffffff');
    }
};

$(function () {

    current_date = new moment().format('YYYY-MM-DD');
    input_date_range = $('input[name="date_range"]');

    input_date_range
        .daterangepicker({
            language: 'auto',
            startDate: new Date(),
            locale: { format: 'YYYY-MM-DD' },
            autoApply: true,
        })
        .on('change.daterangepicker apply.daterangepicker', function () {
            report.list(false);
        });

    $('.drp-buttons').hide();

    report.initTable();
    report.list(false);

    $('.btnSearchAll').on('click', function () {
        report.list(true);
    });
});
