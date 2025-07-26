import json
from datetime import datetime

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import FloatField, Sum
from django.db.models.functions import Coalesce
from django.http import HttpResponse
from django.views.generic import TemplateView
from django.db.models import DecimalField
from django.utils.timezone import now, timedelta
from decimal import Decimal

from core.pos.models import Sale, Product, SaleDetail, Company
from core.security.models import Dashboard


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'panel.html'
    permission_required = 'view_dashboard'
    raise_exception = True

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            action = request.POST['action']
            if action == 'get_graph_sales_year_month':
                data = []
                year = datetime.now().year
                queryset = Sale.objects.filter(date_joined__year=year)
                for m in range(1, 13):
                    total = queryset.filter(date_joined__month=m).aggregate(result=Coalesce(Sum('total'), 0.00, output_field=FloatField())).get('result')
                    data.append(float(total))
            elif action == 'get_graph_sales_products_year_month':
                data = []
                year = datetime.now().year
                month = datetime.now().month
                queryset = SaleDetail.objects.filter(sale__date_joined__year=year, sale__date_joined__month=month)
                for p in Product.objects.filter():
                    total = queryset.filter(product_id=p.id).aggregate(result=Coalesce(Sum('total'), 0.00, output_field=FloatField())).get('result')
                    if total:
                        data.append({'name': p.name, 'y': float(total)})
            elif action == 'get_sales_total_today':
                last_24_hours = now() - timedelta(hours=24)
                total = (
                    Sale.objects
                    .filter(date_joined__gte=last_24_hours)
                    .aggregate(total=Coalesce(Sum('total'), 0.00, output_field=DecimalField()))['total']
                )
                data = {'total': float(total)}
            elif action == 'get_sales_total_today_payment':
                last_24_hours = now() - timedelta(hours=24)
                total = (
                    Sale.objects
                    .filter(date_joined__gte=last_24_hours, payment = True)
                    .aggregate(total=Coalesce(Sum('total'), 0.00, output_field=DecimalField()))['total']
                )
                data = {'total': float(total)}
            elif action == 'gain_employee':
                last_24_hours = now() - timedelta(hours=24)
                total = (
                    Sale.objects
                    .filter(date_joined__gte=last_24_hours, payment = True)
                    .aggregate(total=Coalesce(Sum('total'), 0.00, output_field=DecimalField()))['total']
                )
                company = Company.objects.first()
                commission_percent = company.commission if company else 0
                gain = total * (Decimal(commission_percent) / Decimal('100'))

                data = {'total': float(gain)}
            elif action == 'sales_not_payment':
                last_24_hours = now() - timedelta(hours=24)
                total = (
                    Sale.objects
                    .filter(date_joined__gte=last_24_hours, payment=False)
                    .count()
                )

                data = {'total': float(total)}
            else:
                data['error'] = 'No ha seleccionado ninguna opción'
        except Exception as e:
            data['error'] = str(e)
        return HttpResponse(json.dumps(data), content_type='application/json')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Panel de Administración'
        context['sales'] = Sale.objects.filter().order_by('-id')[0:10]
        context['dashboard'] = Dashboard.objects.first()
        return context
