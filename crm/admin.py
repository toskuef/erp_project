from import_export.admin import ImportExportModelAdmin

from django.contrib import admin
from .models import *


@admin.register(Customer)
class CustomerAdmin(ImportExportModelAdmin):
    pass


admin.site.register(SourceCustomer)


@admin.register(Address)
class AddressAdmin(ImportExportModelAdmin):
    pass


@admin.register(AddressCountry)
class AddressCountryAdmin(ImportExportModelAdmin):
    pass


@admin.register(AddressArea)
class AddressAreaAdmin(ImportExportModelAdmin):
    pass


@admin.register(AddressRegion)
class AddressRegionAdmin(ImportExportModelAdmin):
    pass


@admin.register(AddressTown)
class AddressTownAdmin(ImportExportModelAdmin):
    pass


@admin.register(AddressStreet)
class AddressStreetAdmin(ImportExportModelAdmin):
    pass


@admin.register(Order)
class OrderAdmin(ImportExportModelAdmin):
    pass


admin.site.register(TypePay)
admin.site.register(StatusOrder)
admin.site.register(Comment)


@admin.register(Product)
class ProductAdmin(ImportExportModelAdmin):
    pass


admin.site.register(Task)
admin.site.register(Measuring)
admin.site.register(TypeTask)
admin.site.register(SocialWebCustomers)
