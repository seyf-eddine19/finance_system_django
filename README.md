#  Finance Management System

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
