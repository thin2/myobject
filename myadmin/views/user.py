from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from django.db.models import Q
from myadmin.models import User
from myadmin.decorators import role_required


@role_required('admin', 'supervisor')
def index(request, pIndex=1):
    ulist = User.objects.filter(status__lt=9)
    mywhere = []

    kw = request.GET.get("keyword", None)
    if kw:
        ulist = ulist.filter(Q(username__contains=kw) | Q(first_name__contains=kw) | Q(phone__contains=kw))
        mywhere.append("keyword=" + kw)

    status = request.GET.get("status", '')
    if status != '':
        ulist = ulist.filter(status=status)
        mywhere.append("status=" + status)

    role = request.GET.get("role", '')
    if role:
        ulist = ulist.filter(role=role)
        mywhere.append("role=" + role)

    pIndex = int(pIndex)
    page = Paginator(ulist, 10)
    maxpage = page.num_pages
    if pIndex > maxpage:
        pIndex = maxpage
    if pIndex < 1:
        pIndex = 1
    list2 = page.page(pIndex)
    plist = page.page_range
    context = {"userlist": list2, 'plist': plist, 'pIndex': pIndex, 'maxpage': maxpage, 'mywhere': mywhere}
    return render(request, "myadmin/user/index.html", context)


@role_required('admin')
def add(request):
    return render(request, 'myadmin/user/add.html', {
        'role_choices': User.ROLE_CHOICES,
        'gender_choices': User.GENDER_CHOICES,
        'education_choices': User.EDUCATION_CHOICES,
        'certificate_choices': User.CERTIFICATE_CHOICES,
    })


@role_required('admin')
def insert(request):
    if request.method != 'POST':
        return redirect('myadmin_user_add')

    username = request.POST.get('username', '').strip()
    password = request.POST.get('password', '').strip()
    first_name = request.POST.get('first_name', '').strip()

    if not username or not password or not first_name:
        context = {
            'error': '账号、密码、姓名为必填项',
            'role_choices': User.ROLE_CHOICES,
            'gender_choices': User.GENDER_CHOICES,
            'education_choices': User.EDUCATION_CHOICES,
            'certificate_choices': User.CERTIFICATE_CHOICES,
        }
        return render(request, 'myadmin/user/add.html', context)

    if User.objects.filter(username=username).exists():
        context = {
            'error': '账号已存在',
            'role_choices': User.ROLE_CHOICES,
            'gender_choices': User.GENDER_CHOICES,
            'education_choices': User.EDUCATION_CHOICES,
            'certificate_choices': User.CERTIFICATE_CHOICES,
        }
        return render(request, 'myadmin/user/add.html', context)

    user = User.objects.create_user(
        username=username,
        password=password,
        first_name=first_name,
        role=request.POST.get('role', 'accountant'),
        phone=request.POST.get('phone', ''),
        gender=request.POST.get('gender', ''),
        age=request.POST.get('age') or None,
        education=request.POST.get('education', ''),
        major=request.POST.get('major', ''),
        certificate=request.POST.get('certificate', 'none'),
        work_years=request.POST.get('work_years') or 0,
        hire_date=request.POST.get('hire_date') or None,
    )
    return redirect('myadmin_user_index', pIndex=1)


@role_required('admin')
def delete(request, uid=0):
    user = User.objects.get(id=uid)
    user.status = 9
    user.save()
    return redirect('myadmin_user_index', pIndex=1)


@role_required('admin')
def edit(request, uid=0):
    user = User.objects.get(id=uid)
    context = {
        'user': user,
        'role_choices': User.ROLE_CHOICES,
        'gender_choices': User.GENDER_CHOICES,
        'education_choices': User.EDUCATION_CHOICES,
        'certificate_choices': User.CERTIFICATE_CHOICES,
    }
    return render(request, 'myadmin/user/edit.html', context)


@role_required('admin')
def update(request, uid):
    if request.method != 'POST':
        return redirect('myadmin_user_edit', uid=uid)

    user = User.objects.get(id=uid)
    user.first_name = request.POST.get('first_name', user.first_name)
    user.role = request.POST.get('role', user.role)
    user.phone = request.POST.get('phone', '')
    user.gender = request.POST.get('gender', '')
    user.age = request.POST.get('age') or None
    user.education = request.POST.get('education', '')
    user.major = request.POST.get('major', '')
    user.certificate = request.POST.get('certificate', 'none')
    user.work_years = request.POST.get('work_years') or 0
    user.hire_date = request.POST.get('hire_date') or None
    user.status = int(request.POST.get('status', 1))

    password = request.POST.get('password', '').strip()
    if password:
        user.set_password(password)

    user.save()
    return redirect('myadmin_user_index', pIndex=1)
