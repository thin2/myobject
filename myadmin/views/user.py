#会计员工信息管理试图文件
from django.shortcuts import render
from django.http import HttpResponse
from django.core.paginator import Paginator
from django.db.models import Q
# Create your views here.
from myadmin.models import User

def index(request, pIndex=1):
    '''浏览信息'''
    umod = User.objects
    ulist = umod.filter(status__lt=9)
    mywhere = []
    #获取并判断搜索条件
    kw = request.GET.get("keyword", None)
    if kw:
        ulist = ulist.filter(Q(username__contains=kw) | Q(nickname__contains=kw))
        mywhere.append("keyword=" + kw)
    # 获取、判断并封装状态status搜索条件
    status = request.GET.get("status", '')
    if status != '':
        ulist = ulist.filter(status=status)
        mywhere.append("status=" + status)

    # 执行分页处理
    pIndex = int(pIndex)
    page = Paginator(ulist, 6)  # 每页八条数据分页
    maxpage = page.num_pages  # 获取最大页数
    # 判断页数是否越界
    if pIndex > maxpage:
        pIndex = maxpage
    if pIndex < 1:
        pIndex = 1
    list2 = page.page(pIndex)  # 获取当前页数据
    plist = page.page_range  # 获取页码列表信息
    context = {"userlist": list2, 'plist': plist, 'pIndex': pIndex, 'maxpage': maxpage, 'mywhere': mywhere}
    return render(request, "myadmin/user/index.html", context)

def add(request):
    '''加载信息添加表单'''
    pass

def insert(request):
    '''执行信息添加'''
    pass

def delete(request,uid=0):
    '''执行信息删除'''
    pass

def edit(request,uid=0):
    '''加载信息编辑表单'''
    pass

def update(request,uid):
    '''执行信息编辑'''
    pass