from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser, PermissionsMixin
)
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
# Create your models here.

class Customer(models.Model):
    '''
    客户信息
    '''
    name = models.CharField(max_length=32, blank=True, null=True, help_text="请改为真实姓名")
    qq = models.CharField(verbose_name="QQ",max_length=64,  unique=True)
    qq_name = models.CharField(verbose_name="QQ昵称",max_length=64, blank=True, null=True)
    phone = models.CharField(verbose_name="手机号",max_length=64, blank=True, null=True)
    id_num = models.CharField(verbose_name="身份证号",max_length=64, blank=True, null=True)
    email = models.EmailField(verbose_name="常用邮箱", blank=True, null=True)

    source_choices = (                        #客户来源
                     (1,"转介绍"),
                     (2, "QQ群"),
                     (3, "官网"),
                     (4, "百度推广"),
                     (5, "51CTO"),
                     (6, "知乎"),
                     (7, "V2EX"),
                     (8, "市场推广"),
                     )
    source = models.SmallIntegerField(choices=source_choices)
    referral_from = models.CharField(verbose_name="转介绍人", max_length=64, blank=True)
    consult_course = models.ForeignKey("Course", verbose_name="咨询课程")
    content = models.TextField(verbose_name="咨询详情")
    ##下面这句代码如果再加上null=True,会出现警告错误
    # (fields.W340) null has no effect on ManyToManyField.
    # tags = models.ManyToManyField("Tag", blank=True, null=True)
    tags = models.ManyToManyField("Tag", blank=True)
    consultant = models.ForeignKey("UserProfile")   #课程顾问
    status_choices = ((0, '已报名'),
                      (1, '未报名'))
    status = models.SmallIntegerField(choices=status_choices, default=1)
    memo = models.TextField(blank=True, null=True)  #备注
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.qq

    class Meta:
        verbose_name = "客户"
        verbose_name_plural = "客户"


class Tag(models.Model):
    '''
    标签
    '''
    name = models.CharField(unique=True, max_length=32)
    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "标签"
        verbose_name_plural = "标签"
class CustomerFollowUp(models.Model):
    '''
    客户跟进表
    '''
    customer = models.ForeignKey("Customer")
    content = models.TextField("跟进内容")  #等同于使用verbose_name="跟进内容"
    consultant = models.ForeignKey("UserProfile")  #跟进人(顾问)
    date = models.DateTimeField(auto_now_add=True)
    intention_choices = (
        (0, "2周内"),
        (1, "一个月内"),
        (2, "近期无计划"),
        (3, "已报名"),
        (4, "无计划")
    )  #意向选择

    intention = models.SmallIntegerField(choices=intention_choices) #意向

    def __str__(self):
        return "<%s : %s>" % (self.customer.qq, self.intention)

    class Meta:
        verbose_name = "客户跟进"
        verbose_name_plural = "客户跟进"


class Course(models.Model):
    '''
    课程表
    '''
    name = models.CharField(max_length=64, unique=True)
    price = models.PositiveSmallIntegerField()
    period = models.PositiveSmallIntegerField(verbose_name="周期（月）")
    outline = models.TextField()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "课程"
        verbose_name_plural = "课程"

class Branch(models.Model):
    '''
    地区
    '''
    name = models.CharField(max_length=128, unique=True)
    addr = models.CharField(max_length=128)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "地区"
        verbose_name_plural = "地区"


class ContractTemplate(models.Model):
    '''
    合同模板
    '''
    name = models.CharField("合同模板", max_length=64)
    template = models.TextField()

    def __str__(self):
        return self.name



class ClassList(models.Model):
    '''
    班级
    '''
    branch = models.ForeignKey("Branch", verbose_name="校区")
    course = models.ForeignKey("Course")
    class_type_choices = (
        (0, "面授（脱产）"),
        (1, "面授（周末）"),
        (2, "网络班")
    )

    contract = models.ForeignKey("ContractTemplate", blank=True, null=True)

    class_type = models.SmallIntegerField(choices=class_type_choices, verbose_name="课程类型")
    semester = models.PositiveSmallIntegerField(verbose_name="学期")
    teachers = models.ManyToManyField("UserProfile")
    start_date = models.DateField(verbose_name="开始日期")
    end_date = models.DateField(verbose_name="结束日期", blank=True, null=True)

    def __str__(self):
        return "%s %s %s" % (self.branch, self.course, self.semester)

    class Meta:
        unique_together = ("branch", "course", "semester")
        verbose_name = "班级"
        verbose_name_plural = "班级"


class CourseRecord(models.Model):
    '''
    上课记录
    '''
    from_class = models.ForeignKey("ClassList", verbose_name="班级")
    day_num = models.PositiveSmallIntegerField(verbose_name="第几节")
    teacher = models.ForeignKey("UserProfile")
    has_homework = models.BooleanField(default=True)
    homework_title = models.CharField(max_length=128, blank=True, null=True)
    homework_content = models.TextField(blank=True, null=True)
    outline = models.TextField(verbose_name="课程大纲")
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return "%s %s" % (self.from_class, self.day_num)

    class Meta:
        unique_together = ("from_class", "day_num")
        verbose_name = "上课记录"
        verbose_name_plural = "上课记录"



class StudyRecord(models.Model):
    '''
    学习记录
    '''
    student = models.ForeignKey("Enrollment")
    course_record = models.ForeignKey("CourseRecord")
    attendance_choices = (
        (0, "已签到"),
        (1, "迟到"),
        (2, "缺勤"),
        (3, "早退"),
    )
    attendance = models.SmallIntegerField(choices=attendance_choices, default=0)
    score_choices = (
        (100, "A+"),
        (90, "A"),
        (85, "B+"),
        (80, "B"),
        (75, "B-"),
        (70, "C+"),
        (60, "C"),
        (40, "C-"),
        (-50, "D"),
        (0, "N/A"),
    )
    socre = models.SmallIntegerField(choices=score_choices)
    memo = models.TextField(blank=True, null=True)  #备注
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return "%s %s %s" % (self.student, self.course_record, self.socre)

    class Meta:
        unique_together = ("student", "course_record")
        verbose_name = "学习记录"
        verbose_name_plural = "学习记录"

class Enrollment(models.Model):
    '''
    报名表
    '''
    customer = models.ForeignKey("Customer")
    enrolled_class = models.ForeignKey("ClassList", verbose_name="报名班级")
    consultant = models.ForeignKey("UserProfile", verbose_name="课程顾问（商务）")
    contract_agreed = models.BooleanField(default=False, verbose_name="客户已同意合同条款")
    contract_approved = models.BooleanField(default=False, verbose_name="合同已审核")
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "%s %s" % (self.customer, self.enrolled_class)

    class Meta:
        unique_together = ("customer", "enrolled_class")
        verbose_name = "报名"
        verbose_name_plural = "报名"


class Payment(models.Model):
    '''
    缴费记录
    '''
    customer = models.ForeignKey("Customer")
    course = models.ForeignKey("Course", verbose_name="所报课程")
    amount = models.PositiveSmallIntegerField(verbose_name="缴费数额", default=500)
    consultant = models.ForeignKey("UserProfile")
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "%s %s" % (self.customer, self.amount)

    class Meta:
        verbose_name = "缴费记录"
        verbose_name_plural = "缴费记录"


# class UserProfile(models.Model):
#     '''
#     用户信息表
#     '''
#     user = models.OneToOneField(User)
#     name = models.CharField(max_length=32)
#
#     ##下面这句代码如果再加上null=True,会出现警告错误
#     # (fields.W340) null has no effect on ManyToManyField.
#     #roles = models.ManyToManyField("Role", blank=True, null=True)
#     roles = models.ManyToManyField("Role", blank=True)
#
#     def __str__(self):
#         return self.name
#
#     class Meta:
#         verbose_name = "用户"
#         verbose_name_plural = "用户
class UserProfileManager(BaseUserManager):
    def create_user(self, email, name, password=None):
        '''
        基于email 来创建和保存用户
        :param email: 
        :param name: 
        :param password: 
        :return: 
        '''
        if not email:
            raise ValueError("用户名必须是一个邮箱地址")
        user = self.model(email=self.normalize_email(email), name=name)

        user.set_password(password)
        self.is_active = True
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, password):
        '''
        基于邮箱创建超级用户
        :param email: 
        :param name: 
        :param password: 
        :return: 
        '''
        user = self.create_user(email, password=password, name=name)
        user.is_active = True
        user.is_admin = True
        user.save(using=self._db)
        return user


class UserProfile(AbstractBaseUser, PermissionsMixin):
    '''
    用户账号表
    '''
    email = models.EmailField(verbose_name='邮箱地址', max_length=255, unique=True, null=True)
    password = models.CharField(_('password'), max_length=128, help_text=mark_safe('''<a href=password>修改密码</a>'''))
    name = models.CharField(max_length=32)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    roles = models.ManyToManyField("Role", blank=True)
    objects = UserProfileManager()

    stu_account = models.ForeignKey("Customer", verbose_name="关联客户表", blank=True, null=True, help_text="报名后才能创建账号")

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    def get_full_name(self):
        return self.email

    def get_short_name(self):
        return self.email

    def __str__(self):
        return self.email

    # def has_perm(self, perm, obj=None):
    #     return True
    #
    # def has_module_perms(self, app_label):
    #     return True

    @property
    def is_staff(self):
        return self.is_admin

    class Meta:
        permissions = (('can_access_my_course', '可以访问我的课程'),
                       ('can_access_customer_list', '可以访问客户列表'),
                       ('can_access_customer_detail', '可以访问客户详细'),
                       ('can_access_studyrecords', '可以访问学习记录页面'),
                       ('can_access_homework_detail', '可以访问作业详情页面'),
                       ('can_upload_homework', '可以交作业'),
                       ('access_kingadmin_table_obj_detail', '可以访问kingadmin每个表的对象'),
                       ('change_kingadmin_table_obj_detail', '可以修改kingadmin每个表的对象'),
                       )

class Role(models.Model):
    '''
    角色表
    '''
    name = models.CharField(max_length=32, unique=True)
    menus = models.ManyToManyField("Menu", blank=True)

    def __str__(self):
        return  self.name

    class Meta:
        verbose_name = "角色"
        verbose_name_plural = "角色"

class Menu(models.Model):
    '''
    菜单
    '''
    name = models.CharField(max_length=32)
    url_type_choices = ((0, 'alias'),(1, 'absolute_url'))
    url_type = models.SmallIntegerField(choices=url_type_choices, default=0)
    url_name = models.CharField(max_length=64)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "菜单"
        verbose_name_plural = "菜单"


