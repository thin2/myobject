from django.db import models
from datetime import datetime

# Create your models here.
#账户信息模型
class User(models.Model):
    username = models.CharField(max_length=50)     #员工账号
    nickname = models.CharField(max_length=50)     #昵称
    password_hash =models.CharField(max_length=100) #密码
    password_salt =models.CharField(max_length=50) #密码干扰值
    status = models.IntegerField(default=1)
    create_at = models.DateTimeField(default=datetime.now)
    update_at = models.DateTimeField(default=datetime.now)

    def toDict(self):
        return {'id':self.id,'username':self.username,'nickname':self.nickname,'password_hash':self.password_hash,'passward_salt':self.passward_salt,'status':self.status,'create_at':self.create_at,'update_at':self.update_at}

    class Meta:
        db_table = "user" #更改表名