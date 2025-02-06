from django.contrib import admin
from .models import Loan, LoanHistory, Covenant, CovenantHistory, Fund, FundRevenue, FundExpense, Budget, BudgetExpense, BudgetRevenue, Client, ClientPhone, ClientEmail, ClientDocument 

from .models import (
    ClientType, ClientCategory, LoanType, CovenantType, 
    ExpenseCategory, RevenueCategory
)

admin.site.register(ClientType)
admin.site.register(ClientCategory)
admin.site.register(LoanType)
admin.site.register(CovenantType)
admin.site.register(ExpenseCategory)
admin.site.register(RevenueCategory)

class LoanHistoryInline(admin.TabularInline):
    model = LoanHistory
    extra = 0

class CovenantHistoryInline(admin.TabularInline):
    model = CovenantHistory
    extra = 0

class FundRevenueInline(admin.TabularInline):
    model = FundRevenue
    extra = 0

class FundExpenseInline(admin.TabularInline):
    model = FundExpense
    extra = 0

class BudgetRevenueInline(admin.TabularInline):
    model = BudgetRevenue
    extra = 0

class BudgetExpenseInline(admin.TabularInline):
    model = BudgetExpense
    extra = 0

class ClientPhoneInline(admin.TabularInline):
    model = ClientPhone
    extra = 0

class ClientEmailInline(admin.TabularInline):
    model = ClientEmail
    extra = 0

class ClientDocumentInline(admin.TabularInline):
    model = ClientDocument
    extra = 0

class LoanAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Loan._meta.fields]
    search_fields = []
    list_filter =[]
    inlines = [LoanHistoryInline]

class CovenantAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Covenant._meta.fields]
    search_fields = []
    list_filter =[]
    inlines = [CovenantHistoryInline]

class FundAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Fund._meta.fields]
    search_fields = []
    list_filter =[]
    inlines = [FundExpenseInline, FundRevenueInline]

class BudgetAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Budget._meta.fields]
    search_fields = []
    list_filter =[]
    inlines = [BudgetExpenseInline, BudgetRevenueInline]

class ClientAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Client._meta.fields]
    search_fields = []
    list_filter =[]
    inlines = [ClientPhoneInline, ClientEmailInline, ClientDocumentInline]


from django.contrib.auth.models import Permission
admin.site.register(Permission)

admin.site.register(Loan, LoanAdmin)
admin.site.register(Covenant, CovenantAdmin)
admin.site.register(Fund, FundAdmin)
admin.site.register(Budget, BudgetAdmin)
admin.site.register(Client, ClientAdmin)
