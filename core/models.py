from django.db import models
from django.contrib.auth.models import User


class Loan(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="صاحب السلف")
    loan_type = models.CharField(max_length=100, verbose_name="شكل السلف")
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="قيمة السلف")
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="المبلغ المدفوع")
    remaining_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True, verbose_name="المتبقي")
    date = models.DateField(verbose_name="التاريخ")

    def save(self, *args, **kwargs):
        # Calculate the remaining amount before saving
        if self.amount and self.paid_amount is not None:
            self.remaining_amount = self.amount - self.paid_amount
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "سلفة"
        verbose_name_plural = "السلف"

    def __str__(self):
        return self.loan_type
    
    
class Covenant(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="صاحب العهد")
    covenant_type = models.CharField(max_length=100, verbose_name="شكل العهد")
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="قيمة العهد")
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="المبلغ المدفوع")
    remaining_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="المتبقي")
    date = models.DateField(verbose_name="التاريخ")

    def save(self, *args, **kwargs):
        # Calculate the remaining amount before saving
        if self.amount and self.paid_amount is not None:
            self.remaining_amount = self.amount - self.paid_amount
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "عهدة"
        verbose_name_plural = "العهود"

    def __str__(self):
        return self.covenant_type
    

class Fund(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="صاحب الصندوق")
    name = models.CharField(max_length=100, verbose_name="اسم الصندوق")
    description = models.TextField(verbose_name="وصف الصندوق")
    opening_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="الرصيد الافتتاحي")
    current_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="الرصيد الحالي")
    date = models.DateField(verbose_name="تاريخ الصندوق")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")

    class Meta:
        verbose_name = "صندوق"
        verbose_name_plural = "الصناديق"

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
    category = models.CharField(max_length=100, verbose_name="فئة الإيراد")
    description = models.TextField(verbose_name="وصف الإيراد")
    date = models.DateField(verbose_name="تاريخ الإيراد")

    class Meta:
        verbose_name = "إيراد صندوق"
        verbose_name_plural = "إيرادات الصندوق"

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
    category = models.CharField(max_length=100, verbose_name="فئة المصروف")
    description = models.TextField(verbose_name="وصف المصروف")
    date = models.DateField(verbose_name="تاريخ المصروف")

    class Meta:
        verbose_name = "مصروف صندوق"
        verbose_name_plural = "مصروفات الصندوق"
    
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


class BudgetExpense(models.Model):
    budget = models.ForeignKey(Budget, on_delete=models.CASCADE, verbose_name="الموازنة")
    category = models.CharField(max_length=100, verbose_name="فئة المصروف")
    description = models.TextField(verbose_name="وصف المصروف")
    estimated_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="المبلغ التقديري")
    actual_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, default=0, verbose_name="المبلغ الفعلي")
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, default=0, verbose_name="المبلغ المدفوع")
    remaining_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, default=0, verbose_name="المتبقي")
    date = models.DateField(verbose_name="تاريخ المصروف")

    class Meta:
        verbose_name = "مصروف موازنة"
        verbose_name_plural = "مصروفات الموازنة"

    def save(self, *args, **kwargs):
        # Calculate the remaining amount before saving
        if self.actual_amount and self.paid_amount is not None:
            self.remaining_amount = self.actual_amount - self.paid_amount
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.budget.name} - {self.category} - {self.date.strftime('%Y-%m-%d')}"


class BudgetRevenue(models.Model):
    budget = models.ForeignKey(Budget, on_delete=models.CASCADE, verbose_name="الموازنة")
    client = models.ForeignKey('Client', on_delete=models.CASCADE, verbose_name="العميل")  # FK to Client model
    category = models.CharField(max_length=100, verbose_name="فئة الإيراد")
    description = models.TextField(verbose_name="وصف إضافي للإيراد")
    estimated_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="المبلغ التقديري")
    actual_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, default=0, verbose_name="المبلغ الفعلي")
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, default=0, verbose_name="المبلغ المدفوع")
    remaining_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, default=0, verbose_name="المتبقي")
    date = models.DateField(verbose_name="تاريخ عملية الإيراد")

    class Meta:
        verbose_name = "إيراد موازنة"
        verbose_name_plural = "إيرادات الموازنة"

    def save(self, *args, **kwargs):
        # Calculate the remaining amount before saving
        if self.actual_amount and self.paid_amount is not None:
            self.remaining_amount = self.actual_amount - self.paid_amount
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.budget.name} - {self.category} - {self.date.strftime('%Y-%m-%d')}"


class Client(models.Model):
    name = models.CharField(max_length=100, verbose_name="اسم العميل", unique=True)
    email = models.EmailField(verbose_name="البريد الإلكتروني", unique=True)
    phone = models.CharField(max_length=15, verbose_name="رقم الهاتف", unique=True)
    type = models.CharField(max_length=50, verbose_name="النوع")
    category = models.CharField(max_length=50, verbose_name="الفئة")
    join_date = models.DateField(verbose_name="تاريخ الانضمام")
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="الرصيد")

    class Meta:
        verbose_name = "عميل"
        verbose_name_plural = "العملاء"

    def __str__(self):
        return self.name
    

