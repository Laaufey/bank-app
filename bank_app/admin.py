from django.contrib import admin
from .models import Account, Store, Ledger
from .models import Customer


admin.site.register(Account)
admin.site.register(Customer)
admin.site.register(Store)
admin.site.register(Ledger)

