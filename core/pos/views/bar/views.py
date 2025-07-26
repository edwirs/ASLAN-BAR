import json

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import Group
from django.db import transaction
from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, DeleteView, FormView, TemplateView

from core.pos.forms import *
from core.pos.utilities import printer
from core.reports.forms import ReportForm
from core.security.mixins import GroupPermissionMixin

MODULE_NAME = 'Barra'

class BarCreateView(GroupPermissionMixin, CreateView):
    model = Sale
    template_name = 'bar/admin/create.html'
    form_class = BarForm
    success_url = reverse_lazy('bar_admin_create')
    permission_required = 'add_bar'

    def post(self, request, *args, **kwargs):
        action = request.POST['action']
        data = {}
        try:
            if action == 'add':
                with transaction.atomic():
                    company = Company.objects.first()
                    iva = float(company.iva) / 100
                    sale = Sale()
                    sale.company = company
                    if request.user.username == 'meseros':
                        sale.employee_id = request.POST.get('employee')
                    else:
                        sale.employee_id = request.user.id
                    sale.client_id = int(request.POST['client'])
                    sale.iva = iva
                    sale.dscto = float(request.POST['dscto']) / 100
                    sale.cash = float(0)
                    sale.change = float(0)
                    sale.paymentmethod = (request.POST['paymentmethod'])
                    if sale.paymentmethod == 'transfer':
                        sale.transfermethods = (request.POST['transfermethods'])
                    else:
                        sale.transfermethods = None

                    if request.POST.get('switchDescuento') == 'on':
                        sale.autorization_discount = (request.POST['autorization_discount'])
                    elif request.POST.get('switchCortesia') == 'on':
                        sale.autorization_discount = (request.POST['autorization_discount'])
                    else:
                        sale.autorization_discount = None
                    sale.save()
                    for i in json.loads(request.POST['products']):
                        product = Product.objects.get(pk=i['id'])
                        detail = SaleDetail()
                        detail.sale_id = sale.id
                        detail.product_id = product.id
                        detail.cant = int(i['cant'])
                        detail.price = float(i['pvp'])
                        detail.dscto = float(i['dscto']) / 100
                        detail.save()
                        sale.calculate_detail()
                        detail.product.stock -= detail.cant
                        detail.product.save()

                        auto_products = ProductAutoAdd.objects.filter(trigger_product=product)
                        for auto in auto_products:
                            extra_detail = SaleDetail()
                            extra_detail.sale_id = sale.id
                            extra_detail.product_id = auto.auto_product.id
                            extra_detail.cant = auto.quantity
                            extra_detail.price = 0
                            extra_detail.dscto = 0
                            extra_detail.save()
                            sale.calculate_detail()
                            auto.auto_product.stock -= auto.quantity
                            auto.auto_product.save()
                    sale.calculate_invoice()
                    # Aplicar descuento personalizado (después de calcular total)
                    discount_value = float(request.POST.get('discount_value', 0))
                    if discount_value > 0:
                        sale.discount_value = discount_value
                        sale.total -= discount_value
                        sale.save()
                    if request.POST.get('switchCortesia') == 'on':
                        sale.discount_value = sale.total
                        sale.total = 0
                        sale.save()
                    data = {'print_url': str(reverse_lazy('sale_admin_print_invoice', kwargs={'pk': sale.id}))}
            elif action == 'search_products':
                ids = json.loads(request.POST['ids'])
                data = []
                term = request.POST['term']
                queryset = Product.objects.filter(Q(stock__gt=0) | Q(is_service=True)).exclude(id__in=ids).order_by('code')
                if len(term):
                    queryset = queryset.filter(Q(name__icontains=term) | Q(code__icontains=term))
                    queryset = queryset[:10]
                for i in queryset:
                    item = i.toJSON()
                    item['pvp'] = float(i.pvp)
                    item['value'] = i.get_full_name()
                    item['dscto'] = '0.00'
                    item['total_dscto'] = '0.00'
                    data.append(item)
            elif action == 'search_client':
                data = []
                term = request.POST['term']
                for i in Client.objects.filter(Q(names__icontains=term) | Q(dni__icontains=term)).order_by('names')[0:10]:
                    data.append(i.toJSON())
            elif action == 'create_client':
                form = ClientForm(self.request.POST)
                data = form.save()
            else:
                data['error'] = 'No ha seleccionado ninguna opción'
        except Exception as e:
            data['error'] = str(e)
        return HttpResponse(json.dumps(data), content_type='application/json')

    def get_final_consumer(self):
        queryset = Client.objects.filter(dni='2222222222')
        if queryset.exists():
            return json.dumps(queryset[0].toJSON())
        return {}
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['frmClient'] = ClientForm()
        context['list_url'] = self.success_url
        context['title'] = 'Nuevo registro de una Venta de Barra'
        context['action'] = 'add'
        context['company'] = Company.objects.first()
        context['final_consumer'] = self.get_final_consumer()
        context['module_name'] = MODULE_NAME
        context['products'] = Product.objects.filter(Q(stock__gt=0) | Q(is_service=True)).order_by('id')
        return context
