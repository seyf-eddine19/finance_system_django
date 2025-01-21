from django.contrib import admin
from .models import Loan, Covenant, Fund, FundRevenue, FundExpense, Budget, BudgetExpense, BudgetRevenue, Client

admin.site.register(Loan)
admin.site.register(Covenant)
admin.site.register(Fund)
admin.site.register(FundRevenue)
admin.site.register(FundExpense)
admin.site.register(Budget)
admin.site.register(BudgetExpense)
admin.site.register(BudgetRevenue)
admin.site.register(Client)
