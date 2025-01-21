#  Finance Management System
### وصف المشروع

نظام شامل لإدارة السلف، العهد، الصناديق والموازنات المالية.
---

### فكرة المشروع
يهدف هذا المشروع إلى تقديم نظام إدارة شامل لإدارة السلف والعهد والموازنات المالية في المؤسسات. يتميز النظام بواجهة مستخدم بسيطة وسهلة الاستخدام، مع إمكانية تتبع العمليات المالية المختلفة لكل مستخدم، وإعداد تقارير دورية ودقيقة.

---

### المزايا الرئيسية للنظام

#### 1. **إدارة السلف:**
- تسجيل السلف الجديدة لكل مستخدم مع تحديد نوع السلفة وقيمتها.
- تحديث الحالة المالية للسلفة بشكل ديناميكي.
- تتبع المبالغ المدفوعة والمبالغ المتبقية.

#### 2. **إدارة العهد:**
- تسجيل العهد الجديدة مع تحديد النوع والمبالغ.
- تحديث الحالة المالية للعهد بشكل ديناميكي.
- تتبع المبالغ المدفوعة والمبالغ المتبقية.

#### 3. **إدارة الصناديق:**
- إنشاء صناديق مالية مع تحديد الرصيد الافتتاحي.
- تسجيل الإيرادات والمصروفات لكل صندوق.
- تحديث الرصيد الحالي للصندوق تلقائيًا عند إضافة أو تعديل الإيرادات والمصروفات.
- عرض تفصيلي لجميع العمليات المالية المتعلقة بكل صندوق.

#### 4. **إدارة الموازنات:**
- إنشاء موازنات مالية مع وصف تفصيلي.
- تسجيل المصروفات والإيرادات لكل موازنة.
- إدارة المصروفات والإيرادات التقديرية والفعلية مع تتبع المدفوع والمتبقي.

#### 5. **إدارة العملاء:**
- تسجيل العملاء مع تفاصيل مثل الاسم، البريد الإلكتروني، ورقم الهاتف.
- تصنيف العملاء حسب النوع والفئة.
- تتبع الرصيد المالي لكل عميل.

---

### التقنيات المستخدمة
- **Django Framework:** لبناء الواجهة الخلفية للنظام.
- **SQLite:** كقاعدة بيانات لتخزين المعلومات.
- **HTML/CSS:** لواجهة المستخدم الأساسية.
- **Excel Export:** لتصدير البيانات بسهولة.

---

### هيكلية التطبيق

#### **النماذج (Models):**
- **Loan, Covenant, Fund, FundRevenue, FundExpense, Budget, BudgetRevenue, BudgetExpense, Client**
- تحتوي هذه النماذج على منطق لحساب القيم المتبقية والمدفوعة تلقائيًا.

#### **الواجهات (Views):**
- **Class-Based Views:** لإنشاء واجهات CRUD لجميع العمليات.
- دعم **تصدير البيانات** عبر طرق خاصة.

#### **الروابط (URLs):**
- تم تنظيم الروابط لدعم عمليات العرض، الإضافة، التعديل، والحذف لكل من السلف، العهد، الصناديق، والموازنات. 
## Project Description

Manage Loan, Covenant, Fond and Budget Management System

---

### Project Idea
This project aims to provide a comprehensive system for managing loans, covenants, and financial budgets in organizations. It features a user-friendly interface with the ability to track various financial operations for each user and generate periodic and accurate reports.

---

### Key Features of the System

#### 1. **Loan Management:**
- Record new loans for each user with the loan type and amount.
- Dynamically update the financial status of covenants.
- Track paid and remaining balances.

#### 2. **Covenant Management:**
- Register new covenants with type and amounts.
- Dynamically update the financial status of covenants.
- Track paid and remaining balances.

#### 3. **Fund Management:**
- Create financial funds with an opening balance.
- Record revenues and expenses for each fund.
- Automatically update the current fund balance when adding or editing revenues and expenses.
- Detailed view of all financial operations for each fund.

#### 4. **Budget Management:**
- Create financial budgets with detailed descriptions.
- Record expenses and revenues for each budget.
- Manage estimated and actual expenses and revenues with tracking of paid and remaining balances.

#### 5. **Client Management:**
- Register clients with details such as name, email, and phone number.
- Classify clients by type and category.
- Track the financial balance for each client.

---

### Technologies Used
- **Django Framework:** For building the backend of the system.
- **SQLite:** As the database to store information.
- **HTML/CSS:** For the basic user interface.
- **Excel Export:** For easy data export.

---

### Application Structure

#### **Models:**
- **Loan, Covenant, Fund, FundRevenue, FundExpense, Budget, BudgetRevenue, BudgetExpense, Client**
- These models include logic for automatically calculating remaining and paid amounts.

#### **Views:**
- **Class-Based Views:** For creating CRUD interfaces for all operations.
- Support for **data export** through special methods.

#### **URLs:**
- Organized URLs for viewing, adding, editing, and deleting items for loans, covenants, funds, and budgets.

---
