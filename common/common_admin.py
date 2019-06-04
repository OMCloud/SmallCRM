from django.shortcuts import render,redirect
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
    list_display = ['id', 'qq','name','source','consultant','consult_course','date','status']
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

class CustomerFollowUpAdmin(BaseAdmin):
    list_display = ['id', 'customer', 'content', 'consultant']
    list_filters = ['customer', 'content', 'consultant',]
    search_filter = ['id', 'content',]
    list_per_page =5


class UserProfileAdmin(BaseAdmin):
    list_display = ('email', 'name')
    readonly_fields = ('password')


def register(model_class, admin_class=None):
    if model_class._meta.app_label not in enabled_admins:
        enabled_admins[model_class._meta.app_label] = {}
    admin_class.model = model_class
    enabled_admins[model_class._meta.app_label][model_class._meta.model_name] = admin_class

register(models.Customer, CustomerAdmin)
register(models.CustomerFollowUp, CustomerFollowUpAdmin)
register(models.UserProfile, UserProfileAdmin)