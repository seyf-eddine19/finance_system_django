from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('dashboard/', views.dashboard, name='dashboard'),

    # Loan URLs
    path('loans/', views.LoanListView.as_view(), name='loan_list'),
    path('loans/create/', views.LoanCreateView.as_view(), name='loan_create'),
    path('loans/<int:pk>/', views.LoanDetailView.as_view(), name='loan_detail'),
    path('loans/<int:pk>/update/', views.LoanUpdateView.as_view(), name='loan_update'),
    path('loans/<int:pk>/delete/', views.LoanDeleteView.as_view(), name='loan_delete'),

    path('loans/export/excel', views.loan_export_excel, name='loan_export_excel'),
    path('loans/export/pdf/', views.loan_export_pdf, name='loan_export_pdf'),

    # Covenant URLs
    path('covenants/', views.CovenantListView.as_view(), name='covenant_list'),
    path('covenants/create/', views.CovenantCreateView.as_view(), name='covenant_create'),
    path('covenants/<int:pk>/', views.CovenantDetailView.as_view(), name='covenant_detail'),
    path('covenants/<int:pk>/update/', views.CovenantUpdateView.as_view(), name='covenant_update'),
    path('covenants/<int:pk>/delete/', views.CovenantDeleteView.as_view(), name='covenant_delete'),

    # Client URLs
    path('clients/', views.ClientListView.as_view(), name='client_list'),
    path('clients/create/', views.ClientCreateView.as_view(), name='client_create'),
    path('clients/<int:pk>/', views.ClientDetailView.as_view(), name='client_detail'),
    path('clients/<int:pk>/update/', views.ClientUpdateView.as_view(), name='client_update'),
    path('clients/<int:pk>/delete/', views.ClientDeleteView.as_view(), name='client_delete'),

    # Budget URLs
    path('budgets/', views.BudgetView.as_view(), name='budget_list'),
    path('budgets/<int:pk>/', views.BudgetView.as_view(), name='budget_update'),
    path('budgets/<int:pk>/detail', views.BudgetDetailView.as_view(), name='budget_detail'),
    path('budgets/<int:budget_pk>/update-budget-revenues/', views.BudgetRevenuesChangeView.as_view(), name='budget_revenues_change'),
    path('budgets/<int:budget_pk>/update-budget-expenses/', views.BudgetExpensesChangeView.as_view(), name='budget_expenses_change'),

    # Fund URLs
    path('funds/', views.FundView.as_view(), name='fund_list'),
    path('funds/<int:pk>/', views.FundView.as_view(), name='fund_update'),
    path('funds/<int:pk>/detail/', views.FundDetailView.as_view(), name='fund_detail'),
    path('funds/<int:fund_pk>/update-fund-revenues/', views.FundRevenuesChangeView.as_view(), name='fund_revenues_change'),
    path('funds/<int:fund_pk>/update-fund-expenses/', views.FundExpensesChangeView.as_view(), name='fund_expenses_change'),
    path('funds/<int:pk>/delete/', views.FundDeleteView.as_view(), name='fund_delete'),

    # User URLs
    path('users/', views.user_list, name='user_list'),
    path('users/create/', views.user_create, name='user_create'),
    path('users/<int:user_id>/update/', views.user_update, name='user_update'),
    path('users/<int:user_id>/delete/', views.user_delete, name='user_delete'),
    path('profile/', views.profile_view, name='profile'),
    path('logout/', views.logout_view, name='logout'),
]

handler403 = 'core.views.custom_403'
handler404 = 'core.views.custom_404'
handler500 = 'core.views.custom_500'
