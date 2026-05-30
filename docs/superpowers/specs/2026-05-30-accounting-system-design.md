# 代账公司管理系统 — 开发设计规范

> 版本：v1.0 | 日期：2026/05/30

---

## 一、技术架构

| 层级 | 技术选型 |
|------|---------|
| 后端框架 | Django 5.1.15 |
| 数据库 | MySQL 8.x (utf8mb4) |
| 认证系统 | Django 内置 auth（AbstractUser 扩展） |
| 权限控制 | 基于角色字段 + Django 装饰器 |
| 前端模板 | AdminLTE 2.x + Bootstrap 3 + jQuery |
| 模板引擎 | Django Template |
| 分页 | Django Paginator |

---

## 二、应用结构

```
myobject/
├── myobject/          # 项目配置
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── myadmin/           # 后台管理应用（所有业务逻辑）
│   ├── models.py      # 所有数据模型
│   ├── views/
│   │   ├── __init__.py
│   │   ├── index.py       # 仪表盘/首页
│   │   ├── auth.py        # 登录/登出
│   │   ├── user.py        # 员工管理
│   │   ├── client.py      # 客户管理
│   │   ├── fee.py         # 收费管理
│   │   ├── salary.py      # 薪酬管理
│   │   ├── worklog.py     # 工作日志
│   │   └── report.py      # 经营报表
│   ├── urls.py
│   ├── decorators.py  # 权限装饰器
│   └── utils.py       # 工具函数
├── web/               # 前台（暂不开发）
├── templates/myadmin/ # 模板文件
├── static/            # 静态资源
└── manage.py
```

---

## 三、数据模型设计

### 3.1 User（用户/员工模型）— 继承 AbstractUser

```python
class User(AbstractUser):
    ROLE_CHOICES = (
        ('admin', '管理员'),
        ('supervisor', '主管'),
        ('accountant', '会计'),
    )
    role = CharField(max_length=20, choices=ROLE_CHOICES, default='accountant')
    phone = CharField(max_length=20, blank=True)
    gender = CharField(max_length=10, choices=GENDER_CHOICES, blank=True)
    age = IntegerField(null=True, blank=True)
    education = CharField(max_length=20, blank=True)       # 学历
    major = CharField(max_length=50, blank=True)           # 专业
    certificate = CharField(max_length=100, blank=True)    # 证书
    work_years = IntegerField(default=0)                   # 工龄
    hire_date = DateField(null=True, blank=True)           # 入职日期
    status = IntegerField(default=1)                       # 1正常 0禁用
    create_at = DateTimeField(auto_now_add=True)
    update_at = DateTimeField(auto_now=True)

    class Meta:
        db_table = 'user'
```

### 3.2 Client（客户/企业模型）

```python
class Client(Model):
    STATUS_CHOICES = ((1,'正常'), (0,'停用'))
    NATURE_CHOICES = (('small','小规模纳税人'), ('general','一般纳税人'))
    CYCLE_CHOICES = (('monthly','按月'), ('quarterly','按季'), ('yearly','按年'))

    client_no = CharField(max_length=50, unique=True)      # 客户编号
    name = CharField(max_length=200)                       # 企业名称
    nature = CharField(max_length=20, choices=NATURE_CHOICES)  # 企业性质
    business_scope = TextField(blank=True)                 # 经营范围
    legal_person = CharField(max_length=50, blank=True)    # 法人代表
    contact_name = CharField(max_length=50)                # 联系人
    contact_phone = CharField(max_length=20)               # 联系电话
    address = CharField(max_length=300, blank=True)        # 地址
    fee_start_date = DateField(null=True, blank=True)      # 缴费开始日期
    fee_cycle = CharField(max_length=20, choices=CYCLE_CHOICES, default='monthly')
    fee_amount = DecimalField(max_digits=10, decimal_places=2, default=0)  # 缴费金额
    status = IntegerField(default=1)
    accountant = ForeignKey(User, on_delete=SET_NULL, null=True, blank=True,
                           related_name='clients')         # 对接会计
    create_at = DateTimeField(auto_now_add=True)
    update_at = DateTimeField(auto_now=True)

    class Meta:
        db_table = 'client'
```

### 3.3 Fee（收费记录模型）

```python
class Fee(Model):
    STATUS_CHOICES = ((0,'待缴'), (1,'已缴'), (2,'欠费'))

    client = ForeignKey(Client, on_delete=CASCADE, related_name='fees')
    due_date = DateField()                                 # 应收日期
    due_amount = DecimalField(max_digits=10, decimal_places=2)  # 应收金额
    paid_date = DateField(null=True, blank=True)           # 实收日期
    paid_amount = DecimalField(max_digits=10, decimal_places=2, default=0)
    status = IntegerField(default=0)
    remark = TextField(blank=True)
    create_at = DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'fee'
        ordering = ['-due_date']
```

### 3.4 Salary（薪酬模型）

```python
class Salary(Model):
    user = ForeignKey(User, on_delete=CASCADE, related_name='salaries')
    month = CharField(max_length=7)                        # 格式：2026-05
    base_salary = DecimalField(max_digits=10, decimal_places=2, default=0)
    performance_salary = DecimalField(max_digits=10, decimal_places=2, default=0)
    total_salary = DecimalField(max_digits=10, decimal_places=2, default=0)
    remark = TextField(blank=True)
    create_at = DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'salary'
        unique_together = ['user', 'month']
```

### 3.5 WorkLog（工作日志模型）

```python
class WorkLog(Model):
    TYPE_CHOICES = (
        ('bookkeeping', '记账'),
        ('tax_filing', '报税'),
        ('invoicing', '开票'),
        ('consulting', '咨询'),
        ('other', '其他'),
    )

    user = ForeignKey(User, on_delete=CASCADE, related_name='worklogs')
    client = ForeignKey(Client, on_delete=SET_NULL, null=True, blank=True)
    date = DateField()
    work_type = CharField(max_length=20, choices=TYPE_CHOICES)
    content = TextField()
    create_at = DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'worklog'
        ordering = ['-date']
```

---

## 四、权限控制设计

### 角色权限矩阵

| 功能 | 管理员 | 主管 | 会计 |
|------|--------|------|------|
| 仪表盘（全局数据） | ✓ | ✓ | ✗ |
| 员工管理（CRUD） | ✓ | ✓（只读） | ✗ |
| 客户管理（全部） | ✓ | ✓ | ✗ |
| 客户管理（自己的） | — | — | ✓ |
| 收费管理 | ✓ | ✓ | 仅查看自己客户 |
| 薪酬管理（全部） | ✓ | ✓ | ✗ |
| 我的薪酬 | — | — | ✓ |
| 工作日志（全部） | ✓ | ✓ | ✗ |
| 工作日志（自己的） | — | — | ✓（读写） |
| 经营报表 | ✓ | ✓ | ✗ |

### 实现方式

通过自定义装饰器实现：

```python
# decorators.py
def role_required(*roles):
    """角色权限装饰器"""
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('myadmin_login')
            if request.user.role not in roles:
                return HttpResponseForbidden('无权限访问')
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator
```

---

## 五、URL 路由规划

```python
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
```

---

## 六、薪酬核算规则

### 基本工资计算

| 因素 | 规则 |
|------|------|
| 学历 | 大专 +500，本科 +1000，硕士 +2000 |
| 证书 | 会计证 +300，中级会计师 +800，高级会计师 +1500 |
| 工龄 | 每年 +200 |
| 基础底薪 | 3000 元 |

`基本工资 = 基础底薪 + 学历加成 + 证书加成 + 工龄×200`

### 绩效工资计算

| 因素 | 单价 |
|------|------|
| 对接客户数 | 每个客户 200 元/月 |
| 报税服务 | 每次 50 元 |
| 开票服务 | 每次 30 元 |

`绩效工资 = 客户数×200 + 当月报税次数×50 + 当月开票次数×30`

`总薪酬 = 基本工资 + 绩效工资`

---

## 七、页面模板规划

所有页面继承 `base.html`，使用 AdminLTE 组件：

| 模板路径 | 功能 |
|---------|------|
| `myadmin/auth/login.html` | 登录页 |
| `myadmin/index/index.html` | 仪表盘 |
| `myadmin/user/index.html` | 员工列表 |
| `myadmin/user/add.html` | 员工添加 |
| `myadmin/user/edit.html` | 员工编辑 |
| `myadmin/client/index.html` | 客户列表 |
| `myadmin/client/add.html` | 客户添加 |
| `myadmin/client/edit.html` | 客户编辑 |
| `myadmin/client/detail.html` | 客户详情（含缴费记录） |
| `myadmin/fee/index.html` | 收费列表 |
| `myadmin/fee/remind.html` | 催收提醒 |
| `myadmin/salary/index.html` | 薪酬列表 |
| `myadmin/salary/mine.html` | 我的薪酬 |
| `myadmin/worklog/index.html` | 工作日志列表 |
| `myadmin/worklog/add.html` | 填写日志 |
| `myadmin/report/index.html` | 经营报表 |

---

## 八、开发规范

### 编码规范

- 视图函数统一返回 `render()` 或 `redirect()`
- POST 操作完成后 redirect 防止重复提交
- 所有表单使用 CSRF token
- 分页统一每页 10 条
- 搜索通过 GET 参数传递，保持分页时搜索条件不丢失
- 删除操作使用软删除（status=9）

### 错误处理

- 表单验证失败：回显表单并显示错误信息
- 权限不足：返回 403 或 redirect 到登录页
- 对象不存在：返回 404

### 侧边栏导航结构

```
仪表盘
员工管理
  └─ 员工列表
客户管理
  └─ 客户列表
  └─ 客户分配
收费管理
  └─ 收费记录
  └─ 催收提醒
薪酬管理
  └─ 薪酬列表
  └─ 我的薪酬（会计可见）
工作日志
  └─ 日志列表
  └─ 填写日志（会计可见）
经营报表（管理员/主管可见）
```

---

## 九、开发顺序

| 阶段 | 内容 | 依赖 |
|------|------|------|
| Phase 1 | User 模型重建 + 登录/登出 + 权限装饰器 | 无 |
| Phase 2 | 员工 CRUD 补全 + 模板 | Phase 1 |
| Phase 3 | Client 模型 + 客户 CRUD + 客户分配 | Phase 1 |
| Phase 4 | Fee 模型 + 收费记录 + 催收提醒 | Phase 3 |
| Phase 5 | WorkLog 模型 + 工作日志 CRUD | Phase 1, 3 |
| Phase 6 | Salary 模型 + 薪酬核算 | Phase 2, 3, 5 |
| Phase 7 | 仪表盘 + 经营报表 | Phase 4, 6 |
| Phase 8 | 侧边栏动态权限 + 整体联调 | 全部 |
