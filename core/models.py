import os
from django.db import models
from django.contrib.auth.models import User


class Loan(models.Model):
    loan_owner = models.CharField(max_length=100, default='owner', verbose_name="صاحب السلف")
    loan_type = models.CharField(max_length=100, verbose_name="شكل السلف")
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="قيمة السلف")
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="المبلغ المدفوع")
    remaining_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True, verbose_name="المتبقي")
    note = models.TextField(verbose_name="ملاحظات", blank=True, null=True)
    date = models.DateField(verbose_name="تاريخ السلفة", auto_now_add=True)

    class Meta:
        verbose_name = "سلفة"
        verbose_name_plural = "السلف"

    @staticmethod
    def get_loan_types():
        """ إرجاع القيم الفريدة لحقول `loan_type` """
        return Loan.objects.values_list("loan_type", flat=True).distinct()

    def formatted_amount(self):
        return "{:,.2f}".format(self.amount)

    def formatted_paid_amount(self):
        return "{:,.2f}".format(self.paid_amount)

    def formatted_remaining_amount(self):
        return "{:,.2f}".format(self.remaining_amount)
    
    def save(self, *args, **kwargs):
        # حساب المبلغ المتبقي
        if self.amount and self.paid_amount is not None:
            self.remaining_amount = self.amount - self.paid_amount
        
        if self.pk:  # Updating an existing record
            old_paid = Loan.objects.get(pk=self.pk).paid_amount
            current_paid = self.paid_amount - old_paid
        else:  # Creating a new record
            current_paid = self.paid_amount

        super().save(*args, **kwargs)
        # تسجيل الحركة في سجل الحركات
        if current_paid:
            LoanHistory.objects.create(
                loan=self,
                amount=self.amount,
                paid_amount=current_paid,
                remaining_amount=self.remaining_amount,
                note=self.note
            )

    def __str__(self):
        return f"{self.loan_owner} - {self.loan_type}"


class LoanHistory(models.Model):
    loan = models.ForeignKey(Loan, on_delete=models.CASCADE, related_name="history", verbose_name="السلفة")
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="القيمة")
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="المبلغ المدفوع")
    remaining_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="المتبقي")
    note = models.TextField(verbose_name="ملاحظات", blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ التعديل")

    class Meta:
        verbose_name = "سجل السلفة"
        verbose_name_plural = "سجلات السلف"
        default_permissions = []

    def formatted_amount(self):
        return "{:,.2f}".format(self.amount)

    def formatted_paid_amount(self):
        return "{:,.2f}".format(self.paid_amount)

    def formatted_remaining_amount(self):
        return "{:,.2f}".format(self.remaining_amount)
    
    def __str__(self):
        return f"تعديل على {self.loan.loan_owner} - {self.loan.loan_type} بتاريخ {self.date}"


class Covenant(models.Model):
    covenant_owner = models.CharField(max_length=100, default='owner', verbose_name="صاحب العهدة")
    covenant_type = models.CharField(max_length=100, verbose_name="شكل العهدة")
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="قيمة العهدة")
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="المبلغ المدفوع")
    remaining_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="المتبقي")
    note = models.TextField(verbose_name="ملاحظات", blank=True, null=True)
    date = models.DateField(verbose_name="تاريخ العهدة", auto_now_add=True)

    class Meta:
        verbose_name = "عهدة"
        verbose_name_plural = "العهود"

    def formatted_amount(self):
        return "{:,.2f}".format(self.amount)

    def formatted_paid_amount(self):
        return "{:,.2f}".format(self.paid_amount)

    def formatted_remaining_amount(self):
        return "{:,.2f}".format(self.remaining_amount)

    def save(self, *args, **kwargs):
        # حساب المبلغ المتبقي
        if self.amount and self.paid_amount is not None:
            self.remaining_amount = self.amount - self.paid_amount

        if self.pk:  # Updating an existing record
            old_paid = Covenant.objects.get(pk=self.pk).paid_amount
            current_paid = self.paid_amount - old_paid
        else:  # Creating a new record
            current_paid = self.paid_amount

        super().save(*args, **kwargs)

        # تسجيل الحركة في سجل الحركات
        if current_paid:
            CovenantHistory.objects.create(
                covenant=self,
                amount=self.amount,
                paid_amount=current_paid,
                remaining_amount=self.remaining_amount,
                note=self.note
            )

    def __str__(self):
        return f"{self.covenant_owner} - {self.covenant_type}"


class CovenantHistory(models.Model):
    covenant = models.ForeignKey(Covenant, on_delete=models.CASCADE, related_name="history", verbose_name="العهدة")
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="القيمة")
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="المبلغ المدفوع")
    remaining_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="المتبقي")
    note = models.TextField(verbose_name="ملاحظات", blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ التعديل")

    class Meta:
        verbose_name = "سجل العهدة"
        verbose_name_plural = "سجلات العهد"
        default_permissions = []

    def formatted_amount(self):
        return "{:,.2f}".format(self.amount)

    def formatted_paid_amount(self):
        return "{:,.2f}".format(self.paid_amount)

    def formatted_remaining_amount(self):
        return "{:,.2f}".format(self.remaining_amount)
    
    def __str__(self):
        return f"تعديل على {self.covenant.covenant_owner} - {self.covenant.covenant_type} بتاريخ {self.date}"


class Fund(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="صاحب الصندوق")
    name = models.CharField(max_length=100, verbose_name="اسم الصندوق")
    description = models.TextField(verbose_name="وصف الصندوق")
    opening_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="الرصيد الافتتاحي")
    current_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="الرصيد الحالي")
    date = models.DateField(verbose_name="تاريخ الصندوق")
    is_private = models.BooleanField(default=False, verbose_name="صندوق خاص")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")

    class Meta:
        verbose_name = "صندوق"
        verbose_name_plural = "الصناديق"
        permissions = [
            ("viewall_funds", "عرض كل الصناديق"),
            ("viewprivate_funds", "عرض الصناديق الخاصة"),
        ]

    def formatted_opening_balance(self):
        return "{:,.2f}".format(self.opening_balance)

    def formatted_current_balance(self):
        return "{:,.2f}".format(self.current_balance)
    
    def save(self, *args, **kwargs):
        if not self.pk: 
            self.current_balance = self.opening_balance
        else: 
            old_opening_balance = Fund.objects.get(pk=self.pk).opening_balance
            self.current_balance += self.opening_balance - old_opening_balance
        super(Fund, self).save(*args, **kwargs)

    def __str__(self):
        return self.name


class FundRevenue(models.Model):
    fund = models.ForeignKey(Fund, on_delete=models.CASCADE, verbose_name="الصندوق")
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="المبلغ")
    description = models.CharField(max_length=100, verbose_name="بيان الإيراد")
    category = models.CharField(max_length=100, verbose_name="فئة الإيراد")
    date = models.DateField(verbose_name="تاريخ الإيراد")

    class Meta:
        verbose_name = "إيراد صندوق"
        verbose_name_plural = "إيرادات الصندوق"
        default_permissions = []

    def formatted_amount(self):
        return "{:,.2f}".format(self.amount)

    def save(self, *args, **kwargs):
        if self.pk:  # Updating an existing record
            old_amount = FundRevenue.objects.get(pk=self.pk).amount
            self.fund.current_balance += self.amount - old_amount
        else:  # Creating a new record
            self.fund.current_balance += self.amount
        self.fund.save()
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        self.fund.current_balance -= self.amount
        self.fund.save()
        super().delete(*args, **kwargs)

    def __str__(self):
        return self.category
    

class FundExpense(models.Model):
    fund = models.ForeignKey(Fund, on_delete=models.CASCADE, verbose_name="الصندوق")
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="المبلغ")
    description = models.CharField(max_length=100, verbose_name="بيان المصروف")
    category = models.CharField(max_length=100, verbose_name="فئة المصروف")
    date = models.DateField(verbose_name="تاريخ المصروف")

    class Meta:
        verbose_name = "مصروف صندوق"
        verbose_name_plural = "مصروفات الصندوق"
        default_permissions = []

    def formatted_amount(self):
        return "{:,.2f}".format(self.amount)
    
    def save(self, *args, **kwargs):
        if self.pk:  # Updating an existing record
            old_amount = FundExpense.objects.get(pk=self.pk).amount
            self.fund.current_balance -= self.amount - old_amount
        else:  # Creating a new record
            self.fund.current_balance -= self.amount
        self.fund.save()
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        self.fund.current_balance += self.amount
        self.fund.save()
        super().delete(*args, **kwargs)
        
    def __str__(self):
        return self.category
    

class Budget(models.Model):
    name = models.CharField(max_length=100, verbose_name="اسم الموازنة", unique=True)
    description = models.TextField(verbose_name="وصف الموازنة")
    status = models.CharField(
        max_length=50,
        choices=[('فعلية', 'فعلية'), ('تقديرية', 'تقديرية')],
        verbose_name="حالة الموازنة"
    )
    date = models.DateField(verbose_name="تاريخ الموازنة", unique=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")

    class Meta:
        verbose_name = "موازنة"
        verbose_name_plural = "الموازنات"

    def __str__(self):
        return self.name


class BudgetRevenue(models.Model):
    budget = models.ForeignKey(Budget, on_delete=models.CASCADE, verbose_name="الموازنة")
    client = models.ForeignKey('Client', on_delete=models.CASCADE, related_name='budget_revenues', verbose_name="العميل")  # FK to Client model
    description = models.CharField(max_length=100, verbose_name="بيان الإيراد")
    category = models.CharField(max_length=100, verbose_name="فئة الإيراد")
    estimated_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="المبلغ التقديري")
    actual_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, default=0, verbose_name="المبلغ الفعلي")
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, default=0, verbose_name="المبلغ المدفوع")
    remaining_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, default=0, verbose_name="المتبقي")
    date = models.DateField(verbose_name="تاريخ عملية الإيراد")

    class Meta:
        verbose_name = "إيراد موازنة"
        verbose_name_plural = "إيرادات الموازنة"
        default_permissions = []

    def formatted_estimated_amount(self):
        return "{:,.2f}".format(self.estimated_amount)

    def formatted_actual_amount(self):
        return "{:,.2f}".format(self.actual_amount)

    def formatted_paid_amount(self):
        return "{:,.2f}".format(self.paid_amount)

    def formatted_remaining_amount(self):
        return "{:,.2f}".format(self.remaining_amount)
    
    def save(self, *args, **kwargs):
        # Calculate the remaining amount before saving
        if self.actual_amount and self.paid_amount is not None:
            self.remaining_amount = self.actual_amount - self.paid_amount

        if self.pk:  # Updating an existing record
            old_remaining_amount = BudgetRevenue.objects.get(pk=self.pk).remaining_amount
            self.client.balance += self.remaining_amount - old_remaining_amount
        else:  # Creating a new record
            self.client.balance += self.remaining_amount

        self.client.save()
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        # Adjust the client balance when deleting the record
        self.client.balance -= self.remaining_amount  # Deduct the remaining amount of the deleted revenue
        self.client.save()
        super().delete(*args, **kwargs)

    def __str__(self):
        return f"{self.budget.name} - {self.category} - {self.date.strftime('%Y-%m-%d')}"


class BudgetExpense(models.Model):
    EXPENSE_STATUS = [
        ('urgent', 'عاجل'),
        ('important', 'مهم'),
        ('normal', 'عادي'),
    ]

    budget = models.ForeignKey(Budget, on_delete=models.CASCADE, verbose_name="الموازنة")
    description = models.CharField(max_length=100, verbose_name="بيان المصروف")
    category = models.CharField(max_length=100, verbose_name="فئة المصروف")
    estimated_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="المبلغ التقديري")
    actual_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, default=0, verbose_name="المبلغ الفعلي")
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, default=0, verbose_name="المبلغ المدفوع")
    remaining_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, default=0, verbose_name="المتبقي")
    date = models.DateField(verbose_name="تاريخ المصروف")
    expense_status = models.CharField(max_length=10, choices=EXPENSE_STATUS, default='normal', verbose_name="حالة المصروف")

    class Meta:
        verbose_name = "مصروف موازنة"
        verbose_name_plural = "مصروفات الموازنة"
        default_permissions = []

    def formatted_estimated_amount(self):
        return "{:,.2f}".format(self.estimated_amount)

    def formatted_actual_amount(self):
        return "{:,.2f}".format(self.actual_amount)

    def formatted_paid_amount(self):
        return "{:,.2f}".format(self.paid_amount)

    def formatted_remaining_amount(self):
        return "{:,.2f}".format(self.remaining_amount)
    
    def save(self, *args, **kwargs):
        # Calculate the remaining amount before saving
        if self.actual_amount and self.paid_amount is not None:
            self.remaining_amount = self.actual_amount - self.paid_amount
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.budget.name} - {self.category} - {self.date.strftime('%Y-%m-%d')}"


class Client(models.Model):
    name = models.CharField(max_length=100, verbose_name="اسم العميل", unique=True)
    image = models.ImageField(upload_to='clients/images/', blank=True, null=True, verbose_name="صورة العميل")
    type = models.CharField(max_length=50, verbose_name="نوع العميل")
    category = models.CharField(max_length=50, verbose_name="فئة العميل")
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="الرصيد")
    join_date = models.DateField(verbose_name="تاريخ الانضمام")

    class Meta:
        verbose_name = "عميل"
        verbose_name_plural = "العملاء"

    def formatted_balance(self):
        return "{:,.2f}".format(self.balance)

    def __str__(self):
        return self.name


class ClientDocument(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='documents', verbose_name="العميل")
    name = models.CharField(max_length=255, verbose_name="عنوان المستند")
    file = models.FileField(upload_to='documents/', verbose_name="الملف")
    date_upload = models.DateField(auto_now_add=True, verbose_name="تاريخ الرفع")

    class Meta:
        verbose_name = "مستند"
        verbose_name_plural = "المستندات"
        default_permissions = []

    def file_type(self):
        name, extension = os.path.splitext(self.file.name)  # إصلاح اسم الحقل
        return extension.lower()

    @property
    def is_image(self):
        return self.file_type() in ['.jpg', '.jpeg', '.png', '.gif']

    @property
    def is_pdf(self):
        return self.file_type() == '.pdf'

    @property
    def is_excel(self):
        return self.file_type() in ['.xls', '.xlsx']

    @property
    def is_word(self):
        return self.file_type() in ['.doc', '.docx']

    def __str__(self):
        return f"{self.name} - {self.client.name}"  # تصحيح الإشارة إلى الاسم


class ClientPhone(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='phones', verbose_name="العميل")
    phone = models.CharField(max_length=20, verbose_name="رقم الهاتف", unique=True)

    class Meta:
        verbose_name = "رقم الهاتف"
        verbose_name_plural = "أرقام الهواتف"
        default_permissions = []

    def __str__(self):
        return self.phone


class ClientEmail(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='emails', verbose_name="العميل")
    email = models.CharField(max_length=20, verbose_name="عنوان البريد الإلكتروني", unique=True)

    class Meta:
        verbose_name = "عنوان البريد الإلكتروني"
        verbose_name_plural = "عناوين البريد الإلكتروني"
        default_permissions = []

    def __str__(self):
        return self.email

