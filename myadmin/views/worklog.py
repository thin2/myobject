from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from django.db.models import Q
from datetime import date
from myadmin.models import WorkLog, Client
from myadmin.decorators import login_required_custom, role_required


@login_required_custom
def index(request, pIndex=1):
    if request.user.role == 'accountant':
        wlist = WorkLog.objects.filter(user=request.user)
    else:
        wlist = WorkLog.objects.all()

    mywhere = []
    kw = request.GET.get("keyword", '')
    if kw:
        wlist = wlist.filter(Q(content__contains=kw) | Q(client__name__contains=kw))
        mywhere.append("keyword=" + kw)

    work_type = request.GET.get("work_type", '')
    if work_type:
        wlist = wlist.filter(work_type=work_type)
        mywhere.append("work_type=" + work_type)

    pIndex = int(pIndex)
    page = Paginator(wlist, 10)
    maxpage = page.num_pages
    if pIndex > maxpage:
        pIndex = maxpage
    if pIndex < 1:
        pIndex = 1
    list2 = page.page(pIndex)
    plist = page.page_range
    context = {"workloglist": list2, 'plist': plist, 'pIndex': pIndex, 'maxpage': maxpage, 'mywhere': mywhere}
    return render(request, "myadmin/worklog/index.html", context)


@login_required_custom
def add(request):
    if request.user.role == 'accountant':
        clients = Client.objects.filter(accountant=request.user, status=1)
    else:
        clients = Client.objects.filter(status=1)
    return render(request, 'myadmin/worklog/add.html', {
        'type_choices': WorkLog.TYPE_CHOICES,
        'clients': clients,
    })


@login_required_custom
def insert(request):
    if request.method != 'POST':
        return redirect('myadmin_worklog_add')

    content = request.POST.get('content', '').strip()
    work_date = request.POST.get('date', '')
    work_type = request.POST.get('work_type', 'other')

    if not content or not work_date:
        if request.user.role == 'accountant':
            clients = Client.objects.filter(accountant=request.user, status=1)
        else:
            clients = Client.objects.filter(status=1)
        return render(request, 'myadmin/worklog/add.html', {
            'error': '日期和工作内容为必填项',
            'type_choices': WorkLog.TYPE_CHOICES,
            'clients': clients,
        })

    client_id = request.POST.get('client', '')
    WorkLog.objects.create(
        user=request.user,
        date=work_date,
        work_type=work_type,
        content=content,
        client_id=client_id if client_id else None,
    )
    return redirect('myadmin_worklog_index', pIndex=1)
