from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from myadmin.decorators import login_required_custom


def login(request):
    if request.method == 'GET':
        if request.user.is_authenticated:
            return redirect('myadmin_index')
        return render(request, 'myadmin/auth/login.html')

    username = request.POST.get('username', '')
    password = request.POST.get('password', '')
    if not username or not password:
        return render(request, 'myadmin/auth/login.html', {'error': '请输入账号和密码'})

    user = authenticate(request, username=username, password=password)
    if user is None:
        return render(request, 'myadmin/auth/login.html', {'error': '账号或密码错误', 'username': username})
    if user.status != 1:
        return render(request, 'myadmin/auth/login.html', {'error': '账号已被禁用', 'username': username})

    auth_login(request, user)
    return redirect('myadmin_index')


@login_required_custom
def logout(request):
    auth_logout(request)
    return redirect('myadmin_login')
