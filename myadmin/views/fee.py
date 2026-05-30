from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from django.db.models import Q
from datetime import date
from myadmin.models import Fee, Client
from myadmin.decorators import login_required_custom, role_required


@login_required_custom
def index(request, pIndex=1):
    if request.user.role == 'accountant':
        flist = Fee.objects.filter(client__accountant=request.user, client__status__lt=9)
    else:
        flist = Fee.objects.filter(client__status__lt=9)

    mywhere = []
    status = request.GET.get("status", '')
    if status != '':
        flist = flist.filter(status=int(status))
        mywhere.append("status=" + status)

    kw = request.GET.get("keyword", '')
    if kw:
        flist = flist.filter(Q(client__name__contains=kw) | Q(client__client_no__contains=kw))
        mywhere.append("keyword=" + kw)

    pIndex = int(pIndex)
    page = Paginator(flist, 10)
    maxpage = page.num_pages
    if pIndex > maxpage:
        pIndex = maxpage
    if pIndex < 1:
        pIndex = 1
    list2 = page.page(pIndex)
    plist = page.page_range
    context = {"feelist": list2, 'plist': plist, 'pIndex': pIndex, 'maxpage': maxpage, 'mywhere': mywhere}
    return render(request, "myadmin/fee/index.html", context)


@role_required('admin', 'supervisor')
def add(request, cid=0):
    client = Client.objects.get(id=cid)
    if request.method == 'POST':
        Fee.objects.create(
            client=client,
            due_date=request.POST.get('due_date'),
            due_amount=request.POST.get('due_amount', client.fee_amount),
            status=0,
        )
        return redirect('myadmin_client_detail', cid=cid)

    return render(request, 'myadmin/fee/add.html', {'client': client})


@role_required('admin', 'supervisor')
def pay(request, fid=0):
    fee = Fee.objects.get(id=fid)
    if request.method == 'POST':
        fee.paid_date = request.POST.get('paid_date') or date.today()
        fee.paid_amount = request.POST.get('paid_amount', fee.due_amount)
        fee.status = 1
        fee.remark = request.POST.get('remark', '')
        fee.save()
        return redirect('myadmin_client_detail', cid=fee.client_id)

    return render(request, 'myadmin/fee/pay.html', {'fee': fee})


@login_required_custom
def remind(request):
    today = date.today()
    if request.user.role == 'accountant':
        overdue = Fee.objects.filter(
            client__accountant=request.user, client__status=1,
            status__in=[0, 2], due_date__lte=today
        )
    else:
        overdue = Fee.objects.filter(
            client__status=1, status__in=[0, 2], due_date__lte=today
        )

    for fee in overdue:
        if fee.status == 0:
            fee.status = 2
            fee.save()

    return render(request, 'myadmin/fee/remind.html', {'feelist': overdue})
