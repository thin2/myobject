from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from django.db.models import Q
from myadmin.models import Client, User
from myadmin.decorators import login_required_custom, role_required


@login_required_custom
def index(request, pIndex=1):
    if request.user.role == 'accountant':
        clist = Client.objects.filter(status__lt=9, accountant=request.user)
    else:
        clist = Client.objects.filter(status__lt=9)

    mywhere = []
    kw = request.GET.get("keyword", None)
    if kw:
        clist = clist.filter(Q(name__contains=kw) | Q(contact_name__contains=kw) | Q(client_no__contains=kw))
        mywhere.append("keyword=" + kw)

    nature = request.GET.get("nature", '')
    if nature:
        clist = clist.filter(nature=nature)
        mywhere.append("nature=" + nature)

    status = request.GET.get("status", '')
    if status != '':
        clist = clist.filter(status=status)
        mywhere.append("status=" + status)

    pIndex = int(pIndex)
    page = Paginator(clist, 10)
    maxpage = page.num_pages
    if pIndex > maxpage:
        pIndex = maxpage
    if pIndex < 1:
        pIndex = 1
    list2 = page.page(pIndex)
    plist = page.page_range
    context = {"clientlist": list2, 'plist': plist, 'pIndex': pIndex, 'maxpage': maxpage, 'mywhere': mywhere}
    return render(request, "myadmin/client/index.html", context)


@role_required('admin', 'supervisor')
def add(request):
    accountants = User.objects.filter(role='accountant', status=1)
    return render(request, 'myadmin/client/add.html', {
        'nature_choices': Client.NATURE_CHOICES,
        'cycle_choices': Client.CYCLE_CHOICES,
        'accountants': accountants,
    })


@role_required('admin', 'supervisor')
def insert(request):
    if request.method != 'POST':
        return redirect('myadmin_client_add')

    name = request.POST.get('name', '').strip()
    contact_name = request.POST.get('contact_name', '').strip()
    contact_phone = request.POST.get('contact_phone', '').strip()

    if not name or not contact_name or not contact_phone:
        accountants = User.objects.filter(role='accountant', status=1)
        return render(request, 'myadmin/client/add.html', {
            'error': '企业名称、联系人、联系电话为必填项',
            'nature_choices': Client.NATURE_CHOICES,
            'cycle_choices': Client.CYCLE_CHOICES,
            'accountants': accountants,
        })

    client_no = request.POST.get('client_no', '').strip()
    if not client_no:
        last = Client.objects.order_by('-id').first()
        client_no = f"C{(last.id + 1 if last else 1):05d}"

    if Client.objects.filter(client_no=client_no).exists():
        accountants = User.objects.filter(role='accountant', status=1)
        return render(request, 'myadmin/client/add.html', {
            'error': '客户编号已存在',
            'nature_choices': Client.NATURE_CHOICES,
            'cycle_choices': Client.CYCLE_CHOICES,
            'accountants': accountants,
        })

    accountant_id = request.POST.get('accountant', '')
    Client.objects.create(
        client_no=client_no,
        name=name,
        nature=request.POST.get('nature', 'small'),
        business_scope=request.POST.get('business_scope', ''),
        legal_person=request.POST.get('legal_person', ''),
        contact_name=contact_name,
        contact_phone=contact_phone,
        address=request.POST.get('address', ''),
        fee_start_date=request.POST.get('fee_start_date') or None,
        fee_cycle=request.POST.get('fee_cycle', 'monthly'),
        fee_amount=request.POST.get('fee_amount') or 0,
        accountant_id=accountant_id if accountant_id else None,
    )
    return redirect('myadmin_client_index', pIndex=1)


@role_required('admin', 'supervisor')
def delete(request, cid=0):
    client = Client.objects.get(id=cid)
    client.status = 9
    client.save()
    return redirect('myadmin_client_index', pIndex=1)


@role_required('admin', 'supervisor')
def edit(request, cid=0):
    client = Client.objects.get(id=cid)
    accountants = User.objects.filter(role='accountant', status=1)
    context = {
        'client': client,
        'nature_choices': Client.NATURE_CHOICES,
        'cycle_choices': Client.CYCLE_CHOICES,
        'accountants': accountants,
    }
    return render(request, 'myadmin/client/edit.html', context)


@role_required('admin', 'supervisor')
def update(request, cid):
    if request.method != 'POST':
        return redirect('myadmin_client_edit', cid=cid)

    client = Client.objects.get(id=cid)
    client.name = request.POST.get('name', client.name)
    client.nature = request.POST.get('nature', client.nature)
    client.business_scope = request.POST.get('business_scope', '')
    client.legal_person = request.POST.get('legal_person', '')
    client.contact_name = request.POST.get('contact_name', client.contact_name)
    client.contact_phone = request.POST.get('contact_phone', client.contact_phone)
    client.address = request.POST.get('address', '')
    client.fee_start_date = request.POST.get('fee_start_date') or None
    client.fee_cycle = request.POST.get('fee_cycle', 'monthly')
    client.fee_amount = request.POST.get('fee_amount') or 0
    client.status = int(request.POST.get('status', 1))

    accountant_id = request.POST.get('accountant', '')
    client.accountant_id = accountant_id if accountant_id else None
    client.save()
    return redirect('myadmin_client_index', pIndex=1)


@login_required_custom
def detail(request, cid=0):
    client = Client.objects.get(id=cid)
    if request.user.role == 'accountant' and client.accountant != request.user:
        return redirect('myadmin_client_index', pIndex=1)
    fees = client.fees.all()[:20]
    return render(request, 'myadmin/client/detail.html', {'client': client, 'fees': fees})


@role_required('admin', 'supervisor')
def assign(request, cid=0):
    if request.method == 'POST':
        client = Client.objects.get(id=cid)
        accountant_id = request.POST.get('accountant', '')
        client.accountant_id = accountant_id if accountant_id else None
        client.save()
        return redirect('myadmin_client_detail', cid=cid)

    client = Client.objects.get(id=cid)
    accountants = User.objects.filter(role='accountant', status=1)
    return render(request, 'myadmin/client/assign.html', {'client': client, 'accountants': accountants})
