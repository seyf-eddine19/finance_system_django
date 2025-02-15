from django import forms
from django.apps import apps
from django.forms import inlineformset_factory
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User, Permission
from django_select2.forms import Select2Widget

from .models import (
    LoanType, CovenantType, ClientType, ClientCategory, ExpenseCategory, RevenueCategory,
    Loan, Covenant, Budget, BudgetExpense, BudgetRevenue, Fund, FundExpense, FundRevenue,
    Client, ClientDocument, ClientPhone, ClientEmail
)

class ClientTypeForm(forms.ModelForm):
    class Meta:
        model = ClientType
        fields = '__all__'
        
class ClientCategoryForm(forms.ModelForm):
    class Meta:
        model = ClientCategory
        fields = '__all__'
        
class LoanTypeForm(forms.ModelForm):
    class Meta:
        model = LoanType
        fields = '__all__'
        
class CovenantTypeForm(forms.ModelForm):
    class Meta:
        model = CovenantType
        fields = '__all__'
        
class ExpenseCategoryForm(forms.ModelForm):
    class Meta:
        model = ExpenseCategory
        fields = '__all__'
        
class RevenueCategoryForm(forms.ModelForm):
    class Meta:
        model = RevenueCategory
        fields = '__all__'
        
class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']  # Add other fields as needed
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'first_name': 'الاسم الأول',
            'last_name': 'الاسم الأخير',
            'email': 'البريد الإلكتروني',
        }

class PermissionField(forms.ModelMultipleChoiceField):
    """Custom field to display permissions in Arabic format."""
    PERMISSION_TRANSLATIONS = {
        "add": "إضافة",
        "change": "تعديل",
        "delete": "حذف",
        "view": "عرض",
    }

    def __init__(self, *args, **kwargs):
        kwargs['widget'] = forms.CheckboxSelectMultiple()  # Add custom class here
        super().__init__(*args, **kwargs)

    def label_from_instance(self, permission):
        """Customize label to use `verbose_name_plural` for model names."""
        app_label = permission.content_type.app_label
        model_name = permission.content_type.model
        action = permission.codename.split('_')[0]  # Extract action (add, change, delete, view)

        # Translate action
        action_arabic = self.PERMISSION_TRANSLATIONS.get(action, None)

        # Get model's verbose_name_plural
        model_class = apps.get_model(app_label, model_name)
        model_arabic = getattr(model_class._meta, "verbose_name_plural", model_name)
        if action_arabic:
            return f"{action_arabic} {model_arabic}" 
        else:
            if action == 'viewall':
                return f"عرض كل {model_arabic}" 
            elif action == 'viewprivate':
                return f"عرض {model_arabic} الخاصة"
            else:
                pass 

class UserForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput,
        required=True,
        label="كلمة المرور:"
        # help_text=""
    )
    
    # groups = forms.ModelMultipleChoiceField(
    #     queryset=Group.objects.all(),
    #     required=False,
    #     widget=forms.CheckboxSelectMultiple,
    #     label="المجموعات:",
    # )

    user_permissions = PermissionField(
        queryset=Permission.objects.filter(content_type__app_label='core'),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label="الصلاحيات الفردية:",
    )

    class Meta:
        model = User
        fields = [
            'username', 'password', 'first_name', 'last_name', 'email',
            'is_superuser', 'is_active', 'user_permissions'
        ]
        labels = {
            'is_superuser': 'صلاحيات المدير:',
        }
        help_texts = {
            # 'username': 'مطلوب. 150 رمزاً أو أقل، مكونة من حروف وأرقام و @/./+/-/_ فقط.',
            'username': '',
        }

        required = {
            'username': True,
            'password': True,
            'first_name': True,
            'last_name': True,
        }
        widgets = {
            # 'is_staff': forms.CheckboxInput(attrs={'class': 'custom-checkbox'}),
            'is_superuser': forms.CheckboxInput(attrs={'class': 'custom-checkbox'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'custom-checkbox'}),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        if self.cleaned_data['password']:
            user.password = make_password(self.cleaned_data['password'])
        if commit:
            user.save()
            self.save_m2m()  # Save many-to-many relationships (groups and permissions)
        return user

class LoanForm(forms.ModelForm):
    loan_type = forms.ModelChoiceField(
        queryset=LoanType.objects.all(),
        widget=Select2Widget,
        label="شكل السلف"
    )

    class Meta:
        model = Loan
        fields = "__all__"
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'})
        }

class CovenantForm(forms.ModelForm):
    covenant_type = forms.ModelChoiceField(
        queryset=CovenantType.objects.all(),
        widget=Select2Widget,
        label="شكل العهد"
    )

    class Meta:
        model = Covenant
        fields = '__all__'
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'})
        }

class BudgetForm(forms.ModelForm):
    users = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,  # Set to True if you want to make this field mandatory
        label="المستخدمون الذين يمكنهم العمل على الموازنة"
    )
    date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'month'}),
        input_formats=["%Y-%m"],
    )

    class Meta:
        model = Budget
        fields = '__all__'
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.initial['date'] = self.instance.date.strftime('%Y-%m')
            self.initial['users'] = self.instance.users.all()

class BudgetExpenseForm(forms.ModelForm):
    category = forms.ModelChoiceField(
        queryset=ExpenseCategory.objects.all(),
        widget=Select2Widget,
        label="فئة المصروف"
    )

    class Meta:
        model = BudgetExpense
        fields = ['description', 'category', 'estimated_amount', 'actual_amount', 'paid_amount', 'date', 'expense_status']
        can_delete=True
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'remaining_amount': forms.TextInput(attrs={'readonly': 'readonly'}),  
        }

class BudgetRevenueForm(forms.ModelForm):
    category = forms.ModelChoiceField(
        queryset=RevenueCategory.objects.all(),  
        widget=Select2Widget,
        label="فئة الإيراد"
    )

    class Meta:
        model = BudgetRevenue
        fields=['client', 'description', 'category', 'estimated_amount', 'actual_amount', 'paid_amount', 'date']
        can_delete=True
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'remaining_amount': forms.TextInput(attrs={'readonly': 'readonly'}),  
            "client": Select2Widget,
        }

class FundForm(forms.ModelForm):
    date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'month'}),
        input_formats=["%Y-%m"],  # السماح بإدخال السنة والشهر فقط
    )
    class Meta:
        model = Fund
        fields = ['user', 'name', 'description', 'opening_balance', 'is_private', 'date']

        widgets = {
            'date': forms.DateInput(attrs={'type': 'month'}),
            'current_balance': forms.TextInput(attrs={'readonly': 'readonly'}), 
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.initial['date'] = self.instance.date.strftime('%Y-%m')

class FundExpenseForm(forms.ModelForm):
    category = forms.ModelChoiceField(
        queryset=ExpenseCategory.objects.all(),
        widget=Select2Widget,
        label="فئة المصروف"
    )

    class Meta:
        model = FundExpense
        fields = ['description', 'category', 'amount', 'date']
        can_delete=True
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }

class FundRevenueForm(forms.ModelForm):
    category = forms.ModelChoiceField(
        queryset=RevenueCategory.objects.all(),  
        widget=Select2Widget,
        label="فئة الإيراد"
    )

    class Meta:
        model = FundRevenue
        fields = ['description', 'category', 'amount', 'date']
        can_delete=True
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'})
        }

class ClientForm(forms.ModelForm):
    type = forms.ModelChoiceField(
        queryset=ClientType.objects.all(),
        widget=Select2Widget,
        label="نوع العميل",
    )
    category = forms.ModelChoiceField(
        queryset=ClientCategory.objects.all(),
        widget=Select2Widget,
        label="فئة العميل",
    )
    
    class Meta:
        model = Client
        fields = '__all__'
        widgets = {
            'join_date': forms.DateInput(attrs={'type': 'date'})
        }

class ClientPhoneForm(forms.ModelForm):
    class Meta:
        model = ClientPhone
        fields = ['phone']

class ClientEmailForm(forms.ModelForm):
    class Meta:
        model = ClientEmail
        fields = ['email']

class ClientDocumentForm(forms.ModelForm):
    class Meta:
        model = ClientDocument
        fields = ['name', 'file']

# Inline Formsets for Client Relationships
ClientPhoneFormSet = inlineformset_factory(Client, ClientPhone, form=ClientPhoneForm, extra=0, can_delete=True)
ClientEmailFormSet = inlineformset_factory(Client, ClientEmail, form=ClientEmailForm, extra=0, can_delete=True)
ClientDocumentFormSet = inlineformset_factory(Client, ClientDocument, form=ClientDocumentForm, extra=0, can_delete=True)

class LoanFilterForm(forms.Form):
    owner = forms.ChoiceField(
        required=False,
        widget=Select2Widget(attrs={'data-placeholder': 'اختر صاحب السلفة', 'class': 'form-control'}),
        label="صاحب السلفة"
    )
    loan_type = forms.ModelChoiceField(
        queryset=LoanType.objects.all(),
        widget=Select2Widget(attrs={'data-placeholder': 'اختر النوع', 'class': 'form-control'}),
        required=False,
        label="النوع"
    )
    date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        label="التاريخ"
    )
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        owners = Loan.objects.values_list('loan_owner', flat=True).distinct()
        self.fields['owner'].choices = [("", "---------")] + [(o, o) for o in owners]

class CovenantFilterForm(forms.Form):
    owner = forms.ChoiceField(
        required=False,
        widget=Select2Widget(attrs={'data-placeholder': 'اختر صاحب العهد', 'class': 'form-control'}),
        label="صاحب العهد"
    )
    covenant_type = forms.ModelChoiceField(
        queryset=CovenantType.objects.all(),
        required=False,
        widget=Select2Widget(attrs={'data-placeholder': 'اختر النوع', 'class': 'form-control'}),
        label="النوع"
    )
    date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        label="التاريخ"
    )
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['owner'].choices = [(n, n) for n in Budget.objects.values_list('covenant_owner', flat=True).distinct() if n]  

class ClientFilterForm(forms.Form):
    name = forms.ChoiceField(
        widget=Select2Widget(attrs={'data-placeholder': 'اختر اسم العميل', 'class': 'form-control'}),
        label="اسم العميل",
        required=False
    )
    type = forms.ModelChoiceField(
        queryset=ClientType.objects.all(),
        widget=Select2Widget(attrs={'data-placeholder': 'اختر النوع', 'class': 'form-control'}),
        label="نوع العميل",
        required=False
    )
    category = forms.ModelChoiceField(
        queryset=ClientCategory.objects.all(),
        widget=Select2Widget(attrs={'data-placeholder': 'اختر الفئة', 'class': 'form-control'}),
        label="فئة العميل",
        required=False
    )
    date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        label="تاريخ الانضمام"
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].choices = [(n, n) for n in Client.objects.values_list('name', flat=True).distinct() if n]  


class FundFilterForm(forms.Form):
    user = forms.ModelChoiceField(
        queryset=User.objects.all(),  
        widget=Select2Widget(attrs={'data-placeholder': 'اختر الموضف', 'class': 'form-control'}),
        label="الموضف",
        required=False
    )
    name = forms.ChoiceField(
        widget=Select2Widget(attrs={'data-placeholder': 'اختر الصندوق', 'class': 'form-control'}),
        label="الصندوق",
        required=False
    ) 
    date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'month', 'class': 'form-control'}),
        label="التاريخ"
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].choices = [(n, n) for n in Budget.objects.values_list('name', flat=True).distinct() if n]  

class FundExpenseFilterForm(forms.Form):
    expense_description = forms.ChoiceField(
        widget=Select2Widget(attrs={'data-placeholder': 'اختر بيان المصروف', 'class': 'form-control', 'id': 'expense-description'}),
        label="بيان المصروف",
        required=False
    )
    expense_category = forms.ModelChoiceField(
        queryset=ExpenseCategory.objects.all(),
        widget=Select2Widget(attrs={'data-placeholder': 'اختر فئة المصروف', 'class': 'form-control', 'id': 'expense-category'}),
        label="فئة المصروف",
        required=False
    )
    expense_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control', 'id': 'expense-date'}),
        label="التاريخ"
    )
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['expense_description'].choices = [(n, n) for n in FundExpense.objects.values_list('description', flat=True).distinct() if n]  

class FundRevenueFilterForm(forms.Form):
    revenue_description = forms.ChoiceField(
        widget=Select2Widget(attrs={'data-placeholder': 'اختر بيان الايراد', 'class': 'form-control', 'id': 'revenue-description'}),
        label="بيان الايراد",
        required=False
    )
    revenue_category = forms.ModelChoiceField(
        queryset=LoanType.objects.all(),
        widget=Select2Widget(attrs={'data-placeholder': 'اختر فئة الايراد', 'class': 'form-control', 'id': 'revenue-category'}),
        label="فئة الايراد",
        required=False
    )
    revenue_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control', 'id': 'revenue-date'}),
        label="التاريخ"
    )
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['revenue_description'].choices = [(n, n) for n in FundRevenue.objects.values_list('description', flat=True).distinct() if n]  


class BudgetFilterForm(forms.Form):
    name = forms.ChoiceField(
        widget=Select2Widget(attrs={'data-placeholder': 'اختر الموازنة', 'class': 'form-control'}),
        label="الموازنة",
        required=False
    )  
    status = forms.ChoiceField(
        widget=Select2Widget(attrs={'data-placeholder': 'اختر الحالة', 'class': 'form-control'}),
        label="حالة الموازنة",
        required=False
    )  
    date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'month', 'class': 'form-control'}),
        label="التاريخ"
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].choices = [(n, n) for n in Budget.objects.values_list('name', flat=True).distinct() if n]  
        self.fields['status'].choices = [('فعلية', 'فعلية'), ('تقديرية', 'تقديرية')]

class BudgetExpenseFilterForm(forms.Form):
    expense_description = forms.ChoiceField(
        widget=Select2Widget(attrs={'data-placeholder': 'اختر بيان المصروف', 'class': 'form-control', 'id': 'expense-description'}),
        label="بيان المصروف",
        required=False
    )
    expense_category = forms.ModelChoiceField(
        queryset=ExpenseCategory.objects.all(),
        widget=Select2Widget(attrs={'data-placeholder': 'اختر فئة المصروف', 'class': 'form-control', 'id': 'expense-category'}),
        label="فئة المصروف",
        required=False
    )
    expense_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control', 'id': 'expense-date'}),
        label="التاريخ"
    )
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['expense_description'].choices = [(n, n) for n in BudgetExpense.objects.values_list('description', flat=True).distinct() if n]  

class BudgetRevenueFilterForm(forms.Form):
    revenue_description = forms.ChoiceField(
        widget=Select2Widget(attrs={'data-placeholder': 'اختر بيان الايراد', 'class': 'form-control', 'id': 'revenue-description'}),
        label="بيان الايراد",
        required=False
    )
    revenue_category = forms.ModelChoiceField(
        queryset=LoanType.objects.all(),
        widget=Select2Widget(attrs={'data-placeholder': 'اختر فئة الايراد', 'class': 'form-control', 'id': 'revenue-category'}),
        label="فئة الايراد",
        required=False
    )
    revenue_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control', 'id': 'revenue-date'}),
        label="التاريخ"
    )
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['revenue_description'].choices = [(n, n) for n in BudgetRevenue.objects.values_list('description', flat=True).distinct() if n]  

