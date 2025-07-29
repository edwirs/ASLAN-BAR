$(document).ready(function () {

    let initialized = false;

    $('a[data-toggle="tab"]').on('shown.bs.tab', function (e) {
        const target = $(e.target).attr("href");
        if (target === '#tab-stock' && !initialized) {
        if ($.fn.DataTable) {
            $('#inventory_management').DataTable({
                language: {
                        url: 'https://cdn.datatables.net/plug-ins/1.13.6/i18n/es-ES.json'
                    }
            });
            initialized = true;
        } else {
            console.warn('DataTable no está disponible.');
        }
        }
    });
});