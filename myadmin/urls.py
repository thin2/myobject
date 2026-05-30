from django.urls import path
from myadmin.views import index, auth, user, client, fee, salary, worklog, report

urlpatterns = [
    # 认证
    path('login/', auth.login, name='myadmin_login'),
    path('logout/', auth.logout, name='myadmin_logout'),

    # 仪表盘
    path('', index.index, name='myadmin_index'),

    # 员工管理
    path('user/<int:pIndex>/', user.index, name='myadmin_user_index'),
    path('user/add/', user.add, name='myadmin_user_add'),
    path('user/insert/', user.insert, name='myadmin_user_insert'),
    path('user/del/<int:uid>/', user.delete, name='myadmin_user_delete'),
    path('user/edit/<int:uid>/', user.edit, name='myadmin_user_edit'),
    path('user/update/<int:uid>/', user.update, name='myadmin_user_update'),

    # 客户管理
    path('client/<int:pIndex>/', client.index, name='myadmin_client_index'),
    path('client/add/', client.add, name='myadmin_client_add'),
    path('client/insert/', client.insert, name='myadmin_client_insert'),
    path('client/del/<int:cid>/', client.delete, name='myadmin_client_delete'),
    path('client/edit/<int:cid>/', client.edit, name='myadmin_client_edit'),
    path('client/update/<int:cid>/', client.update, name='myadmin_client_update'),
    path('client/detail/<int:cid>/', client.detail, name='myadmin_client_detail'),
    path('client/assign/<int:cid>/', client.assign, name='myadmin_client_assign'),

    # 收费管理
    path('fee/<int:pIndex>/', fee.index, name='myadmin_fee_index'),
    path('fee/add/<int:cid>/', fee.add, name='myadmin_fee_add'),
    path('fee/pay/<int:fid>/', fee.pay, name='myadmin_fee_pay'),
    path('fee/remind/', fee.remind, name='myadmin_fee_remind'),

    # 薪酬管理
    path('salary/<int:pIndex>/', salary.index, name='myadmin_salary_index'),
    path('salary/calculate/', salary.calculate, name='myadmin_salary_calculate'),
    path('salary/mine/', salary.mine, name='myadmin_salary_mine'),

    # 工作日志
    path('worklog/<int:pIndex>/', worklog.index, name='myadmin_worklog_index'),
    path('worklog/add/', worklog.add, name='myadmin_worklog_add'),
    path('worklog/insert/', worklog.insert, name='myadmin_worklog_insert'),

    # 经营报表
    path('report/', report.index, name='myadmin_report_index'),
]
