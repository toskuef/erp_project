from import_export.admin import ImportExportModelAdmin

from django.contrib import admin
from .models import *


@admin.register(Customer)
class CustomerAdmin(ImportExportModelAdmin):
    pass
#admin.site.register(Customer)
admin.site.register(SourceCustomer)
admin.site.register(Address)
admin.site.register(AddressCountry)
admin.site.register(AddressArea)
admin.site.register(AddressRegion)
admin.site.register(AddressTown)
admin.site.register(AddressStreet)
admin.site.register(Order)
admin.site.register(TypePay)
admin.site.register(StatusOrder)
admin.site.register(Comment)
admin.site.register(Product)
admin.site.register(Task)
admin.site.register(Measuring)
admin.site.register(TypeTask)
admin.site.register(SocialWebCustomers)

