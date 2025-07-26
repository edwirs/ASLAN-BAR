from django.urls import path

from core.reports.views.sale_report.views import SaleReportView
from core.reports.views.employee_report.views import EmployeeSaleReportView
from core.reports.views.employee_debe_report.views import EmployeeDebeReportView
from core.reports.views.employee_gain.views import EmployeeGainReportView
from core.reports.views.sale_by_product_report.views import SaleByProductReportView

urlpatterns = [
    path('sale/', SaleReportView.as_view(), name='sale_report'),
    path('employeesale/', EmployeeSaleReportView.as_view(), name='employee_sale_report'),
    path('employeedebe/', EmployeeDebeReportView.as_view(), name='employee_debe_report'),
    path('employeegain/', EmployeeGainReportView.as_view(), name='employee_gain_report'),
    path('salebyproduct/', SaleByProductReportView.as_view(), name='sale_by_product'),
]
