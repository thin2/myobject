from django.shortcuts import render
from django.db.models import Sum
from datetime import date
from decimal import Decimal
from myadmin.models import Client, User, Fee, Salary
from myadmin.decorators import login_required_custom


@login_required_custom
def index(request):
    today = date.today()
    current_month = today.strftime('%Y-%m')

    if request.user.role == 'accountant':
        my_clients = Client.objects.filter(accountant=request.user, status=1).count()
        my_overdue = Fee.objects.filter(
            client__accountant=request.user, client__status=1, status=2
        ).count()
        my_worklogs = request.user.worklogs.filter(
            date__year=today.year, date__month=today.month
        ).count()
        context = {
            'my_clients': my_clients,
            'my_overdue': my_overdue,
            'my_worklogs': my_worklogs,
        }
    else:
        total_clients = Client.objects.filter(status=1).count()
        total_employees = User.objects.filter(status=1, role='accountant').count()
        overdue_count = Fee.objects.filter(status=2, client__status=1).count()
        month_income = Fee.objects.filter(
            status=1, paid_date__year=today.year, paid_date__month=today.month
        ).aggregate(total=Sum('paid_amount'))['total'] or Decimal('0')
        month_expense = Salary.objects.filter(
            month=current_month
        ).aggregate(total=Sum('total_salary'))['total'] or Decimal('0')
        context = {
            'total_clients': total_clients,
            'total_employees': total_employees,
            'overdue_count': overdue_count,
            'month_income': month_income,
            'month_expense': month_expense,
            'month_profit': month_income - month_expense,
        }

    return render(request, 'myadmin/index/index.html', context)
