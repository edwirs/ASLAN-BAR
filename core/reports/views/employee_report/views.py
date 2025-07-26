import json

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, JsonResponse
from django.views.generic import FormView
from django.db.models import Sum

from core.pos.models import Sale, Company
from core.reports.forms import ReportForm

MODULE_NAME = 'R.Ventas Emp.'


class EmployeeSaleReportView(LoginRequiredMixin, FormView):
    template_name = 'employee_report/report.html'
    form_class = ReportForm

    def post(self, request, *args, **kwargs):
        action = request.POST.get('action')
        if action == 'search_report':
            try:
                start_date = request.POST.get('start_date')
                end_date = request.POST.get('end_date')
                sales = Sale.objects.all()

                if start_date and end_date:
                    sales = sales.filter(date_joined__range=[start_date, end_date])

                company_instance = sales.first().company if sales.exists() else None
                commission = float(company_instance.commission) if company_instance else 0
                commission = commission / 100
                
                grouped = sales.values('employee__id', 'employee__names').annotate(
                    subtotal=Sum('subtotal_12'),
                    total=Sum('total')
                )

                data = [{
                    'employee': {
                        'id': item['employee__id'],
                        'names': item['employee__names']
                    },
                    'subtotal': float(item['subtotal'] or 0),
                    'total': float(item['total'] or 0),
                    'commission': round(float(item['total'] or 0) * commission, 2)
                } for item in grouped]

                return JsonResponse(data, safe=False)
            except Exception as e:
                return JsonResponse({'error': str(e)}, status=500)
        return JsonResponse({'error': 'Acción no válida'}, status=400)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Reporte de Ventas por Empleado'
        context['module_name'] = MODULE_NAME
        return context
