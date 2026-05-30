from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    ROLE_CHOICES = (
        ('admin', '管理员'),
        ('supervisor', '主管'),
        ('accountant', '会计'),
    )
    GENDER_CHOICES = (
        ('male', '男'),
        ('female', '女'),
    )
    EDUCATION_CHOICES = (
        ('college', '大专'),
        ('bachelor', '本科'),
        ('master', '硕士'),
        ('other', '其他'),
    )
    CERTIFICATE_CHOICES = (
        ('none', '无'),
        ('accounting', '会计证'),
        ('intermediate', '中级会计师'),
        ('senior', '高级会计师'),
    )

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='accountant', verbose_name='角色')
    phone = models.CharField(max_length=20, blank=True, verbose_name='手机号')
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True, verbose_name='性别')
    age = models.IntegerField(null=True, blank=True, verbose_name='年龄')
    education = models.CharField(max_length=20, choices=EDUCATION_CHOICES, blank=True, verbose_name='学历')
    major = models.CharField(max_length=50, blank=True, verbose_name='专业')
    certificate = models.CharField(max_length=20, choices=CERTIFICATE_CHOICES, default='none', verbose_name='证书')
    work_years = models.IntegerField(default=0, verbose_name='工龄')
    hire_date = models.DateField(null=True, blank=True, verbose_name='入职日期')
    status = models.IntegerField(default=1, verbose_name='状态')
    create_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    update_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'user'
        verbose_name = '用户'
        verbose_name_plural = '用户'

    def __str__(self):
        return f'{self.get_role_display()} - {self.username}'


class Client(models.Model):
    STATUS_CHOICES = ((1, '正常'), (0, '停用'), (9, '已删除'))
    NATURE_CHOICES = (('small', '小规模纳税人'), ('general', '一般纳税人'))
    CYCLE_CHOICES = (('monthly', '按月'), ('quarterly', '按季'), ('yearly', '按年'))

    client_no = models.CharField(max_length=50, unique=True, verbose_name='客户编号')
    name = models.CharField(max_length=200, verbose_name='企业名称')
    nature = models.CharField(max_length=20, choices=NATURE_CHOICES, default='small', verbose_name='企业性质')
    business_scope = models.TextField(blank=True, verbose_name='经营范围')
    legal_person = models.CharField(max_length=50, blank=True, verbose_name='法人代表')
    contact_name = models.CharField(max_length=50, verbose_name='联系人')
    contact_phone = models.CharField(max_length=20, verbose_name='联系电话')
    address = models.CharField(max_length=300, blank=True, verbose_name='地址')
    fee_start_date = models.DateField(null=True, blank=True, verbose_name='缴费开始日期')
    fee_cycle = models.CharField(max_length=20, choices=CYCLE_CHOICES, default='monthly', verbose_name='缴费周期')
    fee_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='缴费金额')
    status = models.IntegerField(default=1, verbose_name='状态')
    accountant = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='clients', verbose_name='对接会计')
    create_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    update_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'client'
        verbose_name = '客户'
        verbose_name_plural = '客户'

    def __str__(self):
        return self.name


class Fee(models.Model):
    STATUS_CHOICES = ((0, '待缴'), (1, '已缴'), (2, '欠费'))

    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='fees', verbose_name='客户')
    due_date = models.DateField(verbose_name='应收日期')
    due_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='应收金额')
    paid_date = models.DateField(null=True, blank=True, verbose_name='实收日期')
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='实收金额')
    status = models.IntegerField(default=0, verbose_name='状态')
    remark = models.TextField(blank=True, verbose_name='备注')
    create_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'fee'
        ordering = ['-due_date']
        verbose_name = '收费记录'
        verbose_name_plural = '收费记录'

    def __str__(self):
        return f'{self.client.name} - {self.due_date}'


class Salary(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='salaries', verbose_name='员工')
    month = models.CharField(max_length=7, verbose_name='月份')
    base_salary = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='基本工资')
    performance_salary = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='绩效工资')
    total_salary = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='总薪酬')
    remark = models.TextField(blank=True, verbose_name='备注')
    create_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'salary'
        unique_together = ['user', 'month']
        verbose_name = '薪酬'
        verbose_name_plural = '薪酬'

    def __str__(self):
        return f'{self.user.username} - {self.month}'


class WorkLog(models.Model):
    TYPE_CHOICES = (
        ('bookkeeping', '记账'),
        ('tax_filing', '报税'),
        ('invoicing', '开票'),
        ('consulting', '咨询'),
        ('other', '其他'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='worklogs', verbose_name='员工')
    client = models.ForeignKey(Client, on_delete=models.SET_NULL, null=True, blank=True,
                               related_name='worklogs', verbose_name='关联客户')
    date = models.DateField(verbose_name='日期')
    work_type = models.CharField(max_length=20, choices=TYPE_CHOICES, verbose_name='工作类型')
    content = models.TextField(verbose_name='工作内容')
    create_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'worklog'
        ordering = ['-date']
        verbose_name = '工作日志'
        verbose_name_plural = '工作日志'

    def __str__(self):
        return f'{self.user.username} - {self.date} - {self.get_work_type_display()}'
