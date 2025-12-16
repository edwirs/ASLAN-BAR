import json

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.views.generic import FormView

from core.pos.models import Sale
from core.reports.forms import ReportForm

MODULE_NAME = 'R.Cortesías/Descuentos'


class SaleDiscountReportView(LoginRequiredMixin, FormView):
    template_name = 'sale_discount_cortesia/report.html'
    form_class = ReportForm
    permission_required = 'report_sales_menu'

    def post(self, request, *args, **kwargs):
        action = request.POST['action']
        data = {}
        try:
            if action == 'search_report':
                data = []
                start_date = request.POST.get('start_date')
                end_date = request.POST.get('end_date')

                # Filtrar solo ventas con autorización de descuento
                queryset = Sale.objects.filter(autorization_discount__isnull=False)

                # Filtro por fechas si existen
                if start_date and end_date:
                    queryset = queryset.filter(date_joined__range=[start_date, end_date])

                # Construcción del JSON personalizado
                for sale in queryset:
                    # Tipo de venta
                    if sale.discount_value == sale.subtotal_12:
                        tipo_venta = 'Cortesía'
                    elif sale.discount_value < sale.subtotal_12:
                        tipo_venta = 'Descuento'
                    else:
                        tipo_venta = 'Sin Clasificación'

                    data.append({
                        "id": sale.id,
                        "tipo_venta": tipo_venta,
                        "autorization_discount": sale.get_autorization_discount_display(),
                        "description": sale.description,
                        "subtotal_12": float(sale.subtotal_12),
                        "discount_value": float(sale.discount_value or 0),
                        "employee_name": sale.employee.names if sale.employee else ""
                    })

            else:
                data['error'] = 'No ha seleccionado ninguna opción'

        except Exception as e:
            data['error'] = str(e)

        return HttpResponse(json.dumps(data), content_type='application/json')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Reporte de Cortesías y/o Descuentos'
        context['module_name'] = MODULE_NAME
        return context
