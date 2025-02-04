from django.db.models import Sum
from .models import Loan, Covenant, Client, Budget, BudgetExpense, BudgetRevenue, Fund, FundExpense, FundRevenue


def get_loan_chart_data():
    loans_by_type = Loan.objects.values('loan_type').annotate(
        total_amount=Sum('amount'),
        total_paid=Sum('paid_amount'),
        total_remaining=Sum('remaining_amount')
    )
    loans_by_owner = Loan.objects.values('loan_owner').annotate(
        total_amount=Sum('amount'),
        total_paid=Sum('paid_amount'),
        total_remaining=Sum('remaining_amount')
    )

    chart_data_by_type = {
        "labels": [loan['loan_type'] for loan in loans_by_type],
        "datasets": [
            {
                "label": "قيمة السلف",
                "data": [float(loan['total_amount']) for loan in loans_by_owner],
                "backgroundColor": "rgba(85, 93, 211, 0.8)"
            },
            {
                "label": "المبلغ المدفوع",
                "data": [float(loan['total_paid']) for loan in loans_by_owner],
                "backgroundColor": "rgba(85, 211, 102, 0.8)"
            },
            {
                "label": "المبلغ المتبقي",
                "data": [float(loan['total_remaining']) for loan in loans_by_owner],
                "backgroundColor": "rgba(211, 85, 85, 0.8)"
            },
        ]
    }

    chart_data_by_owner = {
        "labels": [loan['loan_owner'] for loan in loans_by_owner],
        "datasets": [
            {
                "label": "قيمة السلف",
                "data": [float(loan['total_amount']) for loan in loans_by_owner],
                "backgroundColor": "rgba(27, 74, 230, 0.8)"
            },
            {
                "label": "المبلغ المدفوع",
                "data": [float(loan['total_paid']) for loan in loans_by_owner],
                "backgroundColor": "rgba(27, 230, 54, 0.8)"
            },
            {
                "label": "المبلغ المتبقي",
                "data": [float(loan['total_remaining']) for loan in loans_by_owner],
                "backgroundColor": "rgba(230, 27, 27, 0.8)"
            },
        ]
    }

    return {"by_type": chart_data_by_type, "by_owner": chart_data_by_owner}

def get_covenant_chart_data():
    covenants_by_type = Covenant.objects.values('covenant_type').annotate(
        total_amount=Sum('amount'),
        total_paid=Sum('paid_amount'),
        total_remaining=Sum('remaining_amount')
    )
    covenants_by_owner = Covenant.objects.values('covenant_owner').annotate(
        total_amount=Sum('amount'),
        total_paid=Sum('paid_amount'),
        total_remaining=Sum('remaining_amount')
    )

    chart_data_by_type = {
        "labels": [covenant['covenant_type'] for covenant in covenants_by_type],
        "datasets": [
            {
                "label": "قيمة العهد",
                "data": [float(covenant['total_amount']) for covenant in covenants_by_owner],
                "backgroundColor": "rgba(85, 93, 211, 0.8)"
            },
            {
                "label": "المبلغ المدفوع",
                "data": [float(covenant['total_paid']) for covenant in covenants_by_owner],
                "backgroundColor": "rgba(85, 211, 102, 0.8)"
            },
            {
                "label": "المبلغ المتبقي",
                "data": [float(covenant['total_remaining']) for covenant in covenants_by_owner],
                "backgroundColor": "rgba(211, 85, 85, 0.8)"
            },
        ]
    }

    chart_data_by_owner = {
        "labels": [covenant['covenant_owner'] for covenant in covenants_by_owner],
        "datasets": [
            {
                "label": "قيمة العهد",
                "data": [float(covenant['total_amount']) for covenant in covenants_by_owner],
                "backgroundColor": "rgba(27, 74, 230, 0.8)"
            },
            {
                "label": "المبلغ المدفوع",
                "data": [float(covenant['total_paid']) for covenant in covenants_by_owner],
                "backgroundColor": "rgba(27, 230, 54, 0.8)"
            },
            {
                "label": "المبلغ المتبقي",
                "data": [float(covenant['total_remaining']) for covenant in covenants_by_owner],
                "backgroundColor": "rgba(230, 27, 27, 0.8)"
            },
        ]
    }

    return {"by_type": chart_data_by_type, "by_owner": chart_data_by_owner}


def get_budget_revenue_chart_data():
    # Query for revenue by budget
    budget_revenues_by_budget = BudgetRevenue.objects.values('budget__date').annotate(
        total_estimated=Sum('estimated_amount'),
        total_actual=Sum('actual_amount'),
        total_paid=Sum('paid_amount'),
        total_remaining=Sum('remaining_amount')
    )

    budget_expenses_by_budget = BudgetExpense.objects.values('budget__date').annotate(
        total_estimated=Sum('estimated_amount'),
        total_actual=Sum('actual_amount'),
        total_paid=Sum('paid_amount'),
        total_remaining=Sum('remaining_amount')
    )
    # budget_revenues_by_budget = BudgetRevenue.objects.values('uatedget__id', 'estimated_amount', 'actual_amount', 'paid_amount', 'remaining_amount')

    # Query for revenue by category
    budget_revenues_by_category = BudgetRevenue.objects.values('category').annotate(
        total_estimated=Sum('estimated_amount'),
        total_actual=Sum('actual_amount'),
        total_paid=Sum('paid_amount'),
        total_remaining=Sum('remaining_amount')
    )

    # Prepare chart data
    chart_data = {
        "by_budget_1": {  # Line Chart Data for Budget
            "labels": [str(revenue['budget__date']) for revenue in budget_revenues_by_budget],
            "datasets": [
                {
                    "label": "الإيراد التقديري",
                    "data": [float(revenue['total_estimated']) for revenue in budget_revenues_by_budget],
                    "borderColor": "#2ECC71",  # Line Chart
                    # "fill": "none"
                },
                {
                    "label": "الإيراد الفعلي",
                    "data": [float(revenue['total_actual']) for revenue in budget_revenues_by_budget],
                    "borderColor": "#090",  # Line Chart
                    # "fill": 'none'
                },
                {
                    "label": "المصروف التقديري",
                    "data": [float(expense['total_estimated']) for expense in budget_expenses_by_budget],
                    "borderColor": "#FF5C5C",  # Line Chart
                    # "fill": "none"
                },
                {
                    "label": "المصروف الفعلي",
                    "data": [float(expense['total_actual']) for expense in budget_expenses_by_budget],
                    "borderColor": "red",  # Line Chart
                    # "fill": 'none'
                }
            ]
        },
        "by_budget_2": {  # Bar Chart Data for Budget
            "labels": [str(revenue['budget__date']) for revenue in budget_revenues_by_budget],
            "datasets": [
                {
                    "label": "المبلغ الفعلي",
                    "data": [float(revenue['total_actual']) for revenue in budget_revenues_by_budget],
                    "borderColor": "rgba(27, 74, 230, 1)",
                    "backgroundColor": "rgba(27, 74, 230, 1)",
                    "type": "line",
                },
                {
                    "label": "المبلغ المدفوع",
                    "data": [float(revenue['total_paid']) for revenue in budget_revenues_by_budget],
                    "backgroundColor": "rgba(27, 230, 54, 1)",
                },
                {
                    "label": "المبلغ المتبقي",
                    "data": [float(revenue['total_remaining']) for revenue in budget_revenues_by_budget],
                    "backgroundColor": "rgba(230, 27, 27, 1)"
                },
            ]
        },
        "by_category": {  # Bar Chart Data for Category
            "labels": [str(revenue['category']) for revenue in budget_revenues_by_category],
            "datasets": [
                # {
                #     "label": "المبلغ الفعلي",
                #     "data": [float(revenue['total_actual']) for revenue in budget_revenues_by_category],
                #     "borderColor": "rgba(27, 74, 230, 1)",
                #     "backgroundColor": "rgba(27, 74, 230, 1)",
                #     "type": "line",
                # },
                {
                    "label": "المبلغ المدفوع",
                    "data": [float(revenue['total_paid']) for revenue in budget_revenues_by_category],
                    "backgroundColor": "rgba(27, 230, 54, 1)",
                },
                {
                    "label": "المبلغ المتبقي",
                    "data": [float(revenue['total_remaining']) for revenue in budget_revenues_by_category],
                    "backgroundColor": "rgba(230, 27, 27, 1)"
                },
            ]
        },
    }

    return chart_data
