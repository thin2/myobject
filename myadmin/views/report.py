from django.shortcuts import render
from django.db.models import Sum, Count, Q
from django.db.models.functions import TruncMonth
from datetime import date
from decimal import Decimal
from myadmin.models import Client, User, Fee, Salary
from myadmin.decorators import role_required


@role_required('admin', 'supervisor')
def index(request):
    today = date.today()
    current_month = today.strftime('%Y-%m')

    total_clients = Client.objects.filter(status=1).count()
    total_employees = User.objects.filter(status=1, role='accountant').count()
    overdue_count = Fee.objects.filter(status=2, client__status=1).count()

    month_income = Fee.objects.filter(
        status=1,
        paid_date__year=today.year,
        paid_date__month=today.month
    ).aggregate(total=Sum('paid_amount'))['total'] or Decimal('0')

    month_expense = Salary.objects.filter(
        month=current_month
    ).aggregate(total=Sum('total_salary'))['total'] or Decimal('0')

    month_profit = month_income - month_expense

    recent_months = []
    for i in range(6):
        m = today.month - i
        y = today.year
        if m <= 0:
            m += 12
            y -= 1
        month_str = f"{y}-{m:02d}"
        income = Fee.objects.filter(
            status=1, paid_date__year=y, paid_date__month=m
        ).aggregate(total=Sum('paid_amount'))['total'] or Decimal('0')
        expense = Salary.objects.filter(
            month=month_str
        ).aggregate(total=Sum('total_salary'))['total'] or Decimal('0')
        recent_months.append({
            'month': month_str,
            'income': income,
            'expense': expense,
            'profit': income - expense,
        })

    context = {
        'total_clients': total_clients,
        'total_employees': total_employees,
        'overdue_count': overdue_count,
        'month_income': month_income,
        'month_expense': month_expense,
        'month_profit': month_profit,
        'recent_months': recent_months,
    }
    return render(request, 'myadmin/report/index.html', context)
