import openpyxl
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from django.http import HttpResponse
from django.urls import reverse_lazy
from django.forms import HiddenInput
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.db.models import Sum, Count, Value

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import update_session_auth_hash, logout
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import User 
from django.contrib import messages

from .models import Loan, Covenant, Client, Budget, BudgetExpense, BudgetRevenue, Fund, FundExpense, FundRevenue
from .forms import LoanForm, CovenantForm, ClientForm, BudgetForm, BudgetRevenueForm, BudgetExpenseForm, FundForm, FundExpenseForm, FundRevenueForm, UserForm, ProfileForm
from .forms import ClientPhoneFormSet, ClientEmailFormSet, ClientDocumentFormSet
from .forms import LoanFilterForm, CovenantFilterForm, ClientFilterForm, FundFilterForm, FundExpenseFilterForm, FundRevenueFilterForm
from .utils import get_loan_chart_data, get_covenant_chart_data, get_budget_revenue_chart_data

def custom_403(request, exception):
    return render(request, '403.html', {}, status=403)

def custom_404(request, exception):
    return render(request, '404.html', {}, status=404)

def custom_500(request):
    return render(request, '500.html', status=500)

@login_required
def index(request):
    total_loans = Loan.objects.aggregate(
        total_amount=Sum('amount', default=Value(0)),
        total_paid_amount=Sum('paid_amount', default=Value(0)),
        total_remaining_amount=Sum('remaining_amount', default=Value(0)),
    )
    loan_chart_data = get_loan_chart_data()

    total_covenants = Covenant.objects.aggregate(
        total_amount=Sum('amount', default=Value(0)),
        total_paid_amount=Sum('paid_amount', default=Value(0)),
        total_remaining_amount=Sum('remaining_amount', default=Value(0)),
    )
    covenant_chart_data = get_covenant_chart_data()

    funds = Fund.objects.aggregate(
        total=Sum('current_balance', default=Value(0)),
        count=Count('id'),
    )
    clients = Client.objects.aggregate(
        total=Sum('balance', default=Value(0)),
        count=Count('id'),
    )

    budget_revenue_chart_data = get_budget_revenue_chart_data()
    budgetrevenues = BudgetRevenue.objects.aggregate(
        total_actual=Sum('actual_amount', default=Value(0)),
        total_estimated=Sum('estimated_amount', default=Value(0)),
    )
    budgetexpenses = BudgetExpense.objects.aggregate(
        total_actual=Sum('actual_amount', default=Value(0)),
        total_estimated=Sum('estimated_amount', default=Value(0)),
    )
    budgets = Budget.objects.aggregate(
        count=Count('name'),
    )

    context = {
        'amount_loans': "{:,.2f}".format(total_loans['total_amount']),
        'paid_amount_loans': "{:,.2f}".format(total_loans['total_paid_amount']),
        'remaining_amount_loans': "{:,.2f}".format(total_loans['total_remaining_amount']),
        'loan_by_type': loan_chart_data['by_type'],
        'loan_by_owner': loan_chart_data['by_owner'],

        'amount_covenants': "{:,.2f}".format(total_covenants['total_amount']),
        'paid_amount_covenants': "{:,.2f}".format(total_covenants['total_paid_amount']),
        'remaining_amount_covenants': "{:,.2f}".format(total_covenants['total_remaining_amount']),
        'covenant_by_type': covenant_chart_data['by_type'],
        'covenant_by_owner': covenant_chart_data['by_owner'],

        'funds_total': "{:,.2f}".format(funds['total']),
        'funds_count': funds['count'],

        'clients_total': "{:,.2f}".format(clients['total']),
        'clients_count': clients['count'],

        'budget_revenue_chart_data': budget_revenue_chart_data,
        'budgets_count': budgets['count'],
        'budgets_total': "{:,.2f}".format((budgetrevenues['total_actual'] or 0) - (budgetexpenses['total_actual'] or 0)),
        'budgetrevenues_actual': "{:,.2f}".format(budgetrevenues['total_actual']),
        'budgetrevenues_estimated': "{:,.2f}".format(budgetrevenues['total_estimated']),
        'budgetexpenses_actual': "{:,.2f}".format(budgetexpenses['total_actual']),
        'budgetexpenses_estimated': "{:,.2f}".format(budgetexpenses['total_estimated']),
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

# Permission Required
class PermissionMixin(PermissionRequiredMixin):
    def has_permission(self):
        perms = self.get_permission_required()
        return self.request.user.has_perms(perms) or self.request.user.is_superuser

# Loan Views
class LoanListView(PermissionMixin, ListView):
    model = Loan
    template_name = 'loans/loan_list.html'
    context_object_name = 'loans'
    permission_required = 'core.view_loan'

    def get_queryset(self):
        queryset = super().get_queryset()
        owner_filter = self.request.GET.get('owner')
        loan_type_filter = self.request.GET.get('loan_type')
        date_filter = self.request.GET.get('date')

        if owner_filter:
            queryset = queryset.filter(loan_owner=owner_filter)
        if loan_type_filter:
            queryset = queryset.filter(loan_type=loan_type_filter)
        if date_filter:
            queryset = queryset.filter(date=date_filter)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter_form'] = LoanFilterForm(self.request.GET)
        return context

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
        # form.fields['loan_owner'].disabled = True
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


# Covenant Views
class CovenantListView(PermissionMixin, ListView):
    model = Covenant
    form = CovenantForm()
    template_name = 'covenants/covenant_list.html'
    context_object_name = 'covenants'
    permission_required = 'core.view_covenant'

    def get_queryset(self):
        queryset = super().get_queryset()
        owner_filter = self.request.GET.get('owner')
        covenant_type_filter = self.request.GET.get('covenant_type')
        date_filter = self.request.GET.get('date')

        if owner_filter:
            queryset = queryset.filter(covenant_owner=owner_filter)
        if covenant_type_filter:
            queryset = queryset.filter(covenant_type=covenant_type_filter)
        if date_filter:
            queryset = queryset.filter(date=date_filter)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter_form'] = CovenantFilterForm(self.request.GET)
        return context

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
    
    def get_form(self):
        # Get the form
        form = super().get_form()

        # Dynamically fetch the last covenant types
        last_covenant_types = Covenant.objects.values_list('covenant_type', flat=True).distinct()
        
        # Set the choices for the covenant_type field
        form.fields['covenant_type'].widget.choices = [(type, type) for type in last_covenant_types]

        # Hide the remaining_amount field
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
        # form.fields['covenant_owner'].disabled = True
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

    def get_queryset(self):
        queryset = super().get_queryset()
        name_filter = self.request.GET.get('name')
        type_filter = self.request.GET.get('type')
        category_filter = self.request.GET.get('category')
        date_filter = self.request.GET.get('date')

        if name_filter:
            queryset = queryset.filter(name=name_filter)
        if type_filter:
            queryset = queryset.filter(type=type_filter)
        if category_filter:
            queryset = queryset.filter(category=category_filter)
        if date_filter:
            queryset = queryset.filter(date=date_filter)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter_form'] = ClientFilterForm(self.request.GET)
        return context

class ClientDetailView(PermissionMixin, DetailView):
    model = Client
    template_name = 'clients/client_detail.html'
    permission_required = 'core.view_client'

    def get_object(self):
        client = super().get_object()

        # Debugging line
        filtered_revenue = client.budget_revenues.filter(remaining_amount__gt=0)
        print(f"Filtered revenues for client {client.id}: {filtered_revenue}")
        
        # Add the filtered revenues to the client object
        client.filtered_revenue = filtered_revenue
        
        return client
    
class ClientDeleteView(PermissionMixin, DeleteView):
    model = Client
    template_name = 'clients/client_confirm_delete.html'
    success_url = reverse_lazy('client_list')
    permission_required = 'core.delete_client'

    def delete(self, request, *args, **kwargs):
        response = super().delete(request, *args, **kwargs)
        messages.success(request, 'تم حذف العميل بنجاح.')
        return response

class ClientFormView(PermissionMixin, CreateView, UpdateView):
    model = Client
    form_class = ClientForm
    template_name = 'clients/client_form.html'
    success_url = reverse_lazy('client_list')

    def get_object(self, queryset=None):
        """Return None for create, existing instance for update."""
        pk = self.kwargs.get('pk')
        if pk:
            return get_object_or_404(Client, pk=pk)
        return None

    def has_permission(self):
        """Check user permissions dynamically based on action."""
        client = self.get_object()
        if client:
            return self.request.user.has_perm('core.change_client')
        return self.request.user.has_perm('core.add_client')

    def get_context_data(self, **kwargs):
        """Add phone, email, and document formsets to the context."""
        context = super().get_context_data(**kwargs)
        instance = self.get_object()

        # Initialize formsets
        if self.request.POST:
            context['phone_formset'] = ClientPhoneFormSet(self.request.POST, instance=instance)
            context['email_formset'] = ClientEmailFormSet(self.request.POST, instance=instance)
            context['document_formset'] = ClientDocumentFormSet(self.request.POST, self.request.FILES, instance=instance)
            
        else:
            context['phone_formset'] = ClientPhoneFormSet(instance=instance)
            context['email_formset'] = ClientEmailFormSet(instance=instance)
            context['document_formset'] = ClientDocumentFormSet(instance=instance)

        return context

    def form_valid(self, form):
        """Validate main form and related formsets."""
        context = self.get_context_data()
        phone_formset = context['phone_formset']
        email_formset = context['email_formset']
        document_formset = context['document_formset']

        if form.is_valid() and phone_formset.is_valid() and email_formset.is_valid() and document_formset.is_valid():
            self.object = form.save()

            phone_formset.instance = self.object
            email_formset.instance = self.object
            document_formset.instance = self.object

            phone_instances = phone_formset.save(commit=False)
            email_instances = email_formset.save(commit=False)
            document_instances = document_formset.save(commit=False)

            for form in phone_formset:
                if form.cleaned_data.get('DELETE', False):  # Check delete flag
                    form.instance.delete()
                else:
                    form.save()
            
            for form in email_formset:
                if form.cleaned_data.get('DELETE', False):  # Check delete flag
                    form.instance.delete()
                else:
                    form.save()
            
            for form in document_formset:
                if form.cleaned_data.get('DELETE', False):  # Check delete flag
                    form.instance.delete()
                else:
                    form.save()

            phone_formset.save_m2m()
            email_formset.save_m2m()
            document_formset.save_m2m()

            messages.success(self.request, "تم حفظ البيانات بنجاح.")
            return super().form_valid(form)  # Ensure this is always returned
        else:
            # Show specific validation errors
            if not phone_formset.is_valid():
                messages.error(self.request, f"حدث خطأ أثناء حفظ أرقام الهاتف: {phone_formset.errors}")
            if not email_formset.is_valid():
                messages.error(self.request, f"حدث خطأ أثناء حفظ البريد الإلكتروني: {email_formset.errors}")
            if not document_formset.is_valid():
                messages.error(self.request, f"حدث خطأ أثناء حفظ المستندات: {document_formset.errors}")

            return self.form_invalid(form)  # Ensure this is also consistently returned

    def form_invalid(self, form):
        """Handle invalid form submissions."""
        messages.error(self.request, "حدث خطأ أثناء حفظ البيانات. يرجى التحقق من المدخلات.")
        return super().form_invalid(form)

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
        expenses = BudgetExpense.objects.filter(budget=self.object)
        revenues = BudgetRevenue.objects.filter(budget=self.object)

        # Aggregate totals for expenses
        total_expenses_estimated = expenses.aggregate(total=Sum('estimated_amount'))['total'] or 0
        total_expenses_actual = expenses.aggregate(total=Sum('actual_amount'))['total'] or 0
        total_expenses_paid = expenses.aggregate(total=Sum('paid_amount'))['total'] or 0
        total_expenses_remaining = expenses.aggregate(total=Sum('remaining_amount'))['total'] or 0

        # Aggregate totals for revenues
        total_revenues_estimated = revenues.aggregate(total=Sum('estimated_amount'))['total'] or 0
        total_revenues_actual = revenues.aggregate(total=Sum('actual_amount'))['total'] or 0
        total_revenues_paid = revenues.aggregate(total=Sum('paid_amount'))['total'] or 0
        total_revenues_remaining = revenues.aggregate(total=Sum('remaining_amount'))['total'] or 0

        # Calculate surplus before formatting
        estimated_surplus = total_revenues_estimated - total_expenses_estimated
        actual_surplus = total_revenues_actual - total_expenses_actual

        # Format values for display
        context.update({
            'expenses': expenses,
            'revenues': revenues,
            'total_expenses_estimated': "{:,.2f}".format(total_expenses_estimated),
            'total_expenses_actual': "{:,.2f}".format(total_expenses_actual),
            'total_expenses_paid': "{:,.2f}".format(total_expenses_paid),
            'total_expenses_remaining': "{:,.2f}".format(total_expenses_remaining),
            'total_revenues_estimated': "{:,.2f}".format(total_revenues_estimated),
            'total_revenues_actual': "{:,.2f}".format(total_revenues_actual),
            'total_revenues_paid': "{:,.2f}".format(total_revenues_paid),
            'total_revenues_remaining': "{:,.2f}".format(total_revenues_remaining),
            'estimated_surplus': estimated_surplus,
            'formatted_estimated_surplus': "{:,.2f}".format(estimated_surplus),
            'actual_surplus': actual_surplus,
            'formatted_actual_surplus': "{:,.2f}".format(actual_surplus),
        })
        
        return context

class BudgetRevenueCreateView(PermissionMixin, CreateView):
    model = BudgetRevenue
    form_class = BudgetRevenueForm
    # fields = ['name', 'email', 'phone', 'type', 'category', 'join_date', 'balance']
    template_name = 'budgets/budget_revenue_form.html'
    success_url = reverse_lazy('budget_list')
    permission_required = 'core.add_budgetrevenue'
 
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['budget'] = get_object_or_404(Budget, pk=self.kwargs['budget_pk'])
        return context
    
    def get_success_url(self):
        return reverse_lazy('budget_detail', kwargs={'pk': self.kwargs['budget_pk']})

    def form_valid(self, form):
        budget = get_object_or_404(Budget, pk=self.kwargs['budget_pk'])
        form.instance.budget = budget
        response = super().form_valid(form)
        messages.success(self.request, 'تم إضافة الايراد بنجاح.')
        return response

    def form_invalid(self, form):
        messages.error(self.request, 'حدث خطأ أثناء إضافة الايراد. يرجى المحاولة مرة أخرى.')
        return super().form_invalid(form)
    
class BudgetRevenueUpdateView(PermissionMixin, UpdateView):
    model = BudgetRevenue
    form_class = BudgetRevenueForm
    template_name = 'budgets/budget_revenue_form.html'
    success_url = reverse_lazy('budget_list')
    permission_required = 'core.change_budgetrevenue'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['budget'] = get_object_or_404(Budget, pk=self.kwargs['budget_pk'])
        return context
    
    def get_success_url(self):
        return reverse_lazy('budget_detail', kwargs={'pk': self.kwargs['budget_pk']})

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'تم تحديث الايراد بنجاح.')
        return response

    def form_invalid(self, form):
        messages.error(self.request, 'حدث خطأ أثناء تحديث الايراد. يرجى المحاولة مرة أخرى.')
        return super().form_invalid(form)
    
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

class BudgetExpenseCreateView(PermissionMixin, CreateView):
    model = BudgetExpense
    form_class = BudgetExpenseForm
    template_name = 'budgets/budget_expense_form.html'
    success_url = reverse_lazy('budget_list')
    permission_required = 'core.add_budgetexpense'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['budget'] = get_object_or_404(Budget, pk=self.kwargs['budget_pk'])
        return context

    def get_success_url(self):
        return reverse_lazy('budget_detail', kwargs={'pk': self.kwargs['budget_pk']})

    def form_valid(self, form):
        budget = get_object_or_404(Budget, pk=self.kwargs['budget_pk'])
        form.instance.budget = budget
        response = super().form_valid(form)
        messages.success(self.request, 'تم إضافة المصروف بنجاح.')
        return response

    def form_invalid(self, form):
        messages.error(self.request, 'حدث خطأ أثناء إضافة المصروف. يرجى المحاولة مرة أخرى.')
        return super().form_invalid(form)

class BudgetExpenseUpdateView(PermissionMixin, UpdateView):
    model = BudgetExpense
    form_class = BudgetExpenseForm
    template_name = 'budgets/budget_expense_form.html'
    success_url = reverse_lazy('budget_list')
    permission_required = 'core.change_budgetexpense'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['budget'] = get_object_or_404(Budget, pk=self.kwargs['budget_pk'])
        return context

    def get_success_url(self):
        return reverse_lazy('budget_detail', kwargs={'pk': self.kwargs['budget_pk']})

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'تم تحديث المصروف بنجاح.')
        return response

    def form_invalid(self, form):
        messages.error(self.request, 'حدث خطأ أثناء تحديث المصروف. يرجى المحاولة مرة أخرى.')
        return super().form_invalid(form)


# Fund Views
class FundView(PermissionMixin, View):
    template_name = 'funds/fund_list.html'
    permission_required = 'core.view_fund'

    def get(self, request, *args, **kwargs):
        # عرض جميع الصناديق إذا كان المستخدم مشرفًا، وإلا يعرض الصناديق الخاصة به فقط
        if request.user.has_perm('core.viewprivate_funds'):
            funds = Fund.objects.all()
        elif request.user.has_perm('core.viewall_funds'):
            funds = Fund.objects.filter(is_private=False)
        else:
            funds = Fund.objects.filter(user=request.user, is_private=False)

        # Apply additional filters from GET parameters
        user_filter = request.GET.get('user')
        name_filter = request.GET.get('name')
        date_filter = request.GET.get('date')

        if name_filter:
            funds = funds.filter(name=name_filter)
        if user_filter:
            funds = funds.filter(user=user_filter)
        if date_filter:
            funds = funds.filter(date=date_filter)


        fund = None
        if 'pk' in kwargs:
            fund = get_object_or_404(funds, pk=kwargs['pk'])  # التأكد من أن المستخدم يمكنه رؤية الصندوق
            form = FundForm(instance=fund)
        else:
            initial_data = {'user': request.user} if not request.user.is_superuser else {}
            form = FundForm(initial=initial_data)

        # Add filtering functionality to the context
        filter_form = FundFilterForm(request.GET)
        context = {
            'funds': funds,
            'form': form,
            'fund': fund,
            'filter_form': filter_form
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        fund = None
        if 'pk' in kwargs:
            fund = get_object_or_404(Fund, pk=kwargs['pk'])
            form = FundForm(request.POST, instance=fund)
        else:
            form = FundForm(request.POST)

        if form.is_valid():
            fund = form.save(commit=False)
            if not request.user.is_superuser:
                fund.user = request.user  # تعيين المالك عند إنشاء الصندوق من قبل مستخدم عادي
            fund.save()
            return redirect('fund_list')  # Make sure 'fund_list' is the correct URL name

        # إعادة تحميل الصناديق بعد الخطأ
        if request.user.has_perm('core.viewprivate_funds'):
            funds = Fund.objects.all()
        elif request.user.has_perm('core.viewall_funds'):
            funds = Fund.objects.filter(is_private=False)
        else:
            funds = Fund.objects.filter(user=request.user, is_private=False)

        # Reapply filters after form submission
        filter_form = FundFilterForm(request.GET)
        context = {
            'funds': funds,
            'form': form,
            'filter_form': filter_form
        }
        return render(request, self.template_name, context)

class FundDetailView(PermissionMixin, DetailView):
    model = Fund
    template_name = 'funds/fund_detail.html'
    context_object_name = 'fund'
    permission_required = 'core.view_fund'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Initialize filter forms with the GET parameters
        expense_filter_form = FundExpenseFilterForm(self.request.GET)
        revenue_filter_form = FundRevenueFilterForm(self.request.GET)

        # Get the base querysets for expenses and revenues
        expenses = FundExpense.objects.filter(fund=self.object)
        revenues = FundRevenue.objects.filter(fund=self.object)

        # Apply filters to expenses if form is valid and filters are applied
        if expense_filter_form.is_valid():
            print(expense_filter_form.cleaned_data) 
            description = expense_filter_form.cleaned_data.get('expense_description')
            category = expense_filter_form.cleaned_data.get('expense_category')
            date = expense_filter_form.cleaned_data.get('expense_date')

            if description:
                expenses = expenses.filter(description=description)
            if category:
                expenses = expenses.filter(category=category)
            if date:
                expenses = expenses.filter(date=date)
        else:
            print(expense_filter_form.errors)

        # Apply filters to revenues if form is valid and filters are applied
        if revenue_filter_form.is_valid():
            description = revenue_filter_form.cleaned_data.get('revenue_description')
            category = revenue_filter_form.cleaned_data.get('revenue_category')
            date = revenue_filter_form.cleaned_data.get('revenue_date')

            if description:
                revenues = revenues.filter(description=description)
            if category:
                revenues = revenues.filter(category=category)
            if date:
                revenues = revenues.filter(date=date)
        else:
            print(revenue_filter_form.errors)

        # Aggregate totals for expenses and revenues
        total_expenses = expenses.aggregate(total=Sum('amount'))['total'] or 0
        total_revenues = revenues.aggregate(total=Sum('amount'))['total'] or 0

        # Add context for expenses, revenues, filter forms, and totals
        context['expenses'] = expenses
        context['revenues'] = revenues
        context['total_expenses'] = "{:,.2f}".format(total_expenses)
        context['total_revenues'] = "{:,.2f}".format(total_revenues)
        context['expense_filter_form'] = expense_filter_form
        context['revenue_filter_form'] = revenue_filter_form

        return context

class FundRevenueCreateView(PermissionMixin, CreateView):
    model = FundRevenue
    form_class = FundRevenueForm
    # fields = ['name', 'email', 'phone', 'type', 'category', 'join_date', 'balance']
    template_name = 'funds/fund_revenue_form.html'
    success_url = reverse_lazy('fund_list')
    permission_required = 'core.add_fundrevenue'
 
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['fund'] = get_object_or_404(Fund, pk=self.kwargs['fund_pk'])
        return context
    
    def get_success_url(self):
        return reverse_lazy('fund_detail', kwargs={'pk': self.kwargs['fund_pk']})

    def form_valid(self, form):
        fund = get_object_or_404(Fund, pk=self.kwargs['fund_pk'])
        form.instance.fund = fund
        response = super().form_valid(form)
        messages.success(self.request, 'تم إضافة الايراد بنجاح.')
        return response

    def form_invalid(self, form):
        messages.error(self.request, 'حدث خطأ أثناء إضافة الايراد. يرجى المحاولة مرة أخرى.')
        return super().form_invalid(form)
    
class FundRevenueUpdateView(PermissionMixin, UpdateView):
    model = FundRevenue
    form_class = FundRevenueForm
    template_name = 'funds/fund_revenue_form.html'
    success_url = reverse_lazy('fund_list')
    permission_required = 'core.change_fundrevenue'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['fund'] = get_object_or_404(Fund, pk=self.kwargs['fund_pk'])
        return context
    
    def get_success_url(self):
        return reverse_lazy('fund_detail', kwargs={'pk': self.kwargs['fund_pk']})

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'تم تحديث الايراد بنجاح.')
        return response

    def form_invalid(self, form):
        messages.error(self.request, 'حدث خطأ أثناء تحديث الايراد. يرجى المحاولة مرة أخرى.')
        return super().form_invalid(form)

class FundExpenseCreateView(PermissionMixin, CreateView):
    model = FundExpense
    form_class = FundExpenseForm
    template_name = 'funds/fund_expense_form.html'
    success_url = reverse_lazy('fund_list')
    permission_required = 'core.add_fundexpense'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['fund'] = get_object_or_404(Fund, pk=self.kwargs['fund_pk'])
        return context

    def get_success_url(self):
        return reverse_lazy('fund_detail', kwargs={'pk': self.kwargs['fund_pk']})

    def form_valid(self, form):
        fund = get_object_or_404(Fund, pk=self.kwargs['fund_pk'])
        form.instance.fund = fund
        response = super().form_valid(form)
        messages.success(self.request, 'تم إضافة المصروف بنجاح.')
        return response

    def form_invalid(self, form):
        messages.error(self.request, 'حدث خطأ أثناء إضافة المصروف. يرجى المحاولة مرة أخرى.')
        return super().form_invalid(form)

class FundExpenseUpdateView(PermissionMixin, UpdateView):
    model = FundExpense
    form_class = FundExpenseForm
    template_name = 'funds/fund_expense_form.html'
    success_url = reverse_lazy('fund_list')
    permission_required = 'core.change_fundexpense'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['fund'] = get_object_or_404(Fund, pk=self.kwargs['fund_pk'])
        return context

    def get_success_url(self):
        return reverse_lazy('fund_detail', kwargs={'pk': self.kwargs['fund_pk']})

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'تم تحديث المصروف بنجاح.')
        return response

    def form_invalid(self, form):
        messages.error(self.request, 'حدث خطأ أثناء تحديث المصروف. يرجى المحاولة مرة أخرى.')
        return super().form_invalid(form)

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

class FundDeleteView(PermissionMixin, DeleteView):
    model = Fund
    template_name = 'fund_confirm_delete.html'
    success_url = reverse_lazy('fund_list')
    permission_required = 'core.delete_fund'

