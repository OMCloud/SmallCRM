from django.shortcuts import render,redirect,HttpResponse
from crm import models

enabled_admins = {}

class BaseAdmin(object):
    list_display = []
    list_filters = []
    search_filter = []
    list_per_page = 10
    ordering = None
    filter_horizontal = []
    actions = ["delete_selected_objs"]
    readonly_fields = []
    readonly_table = False
    modelform_exclude_fields = ()
    
    def enroll(self):
        if self.instance.status == 0:
            return '''<a href="/crm/customer/%s/enrollment/">报名新课程</a>''' % self.instance.id
        else:
            return '''<a href="/crm/customer/%s/enrollment/">报名</a>''' % self.instance.id

    enroll.display_name = "报名课程"


    def default_form_validation(self):
        pass
        # '''
        # 用户自定义表单验证
        # :return:
        # '''
        # content = self.cleaned_data.get("content", "")
        # if len(content) < 15:
        #     return self.ValidationError(
        #         ('Field %(field)s 咨询内容不能少于15个字符'),
        #         code='invalid',
        #         params = {'field': "content"}
        # )

    def delete_selected_objs(self, request, querysets):
        '''
        自定义action，执行对所选择数据集的自定义操作
        :param request: 
        :param querysets: 
        :return: 
        '''
        app_name = self.model._meta.app_label
        table_name = self.model._meta.model_name
        errors = ""
        if request.POST.get("delete_confirm") == "yes":
            if not self.readonly_table:
                querysets.delete()
                return redirect("/common/%s/%s/" % (app_name, table_name))
            else:
                errors = "table %s read only!" % self.model._meta.model_name
        selected_ids = ','.join([str(i.id) for i in querysets])
        return render(request,"common/table_delete.html", context={
        "objs": querysets,
        "admin_class": self,
        "app_name": app_name,
        'table_name': table_name,
        "selected_ids": selected_ids,
        "action": request._action,
        "errors": errors
    })

class CustomerAdmin(BaseAdmin):
    list_display = ['id', 'qq','name','source','consultant','consult_course','date','status', 'enroll']
    list_filters = ['source','consultant','consult_course','status', 'date']
    search_filter = ['id', 'qq','name']
    list_per_page = 5   #自定义每页显示的页数
    ordering = "qq"
    filter_horizontal = ['tags']
    readonly_fields = ['qq', 'consultant', 'tags']
    readonly_table = False

    #自定义字段过滤
    def clean_name(self):
        if not self.cleaned_data['name']:
            self.add_error("name", "不能为空!")

    def default_form_validation(self):
        '''
        用户自定义表单验证
        :return: 
        '''
        content = self.cleaned_data.get("content", "")
        if len(content) < 15:
            return self.ValidationError(
                ('Field %(field)s 咨询内容不能少于15个字符'),
                code='invalid',
                params = {'field': "content"}
        )

class CustomerFollowUpAdmin(BaseAdmin):
    list_display = ['id', 'customer', 'content', 'consultant']
    list_filters = ['customer', 'content', 'consultant',]
    search_filter = ['id', 'content',]
    list_per_page =5


class UserProfileAdmin(BaseAdmin):
    list_display = ('email', 'name')
    readonly_fields = ('password')
    filter_horizontal = ('user_permissions', "groups")
    modelform_exclude_fields = ("last_login",)



class CourseRecordAdmin(BaseAdmin):
    list_display = ['from_class', 'day_num', 'teacher', 'has_homework', 'homework_title', 'date']


    def initialize_studyrecords(self, request, queryset):
        if len(queryset) > 1:
            return HttpResponse("不能选择多个班级")
        new_obj_list = []
        for enroll_obj in queryset[0].from_class.enrollment_set.all():
            new_obj_list.append(
                models.StudyRecord(
                    student = enroll_obj,
                    course_record = queryset[0],
                    attendance = 0,
                    socre = 0,
                )
            )
        try:
            #批量创建
            models.StudyRecord.objects.bulk_create(new_obj_list)
        except Exception as e:
            return HttpResponse("批量创建失败！")
        return redirect("/common/crm/studyrecord/?course_record=%s" % queryset[0].id)

    #django后台自定义动作名称
    initialize_studyrecords.short_description = "初始化本节所有学员的上课记录"
    #django 自定义动作
    actions = ['initialize_studyrecords', ]



class StudyRecordAdmin(BaseAdmin):
    list_display = ['student', 'course_record', 'attendance', 'socre', 'date']
    list_filter = ['course_record', 'socre', 'attendance', 'course_record__from_class', 'student']
    #可编辑
    list_editable = ['socre', 'attendance']




def register(model_class, admin_class=None):
    if model_class._meta.app_label not in enabled_admins:
        enabled_admins[model_class._meta.app_label] = {}
    admin_class.model = model_class
    enabled_admins[model_class._meta.app_label][model_class._meta.model_name] = admin_class

register(models.Customer, CustomerAdmin)
register(models.CustomerFollowUp, CustomerFollowUpAdmin)
register(models.UserProfile, UserProfileAdmin)
register(models.CourseRecord, CourseRecordAdmin)
register(models.StudyRecord, StudyRecordAdmin)