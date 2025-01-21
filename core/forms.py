from django import forms
from .models import  Loan, Covenant, Client, Budget, BudgetExpense, BudgetRevenue, Fund, FundExpense, FundRevenue
from django.contrib.auth.models import User, Permission
from django.contrib.auth.hashers import make_password
from django.apps import apps

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
        action_arabic = self.PERMISSION_TRANSLATIONS.get(action, action)

        # Get model's verbose_name_plural
        model_class = apps.get_model(app_label, model_name)
        model_arabic = getattr(model_class._meta, "verbose_name_plural", model_name)

        return f"{action_arabic} {model_arabic}"    

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
    class Meta:
        model = Loan
        fields = '__all__'
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'})
        }

class CovenantForm(forms.ModelForm):
    class Meta:
        model = Covenant
        fields = '__all__'
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'})
        }

class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = '__all__'
        widgets = {
            'join_date': forms.DateInput(attrs={'type': 'date'})
        }

class BudgetForm(forms.ModelForm):
    class Meta:
        model = Budget
        fields = '__all__'
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'})
        }

class BudgetRevenueForm(forms.ModelForm):
    class Meta:
        model = BudgetRevenue
        fields=['client', 'category', 'description', 'estimated_amount', 'actual_amount', 'paid_amount', 'date']
        can_delete=True
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'remaining_amount': forms.TextInput(attrs={'readonly': 'readonly'}),  
        }

class BudgetExpenseForm(forms.ModelForm):
    class Meta:
        model = BudgetExpense
        fields = ['category', 'description', 'estimated_amount', 'actual_amount', 'paid_amount', 'date']
        can_delete=True
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'remaining_amount': forms.TextInput(attrs={'readonly': 'readonly'}),  
        }

class FundForm(forms.ModelForm):
    class Meta:
        model = Fund
        fields = ['user', 'name', 'description', 'opening_balance', 'date']

        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'current_balance': forms.TextInput(attrs={'readonly': 'readonly'}), 
        }

class FundExpenseForm(forms.ModelForm):
    class Meta:
        model = FundExpense
        fields = ['category', 'description', 'amount', 'date']
        can_delete=True
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'})
        }

class FundRevenueForm(forms.ModelForm):
    class Meta:
        model = FundRevenue
        fields = ['category', 'description', 'amount', 'date']
        can_delete=True
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'})
        }
