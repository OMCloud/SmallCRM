from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Customer(models.Model):
    '''
    客户信息
    '''
    name = models.CharField(max_length=32, blank=True, null=True)
    qq = models.CharField(max_length=64,  unique=True)
    qq_name = models.CharField(max_length=64, blank=True, null=True)
    phone = models.CharField(max_length=64, blank=True, null=True)
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
    tags = models.ManyToManyField("Tag", blank=True, null=True)
    consultant = models.ForeignKey("UserProfile")   #课程顾问
    memo = models.TextField(blank=True, null=True)  #备注
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.qq


class Tag(models.Model):
    '''
    标签
    '''
    name = models.CharField(unique=True, max_length=32)
    def __str__(self):
        return self.name

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


class Branch(models.Model):
    '''
    地区
    '''
    name = models.CharField(max_length=128, unique=True)
    addr = models.CharField(max_length=128)

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
    class_type = models.SmallIntegerField(choices=class_type_choices, verbose_name="课程类型")
    semester = models.PositiveSmallIntegerField(verbose_name="学期")
    teachers = models.ManyToManyField("UserProfile")
    start_date = models.DateField(verbose_name="开始日期")
    end_date = models.DateField(verbose_name="结束日期", blank=True, null=True)

    def __str__(self):
        return "%s %s %s" % (self.branch, self.course, self.semester)

    class Meta:
        unique_together = ("branch", "course", "semester")


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


class UserProfile(models.Model):
    '''
    用户信息表
    '''
    user = models.OneToOneField(User)
    name = models.CharField(max_length=32)
    roles = models.ManyToManyField("Role", blank=True, null=True)

    def __str__(self):
        return self.name


class Role(models.Model):
    '''
    角色表
    '''
    name = models.CharField(max_length=32, unique=True)
    def __str__(self):
        return  self.name


