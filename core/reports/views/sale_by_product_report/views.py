import json

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.views.generic import FormView
from django.db.models import Sum, Case, When, IntegerField, DecimalField, F, Q

from core.pos.models import Sale, SaleDetail
from core.reports.forms import ReportForm

MODULE_NAME = 'R.Ventas X Producto'


class SaleByProductReportView(LoginRequiredMixin, FormView):
    template_name = 'sale_by_product_report/report.html'
    form_class = ReportForm
    permission_required = 'report_sales_menu'

    def post(self, request, *args, **kwargs):
        action = request.POST['action']
        data = {}
        try:
            if action == 'search_report':
                data = []
                start_date = request.POST['start_date']
                end_date = request.POST['end_date']
                filters = Q()
                if start_date and end_date:
                    filters &= Q(sale__date_joined__range=[start_date, end_date])

                queryset = SaleDetail.objects.filter(filters)

                report = queryset.values(
                        'product_id', 
                        'product__name',
                        'product__stock',
                        'product__price'
                    ).annotate(
                    ventas_totales=Sum('total'),
                    ventas_pagadas=Sum(
                        Case(
                            When(sale__payment=True, then='total'),
                            default=0,
                            output_field=DecimalField()
                        )
                    ),
                    cantidad_vendida_gt_0=Sum(
                        Case(
                            When(total__gt=0, then='cant'),
                            default=0,
                            output_field=IntegerField()
                        )
                    ),
                    cantidad_vendida_eq_0=Sum(
                        Case(
                            When(total=0, then='cant'),
                            default=0,
                            output_field=IntegerField()
                        )
                    ),
                    cantidad_total=Sum('cant'),
                )

                for item in report:
                    cantidad_total = item['cantidad_total'] or 0
                    costo_unitario = float(item['product__price'] or 0)
                    costo_total = costo_unitario * cantidad_total

                    data.append({
                        'producto': item['product__name'],
                        'stock': item['product__stock'],
                        'costo_unitario': costo_unitario,
                        'costo_total': round(costo_total, 2),
                        'ventas_totales': float(item['ventas_totales'] or 0),
                        'ventas_pagadas': float(item['ventas_pagadas'] or 0),
                        'cantidad_vendida_gt_0': item['cantidad_vendida_gt_0'] or 0,
                        'cantidad_vendida_eq_0': item['cantidad_vendida_eq_0'] or 0,
                    })
            else:
                data['error'] = 'No ha seleccionado ninguna opción'
        except Exception as e:
            data['error'] = str(e)
        return HttpResponse(json.dumps(data), content_type='application/json')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Reporte de Ventas por Producto'
        context['module_name'] = MODULE_NAME
        return context
