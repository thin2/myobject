from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from decimal import Decimal
from myadmin.models import Salary, User, WorkLog
from myadmin.decorators import login_required_custom, role_required


EDUCATION_BONUS = {
    'college': 500,
    'bachelor': 1000,
    'master': 2000,
    'other': 0,
    '': 0,
}

CERTIFICATE_BONUS = {
    'none': 0,
    'accounting': 300,
    'intermediate': 800,
    'senior': 1500,
}

BASE_SALARY = 3000
WORK_YEAR_BONUS = 200
CLIENT_BONUS = 200
TAX_FILING_BONUS = 50
INVOICING_BONUS = 30


def calc_base_salary(user):
    base = BASE_SALARY
    base += EDUCATION_BONUS.get(user.education, 0)
    base += CERTIFICATE_BONUS.get(user.certificate, 0)
    base += user.work_years * WORK_YEAR_BONUS
    return Decimal(base)


def calc_performance_salary(user, month):
    client_count = user.clients.filter(status=1).count()
    tax_count = WorkLog.objects.filter(
        user=user, work_type='tax_filing',
        date__year=int(month[:4]), date__month=int(month[5:7])
    ).count()
    invoice_count = WorkLog.objects.filter(
        user=user, work_type='invoicing',
        date__year=int(month[:4]), date__month=int(month[5:7])
    ).count()
    perf = client_count * CLIENT_BONUS + tax_count * TAX_FILING_BONUS + invoice_count * INVOICING_BONUS
    return Decimal(perf)


@role_required('admin', 'supervisor')
def index(request, pIndex=1):
    slist = Salary.objects.select_related('user').all().order_by('-month', 'user__username')

    mywhere = []
    month = request.GET.get("month", '')
    if month:
        slist = slist.filter(month=month)
        mywhere.append("month=" + month)

    kw = request.GET.get("keyword", '')
    if kw:
        slist = slist.filter(user__first_name__contains=kw)
        mywhere.append("keyword=" + kw)

    pIndex = int(pIndex)
    page = Paginator(slist, 10)
    maxpage = page.num_pages
    if pIndex > maxpage:
        pIndex = maxpage
    if pIndex < 1:
        pIndex = 1
    list2 = page.page(pIndex)
    plist = page.page_range
    context = {"salarylist": list2, 'plist': plist, 'pIndex': pIndex, 'maxpage': maxpage, 'mywhere': mywhere}
    return render(request, "myadmin/salary/index.html", context)


@role_required('admin', 'supervisor')
def calculate(request):
    if request.method == 'POST':
        month = request.POST.get('month', '')
        if not month:
            return redirect('myadmin_salary_index', pIndex=1)

        accountants = User.objects.filter(role='accountant', status=1)
        for user in accountants:
            base = calc_base_salary(user)
            perf = calc_performance_salary(user, month)
            total = base + perf
            Salary.objects.update_or_create(
                user=user, month=month,
                defaults={
                    'base_salary': base,
                    'performance_salary': perf,
                    'total_salary': total,
                }
            )
        return redirect('myadmin_salary_index', pIndex=1)

    return render(request, 'myadmin/salary/calculate.html')


@login_required_custom
def mine(request):
    slist = Salary.objects.filter(user=request.user).order_by('-month')
    return render(request, 'myadmin/salary/mine.html', {'salarylist': slist})
