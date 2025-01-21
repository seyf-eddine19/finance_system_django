import openpyxl
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from django.http import HttpResponse
from django.urls import reverse_lazy
from django.forms import HiddenInput
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.db.models import Sum, Count

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import User 
from django.contrib import messages

from .models import Loan, Covenant, Client, Budget, BudgetExpense, BudgetRevenue, Fund, FundExpense, FundRevenue
from .forms import LoanForm, CovenantForm, ClientForm, BudgetForm, BudgetRevenueForm, BudgetExpenseForm, FundForm, FundExpenseForm, FundRevenueForm, UserForm, ProfileForm
from .utils import get_loan_chart_data, get_covenant_chart_data, get_budget_revenue_chart_data

from django.contrib.auth import logout

def custom_403(request, exception):
    return render(request, '403.html', {}, status=403)

def custom_404(request, exception):
    return render(request, '404.html', {}, status=404)

def custom_500(request):
    return render(request, '500.html', status=500)

def dashboard(request):
    loans = Loan.objects.values('loan_type').annotate(
        total_amount=Sum('amount'),
        total_paid=Sum('paid_amount'),
        total_remaining=Sum('remaining_amount')
    )
    
    # Aggregate data
    total_loans = Loan.objects.aggregate(total_amount=Sum('amount'))['total_amount'] or 0
    total_covenants = Covenant.objects.aggregate(total_amount=Sum('amount'))['total_amount'] or 0
    total_funds = Fund.objects.aggregate(total_balance=Sum('current_balance'))['total_balance'] or 0
    total_clients = Client.objects.count()
    
    # Data for charts
    funds_revenue_data = FundRevenue.objects.values('category').annotate(total=Sum('amount')).order_by('-total')
    funds_expense_data = FundExpense.objects.values('category').annotate(total=Sum('amount')).order_by('-total')
    budgets_status_data = Budget.objects.values('status').annotate(count=Count('id'))

    # Prepare data for the charts
    revenue_categories = [item['category'] for item in funds_revenue_data]
    revenue_totals = [item['total'] for item in funds_revenue_data]
    expense_categories = [item['category'] for item in funds_expense_data]
    expense_totals = [item['total'] for item in funds_expense_data]
    budget_status_labels = [item['status'] for item in budgets_status_data]
    budget_status_counts = [item['count'] for item in budgets_status_data]

    context = {
        'loans': loans,
        'total_loans': total_loans,
        'total_covenants': total_covenants,
        'total_funds': total_funds,
        'total_clients': total_clients,
        'revenue_categories': revenue_categories,
        'revenue_totals': revenue_totals,
        'expense_categories': expense_categories,
        'expense_totals': expense_totals,
        'budget_status_labels': budget_status_labels,
        'budget_status_counts': budget_status_counts,
    }
    return render(request, 'dashboard.html', context)

@login_required
def index(request):
    context = {
        "total_loans": Loan.objects.aggregate(total=Sum('amount'))['total'] or 0,
        "total_covenants": Covenant.objects.aggregate(total=Sum('amount'))['total'] or 0,
        "total_funds": Fund.objects.aggregate(total=Sum('current_balance'))['total'] or 0,
        "total_budgets": Budget.objects.count(),
        "total_clients": Client.objects.count(),
        "recent_loans": Loan.objects.order_by('-date')[:5],
        "recent_covenants": Covenant.objects.order_by('-date')[:5],
    }
    return render(request, "dashboard.html", context)

@login_required
def index(request):
    # Metrics
    total_loans = float(Loan.objects.aggregate(total=Sum('amount'))['total'] or 0)
    total_covenants = float(Covenant.objects.aggregate(total=Sum('amount'))['total'] or 0)
    total_funds = float(Fund.objects.aggregate(total=Sum('current_balance'))['total'] or 0)

    # Loan Distribution Data
    loan_data = Loan.objects.values('loan_type').annotate(total=Sum('amount'))
    loan_types = [loan['loan_type'] for loan in loan_data]
    loan_amounts = [float(loan['total']) for loan in loan_data]

    # Fund Balance Data
    funds = Fund.objects.all()
    fund_dates = [fund.date.strftime('%Y-%m-%d') for fund in funds]
    fund_balances = [float(fund.current_balance) for fund in funds]

    # Bar Chart Data
    covenant_data = Covenant.objects.values('covenant_type').annotate(total_amount=Sum('amount'))
    bar_chart_categories = [entry['covenant_type'] for entry in covenant_data]
    bar_chart_covenants = [float(entry['total_amount']) for entry in covenant_data]
    bar_chart_loans = loan_amounts

    # Get user permissions
    user = request.user
    permissions = user.get_all_permissions()

    context = {
        'total_loans': total_loans,
        'total_covenants': total_covenants,
        'total_funds': total_funds,
        'loan_types': loan_types,
        'loan_amounts': loan_amounts,
        'fund_dates': fund_dates,
        'fund_balances': fund_balances,
        'bar_chart_categories': bar_chart_categories,
        'bar_chart_covenants': bar_chart_covenants,
        'bar_chart_loans': bar_chart_loans,

        'permissions': permissions
    }
    
    return render(request, 'index.html', context)


@login_required
def index(request):
    total_loans = Loan.objects.aggregate(
        total_amount=Sum('amount'),
        total_paid_amount=Sum('paid_amount'),
        total_remaining_amount=Sum('remaining_amount')
    )
    loan_chart_data = get_loan_chart_data()
    total_covenants = Covenant.objects.aggregate(
        total_amount=Sum('amount'),
        total_paid_amount=Sum('paid_amount'),
        total_remaining_amount=Sum('remaining_amount')
    )
    covenant_chart_data = get_covenant_chart_data()

    funds = Fund.objects.aggregate(
        total=Sum('current_balance'),
        count=Count('id'),
    )
    clients = Client.objects.aggregate(
        total=Sum('balance'),
        count=Count('id'),
    )

    budget_revenue_chart_data = get_budget_revenue_chart_data()
    budgetrevenues = BudgetRevenue.objects.aggregate(
        total_actual=Sum('actual_amount'),
        total_estimated=Sum('estimated_amount'),
    )
    budgetexpenses = BudgetExpense.objects.aggregate(
        total_actual=Sum('actual_amount'),
        total_estimated=Sum('estimated_amount'),
    )
    budgets = Budget.objects.aggregate(
        count=Count('name'),
    )

    context = {
        'amount_loans': total_loans['total_amount'] or 0,
        'paid_amount_loans': total_loans['total_paid_amount'] or 0,
        'remaining_amount_loans': total_loans['total_remaining_amount'] or 0,
        'loan_by_type': loan_chart_data['by_type'],
        'loan_by_user': loan_chart_data['by_user'],

        'amount_covenants': total_covenants['total_amount'] or 0,
        'paid_amount_covenants': total_covenants['total_paid_amount'] or 0,
        'remaining_amount_covenants': total_covenants['total_remaining_amount'] or 0,
        'covenant_by_type': covenant_chart_data['by_type'],
        'covenant_by_user': covenant_chart_data['by_user'],

        'funds_total': funds['total'] or 0,
        'funds_count': funds['count'] or 0,

        'clients_total': clients['total'] or 0,
        'clients_count': clients['count'] or 0,

        'budget_revenue_chart_data': budget_revenue_chart_data,

        # 'budgets_total': budgets['total'] or 0,
        'budgets_count': budgets['count'] or 0,
        'budgets_total': (budgetrevenues['total_actual'] or 0) - (budgetexpenses['total_actual'] or 0),
        'budgetrevenues_actual': budgetrevenues['total_actual'] or 0,
        'budgetrevenues_estimated': budgetrevenues['total_estimated'] or 0,
        'budgetexpenses_actual': budgetexpenses['total_actual'] or 0,
        'budgetexpenses_estimated': budgetexpenses['total_estimated'] or 0,
    }
    return render(request, 'index.html', context=context)

@login_required
def logout_view(request):
    logout(request)
    messages.success(request, 'تم تسجيل الخروج بنجاح!')
    return redirect('login')

# View for displaying and editing a user's profile
@login_required
def profile_view(request):
    user = request.user  # Get the currently logged-in user

    if request.method == 'POST':
        # If POST request, handle user form submission
        form = ProfileForm(request.POST, instance=user)
        password_form = PasswordChangeForm(request.user, request.POST)  # Password change form
        if form.is_valid():
            user = form.save(commit=False)
            user.save()  # Save the updated profile details
            # Display success message if any updates occurred
            messages.success(request, 'تم تحديث الملف الشخصي بنجاح!')
            return redirect('profile') 

            # Handle password change
        if password_form.is_valid() and password_form.has_changed():
            user = password_form.save()  # Save the password
            # Update session to keep the user logged in after password change
            update_session_auth_hash(request, user)

            # Display success message if any updates occurred
            messages.success(request, 'تم تحديث الملف الشخصي بنجاح!')
            return redirect('profile') 
    else:
        # If GET request, initialize the forms with the current user's data
        form = ProfileForm(instance=user)
        password_form = PasswordChangeForm(request.user)

    return render(request, 'users/profile.html', {
        'form': form,  # User information form
        'password_form': password_form,  # Password change form
        'user': user
    })

# User Views
@login_required
@permission_required('auth.view_user', raise_exception=True)
def user_list(request):
    users = User.objects.all()
    return render(request, 'users/user_list.html', {'users': users})

@login_required
@permission_required('auth.add_user', raise_exception=True)
def user_create(request):
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('user_list')
    else:
        form = UserForm()
    return render(request, 'users/user_form.html', {'form': form})

@login_required
@permission_required('auth.change_user', raise_exception=True)
def user_update(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        form = UserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('user_list')
    else:
        form = UserForm(instance=user)
    return render(request, 'users/user_form.html', {'form': form, 'user_update': user})

@login_required
@permission_required('auth.delete_user', raise_exception=True)
def user_delete(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        user.delete()
        return redirect('user_list')
    return render(request, 'users/delete_user.html', {'user': user})

# Permission Required
class PermissionMixin(PermissionRequiredMixin):
    def has_permission(self):
        perms = self.get_permission_required()
        print(self.request.user.has_perms(perms))
        return self.request.user.has_perms(perms) or self.request.user.is_superuser

# Loan Views
class LoanListView(PermissionMixin, ListView):
    model = Loan
    template_name = 'loans/loan_list.html'
    context_object_name = 'loans'
    permission_required = 'core.view_loan'

class LoanDetailView(PermissionMixin, DetailView):
    model = Loan
    template_name = 'loans/loan_detail.html'
    permission_required = 'core.view_loan'

class LoanCreateView(PermissionMixin, CreateView):
    model = Loan
    form_class = LoanForm
    # fields = ['user', 'loan_type', 'amount', 'paid_amount', 'date']
    template_name = 'loans/loan_form.html'
    success_url = reverse_lazy('loan_list')
    permission_required = 'core.add_loan'

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'تم إضافة السلفة بنجاح.')
        return response

    def form_invalid(self, form):
        messages.error(self.request, 'حدث خطأ أثناء إضافة السلفة. يرجى المحاولة مرة أخرى.')
        return super().form_invalid(form)

    def get_form(self):
        form = super().get_form()
        form.fields['remaining_amount'].widget = HiddenInput()
        return form
    
class LoanUpdateView(PermissionMixin, UpdateView):
    model = Loan
    form_class = LoanForm
    template_name = 'loans/loan_form.html'
    success_url = reverse_lazy('loan_list')
    permission_required = 'core.change_loan'

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'تم تحديث السلفة بنجاح.')
        return response

    def form_invalid(self, form):
        messages.error(self.request, 'حدث خطأ أثناء تحديث السلفة. يرجى المحاولة مرة أخرى.')
        return super().form_invalid(form)

    def get_form(self):
        form = super().get_form()
        # لجعل حقل صاحب السلف غير قابل للتعديل عند التحديث
        form.fields['user'].disabled = True
        form.fields['remaining_amount'].disabled = True
        return form
    
class LoanDeleteView(PermissionMixin, DeleteView):
    model = Loan
    template_name = 'loans/loan_confirm_delete.html'
    success_url = reverse_lazy('loan_list')
    permission_required = 'core.delete_loan'

    def delete(self, request, *args, **kwargs):
        response = super().delete(request, *args, **kwargs)
        messages.success(request, 'تم حذف السلفة بنجاح.')
        return response

@login_required
def loan_export_excel(request):
    # إعداد استجابة لتصدير البيانات كـ Excel
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="loans.xlsx"'

    # إنشاء ملف Excel جديد
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Loans"

    # إضافة رؤوس الأعمدة
    ws.append(['صاحب السلفة', 'التاريخ', 'شكل السلفة', 'المبلغ', 'المتبقي', 'المبلغ المدفوع'])

    # إضافة البيانات من قاعدة البيانات
    loans = Loan.objects.all()
    for loan in loans:
        ws.append([loan.user, loan.date, loan.loan_type, loan.amount, loan.remaining_amount, loan.paid_amount])

    # حفظ الملف وإرساله في الاستجابة
    wb.save(response)
    return response

@login_required
def loan_export_pdf(request):
    # إعداد استجابة لتصدير البيانات كـ PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="loans.pdf"'

    # إنشاء مستند PDF
    p = canvas.Canvas(response, pagesize=letter)
    width, height = letter

    # إعداد الخطوط والعناوين
    p.setFont("Helvetica", 12)
    p.drawString(30, height - 40, "قائمة السلف")
    p.drawString(30, height - 60, "صاحب السلفة\tالتاريخ\tشكل السلفة\tالمبلغ\tالمتبقي\tالمبلغ المدفوع")

    # إضافة البيانات من قاعدة البيانات
    y_position = height - 80
    loans = Loan.objects.all()
    for loan in loans:
        p.drawString(30, y_position, f"{loan.user}\t{loan.date}\t{loan.loan_type}\t{loan.amount}\t{loan.remaining_amount}\t{loan.paid_amount}")
        y_position -= 20

    # إنهاء المستند وإرساله
    p.showPage()
    p.save()
    return response

# Covenant Views
class CovenantListView(PermissionMixin, ListView):
    model = Covenant
    form = CovenantForm()
    template_name = 'covenants/covenant_list.html'
    context_object_name = 'covenants'
    permission_required = 'core.view_covenant'

class CovenantDetailView(PermissionMixin, DetailView):
    model = Covenant
    template_name = 'covenants/covenant_detail.html'
    permission_required = 'core.view_covenant'

class CovenantCreateView(PermissionMixin, CreateView):
    model = Covenant
    form_class = CovenantForm
    # fields = ['user', 'covenant_type', 'amount', 'paid_amount', 'date']
    template_name = 'covenants/covenant_form.html'
    success_url = reverse_lazy('covenant_list')
    permission_required = 'core.add_covenant'

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'تم إضافة العهد بنجاح.')
        return response

    def form_invalid(self, form):
        messages.error(self.request, 'حدث خطأ أثناء إضافة العهد. يرجى المحاولة مرة أخرى.')
        return super().form_invalid(form)

    def get_form(self):
        form = super().get_form()
        form.fields['remaining_amount'].widget = HiddenInput()
        return form
    
class CovenantUpdateView(PermissionMixin, UpdateView):
    model = Covenant
    form_class = CovenantForm
    template_name = 'covenants/covenant_form.html'
    success_url = reverse_lazy('covenant_list')
    permission_required = 'core.change_covenant'

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'تم تحديث العهد بنجاح.')
        return response

    def form_invalid(self, form):
        messages.error(self.request, 'حدث خطأ أثناء تحديث العهد. يرجى المحاولة مرة أخرى.')
        return super().form_invalid(form)

    def get_form(self):
        form = super().get_form()
        # لجعل حقل صاحب السلف غير قابل للتعديل عند التحديث
        form.fields['user'].disabled = True
        form.fields['remaining_amount'].disabled = True
        return form
    
class CovenantDeleteView(PermissionMixin, DeleteView):
    model = Covenant
    template_name = 'covenants/covenant_confirm_delete.html'
    success_url = reverse_lazy('covenant_list')
    permission_required = 'core.delete_covenant'

    def delete(self, request, *args, **kwargs):
        response = super().delete(request, *args, **kwargs)
        messages.success(request, 'تم حذف العهد بنجاح.')
        return response


# Client Views
class ClientListView(PermissionMixin, ListView):
    model = Client
    template_name = 'clients/client_list.html'
    context_object_name = 'clients'
    permission_required = 'core.view_client'

class ClientDetailView(PermissionMixin, DetailView):
    model = Client
    template_name = 'clients/client_detail.html'
    permission_required = 'core.view_client'

class ClientCreateView(PermissionMixin, CreateView):
    model = Client
    form_class = ClientForm
    # fields = ['name', 'email', 'phone', 'type', 'category', 'join_date', 'balance']
    template_name = 'clients/client_form.html'
    success_url = reverse_lazy('client_list')
    permission_required = 'core.add_client'
 
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'تم إضافة العميل بنجاح.')
        return response

    def form_invalid(self, form):
        messages.error(self.request, 'حدث خطأ أثناء إضافة العميل. يرجى المحاولة مرة أخرى.')
        return super().form_invalid(form)

class ClientUpdateView(PermissionMixin, UpdateView):
    model = Client
    form_class = ClientForm
    template_name = 'clients/client_form.html'
    success_url = reverse_lazy('client_list')
    permission_required = 'core.change_client'

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'تم تحديث العميل بنجاح.')
        return response

    def form_invalid(self, form):
        messages.error(self.request, 'حدث خطأ أثناء تحديث العميل. يرجى المحاولة مرة أخرى.')
        return super().form_invalid(form)
    
class ClientDeleteView(PermissionMixin, DeleteView):
    model = Client
    template_name = 'clients/client_confirm_delete.html'
    success_url = reverse_lazy('client_list')
    permission_required = 'core.delete_client'

    def delete(self, request, *args, **kwargs):
        response = super().delete(request, *args, **kwargs)
        messages.success(request, 'تم حذف العميل بنجاح.')
        return response


# Budget Views
class BudgetView(PermissionMixin, View):
    template_name = 'budgets/budget_list.html'
    permission_required = 'core.view_budget'

    def get(self, request, *args, **kwargs):
        budgets = Budget.objects.all()
        form = BudgetForm()
        budget = None
        if 'pk' in kwargs:
            budget = get_object_or_404(Budget, pk=kwargs['pk'])
            form = BudgetForm(instance=budget)
        return render(request, self.template_name, {
            'budgets': budgets,
            'form': form,
            'budget': budget
        })

    def post(self, request, *args, **kwargs):
        if 'pk' in kwargs:
            budget = get_object_or_404(Budget, pk=kwargs['pk'])
            form = BudgetForm(request.POST, instance=budget)
        else:
            form = BudgetForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect('budget_list')

        budgets = Budget.objects.all()
        return render(request, self.template_name, {
            'budgets': budgets,
            'form': form
        })
    
class BudgetDetailView(PermissionMixin, DetailView):
    model = Budget
    template_name = 'budgets/budget_detail.html'
    context_object_name = 'budget'
    permission_required = 'core.view_budget'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['expenses'] = BudgetExpense.objects.filter(budget=self.object)
        context['revenues'] = BudgetRevenue.objects.filter(budget=self.object)
        expenses = BudgetExpense.objects.filter(budget=self.object)
        revenues = BudgetRevenue.objects.filter(budget=self.object)
        context['expenses'] = expenses
        context['revenues'] = revenues
        
        # Aggregate totals for expenses
        context['total_expenses_estimated'] = expenses.aggregate(total=Sum('estimated_amount'))['total'] or 0
        context['total_expenses_actual'] = expenses.aggregate(total=Sum('actual_amount'))['total'] or 0
        context['total_expenses_paid'] = expenses.aggregate(total=Sum('paid_amount'))['total'] or 0
        context['total_expenses_remaining'] = expenses.aggregate(total=Sum('remaining_amount'))['total'] or 0

        # Aggregate totals for revenues
        context['total_revenues_estimated'] = revenues.aggregate(total=Sum('estimated_amount'))['total'] or 0
        context['total_revenues_actual'] = revenues.aggregate(total=Sum('actual_amount'))['total'] or 0
        context['total_revenues_paid'] = revenues.aggregate(total=Sum('paid_amount'))['total'] or 0
        context['total_revenues_remaining'] = revenues.aggregate(total=Sum('remaining_amount'))['total'] or 0
        return context

class BudgetRevenuesChangeView(PermissionMixin, View):
    template_name = 'budgets/budget_revenues_change.html'
    permission_required = 'core.change_budget'

    def get(self, request, budget_pk):
        # Get the budget instance
        budget = get_object_or_404(Budget, pk=budget_pk)

        # Get the existing revenues for the budget
        revenues = BudgetRevenue.objects.filter(budget=budget)

        # Create a form instance for each revenue item
        revenue_forms = [
            BudgetRevenueForm(instance=revenue, prefix=f"revenue_{revenue.pk}") 
            for revenue in revenues
        ]


        # Add a form to add a new revenue
        revenue_form = BudgetRevenueForm()

        context = {
            'budget': budget,
            'revenue_forms': revenue_forms,
            'revenue_form': revenue_form,
        }

        return render(request, self.template_name, context)

    def post(self, request, budget_pk):
        # Get the budget instance
        budget = get_object_or_404(Budget, pk=budget_pk)

        # Check if a delete action is triggered
        if "delete_revenue" in request.POST:
            revenue_id = request.POST.get("delete_revenue")
            revenue = get_object_or_404(BudgetRevenue, pk=revenue_id, budget=budget)
            revenue.delete()
            return redirect('budget_revenues_change', budget_pk=budget.pk)

        # Get the existing revenues for the budget
        revenues = BudgetRevenue.objects.filter(budget=budget)

        # Create form instances for each revenue item
        revenue_forms = [
            BudgetRevenueForm(
                request.POST, 
                instance=revenue,
                prefix=f"revenue_{revenue.pk}"
            ) 
            for revenue in revenues
        ]

        # Create new revenue form to add new items
        revenue_form = BudgetRevenueForm(request.POST)

        # Update existing revenues
        for form in revenue_forms:
            if form.is_valid():
                form.save()

        # Add new revenue if valid
        if revenue_form.is_valid():
            new_revenue = revenue_form.save(commit=False)
            new_revenue.budget = budget
            new_revenue.save()

        # Redirect back to the same page with updated revenues
        return redirect('budget_revenues_change', budget_pk=budget.pk)
    
class BudgetExpensesChangeView(PermissionMixin, View):
    template_name = 'budgets/budget_expenses_change.html'
    permission_required = 'core.change_budget'

    def get(self, request, budget_pk):
        # Get the budget instance
        budget = get_object_or_404(Budget, pk=budget_pk)

        # Get the existing expenses for the budget
        expenses = BudgetExpense.objects.filter(budget=budget)

        # Create a form instance for each expense item with unique prefixes
        expense_forms = [
            BudgetExpenseForm(instance=expense, prefix=f"expense_{expense.pk}")
            for expense in expenses
        ]

        # Add a form to add a new expense
        expense_form = BudgetExpenseForm(prefix="new_expense")

        context = {
            'budget': budget,
            'expense_forms': expense_forms,
            'expense_form': expense_form,
        }

        return render(request, self.template_name, context)

    def post(self, request, budget_pk):
        # Get the budget instance
        budget = get_object_or_404(Budget, pk=budget_pk)

        # Check if a delete action is triggered
        if "delete_expense" in request.POST:
            expense_id = request.POST.get("delete_expense")
            expense = get_object_or_404(BudgetExpense, pk=expense_id, budget=budget)
            expense.delete()
            return redirect('budget_expenses_change', budget_pk=budget.pk)

        # Get the existing expenses for the budget
        expenses = BudgetExpense.objects.filter(budget=budget)

        # Create form instances for each expense item with unique prefixes
        expense_forms = [
            BudgetExpenseForm(
                request.POST,
                instance=expense,
                prefix=f"expense_{expense.pk}"
            )
            for expense in expenses
        ]

        # Create a new expense form to add new items
        expense_form = BudgetExpenseForm(request.POST, prefix="new_expense")

        # Flag to check if all forms are valid
        all_valid = all(form.is_valid() for form in expense_forms)

        # Update existing expenses if all forms are valid
        if all_valid:
            for form in expense_forms:
                form.save()

        # Add a new expense if valid
        if expense_form.is_valid():
            new_expense = expense_form.save(commit=False)
            new_expense.budget = budget
            new_expense.save()

        # Redirect back to the same page with updated expenses
        return redirect('budget_expenses_change', budget_pk=budget.pk)


# Fund Views
class FundView(PermissionMixin, View):
    template_name = 'funds/fund_list.html'
    permission_required = 'core.view_fund'

    def get(self, request, *args, **kwargs):
        funds = Fund.objects.all()
        form = FundForm()
        fund = None
        if 'pk' in kwargs:
            fund = get_object_or_404(Fund, pk=kwargs['pk'])
            form = FundForm(instance=fund)
        return render(request, self.template_name, {
            'funds': funds,
            'form': form,
            'fund': fund
        })

    def post(self, request, *args, **kwargs):
        if 'pk' in kwargs:
            fund = get_object_or_404(Fund, pk=kwargs['pk'])
            form = FundForm(request.POST, instance=fund)
        else:
            form = FundForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect('fund_list')

        funds = Fund.objects.all()
        return render(request, self.template_name, {
            'funds': funds,
            'form': form
        })
    
class FundDetailView(LoginRequiredMixin, DetailView):
    model = Fund
    template_name = 'funds/fund_detail.html'
    permission_required = 'core.view_fund'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['expenses'] = FundExpense.objects.filter(fund=self.object)
        context['revenues'] = FundRevenue.objects.filter(fund=self.object)
        expenses = FundExpense.objects.filter(fund=self.object)
        revenues = FundRevenue.objects.filter(fund=self.object)
        context['expenses'] = expenses
        context['revenues'] = revenues
        
        # Aggregate totals for expenses
        context['total_expenses'] = expenses.aggregate(total=Sum('amount'))['total'] or 0
        
        # Aggregate totals for revenues
        context['total_revenues'] = revenues.aggregate(total=Sum('amount'))['total'] or 0
        return context

class FundRevenuesChangeView(PermissionMixin, View):
    template_name = 'funds/fund_revenues_change.html'
    permission_required = 'core.change_fund'

    def get(self, request, fund_pk):
        # Get the fund instance
        fund = get_object_or_404(Fund, pk=fund_pk)

        # Get the existing revenues for the fund
        revenues = FundRevenue.objects.filter(fund=fund)

        # Create a form instance for each revenue item
        revenue_forms = [
            FundRevenueForm(instance=revenue, prefix=f"revenue_{revenue.pk}") 
            for revenue in revenues
        ]


        # Add a form to add a new revenue
        revenue_form = FundRevenueForm()

        context = {
            'fund': fund,
            'revenue_forms': revenue_forms,
            'revenue_form': revenue_form,
        }

        return render(request, self.template_name, context)

    def post(self, request, fund_pk):
        # Get the fund instance
        fund = get_object_or_404(Fund, pk=fund_pk)

        # Check if a delete action is triggered
        if "delete_revenue" in request.POST:
            revenue_id = request.POST.get("delete_revenue")
            revenue = get_object_or_404(FundRevenue, pk=revenue_id, fund=fund)
            revenue.delete()
            return redirect('fund_revenues_change', fund_pk=fund.pk)

        # Get the existing revenues for the fund
        revenues = FundRevenue.objects.filter(fund=fund)

        # Create form instances for each revenue item
        revenue_forms = [
            FundRevenueForm(
                request.POST, 
                instance=revenue,
                prefix=f"revenue_{revenue.pk}"
            ) 
            for revenue in revenues
        ]

        # Create new revenue form to add new items
        revenue_form = FundRevenueForm(request.POST)

        # Update existing revenues
        for form in revenue_forms:
            if form.is_valid():
                form.save()

        # Add new revenue if valid
        if revenue_form.is_valid():
            new_revenue = revenue_form.save(commit=False)
            new_revenue.fund = fund
            new_revenue.save()

        # Redirect back to the same page with updated revenues
        return redirect('fund_revenues_change', fund_pk=fund.pk)
    
class FundExpensesChangeView(PermissionMixin, View):
    template_name = 'funds/fund_expenses_change.html'
    permission_required = 'core.change_fund'

    def get(self, request, fund_pk):
        # Get the fund instance
        fund = get_object_or_404(Fund, pk=fund_pk)

        # Get the existing expenses for the fund
        expenses = FundExpense.objects.filter(fund=fund)

        # Create a form instance for each expense item with unique prefixes
        expense_forms = [
            FundExpenseForm(instance=expense, prefix=f"expense_{expense.pk}")
            for expense in expenses
        ]

        # Add a form to add a new expense
        expense_form = FundExpenseForm(prefix="new_expense")

        context = {
            'fund': fund,
            'expense_forms': expense_forms,
            'expense_form': expense_form,
        }

        return render(request, self.template_name, context)

    def post(self, request, fund_pk):
        # Get the fund instance
        fund = get_object_or_404(Fund, pk=fund_pk)

        # Check if a delete action is triggered
        if "delete_expense" in request.POST:
            expense_id = request.POST.get("delete_expense")
            expense = get_object_or_404(FundExpense, pk=expense_id, fund=fund)
            expense.delete()
            return redirect('fund_expenses_change', fund_pk=fund.pk)

        # Get the existing expenses for the fund
        expenses = FundExpense.objects.filter(fund=fund)

        # Create form instances for each expense item with unique prefixes
        expense_forms = [
            FundExpenseForm(
                request.POST,
                instance=expense,
                prefix=f"expense_{expense.pk}"
            )
            for expense in expenses
        ]

        # Create a new expense form to add new items
        expense_form = FundExpenseForm(request.POST, prefix="new_expense")

        # Flag to check if all forms are valid
        all_valid = all(form.is_valid() for form in expense_forms)

        # Update existing expenses if all forms are valid
        if all_valid:
            for form in expense_forms:
                form.save()

        # Add a new expense if valid
        if expense_form.is_valid():
            new_expense = expense_form.save(commit=False)
            new_expense.fund = fund
            new_expense.save()

        # Redirect back to the same page with updated expenses
        return redirect('fund_expenses_change', fund_pk=fund.pk)

class FundDeleteView(LoginRequiredMixin, DeleteView):
    model = Fund
    template_name = 'fund_confirm_delete.html'
    success_url = reverse_lazy('fund_list')
    permission_required = 'core.delete_fund'

