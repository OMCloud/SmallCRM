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

    def delete_selected_objs(self, request, querysets):
        app_name = self.model._meta.app_label
        table_name = self.model._meta.model_name
        if request.POST.get("delete_confirm") == "yes":
            querysets.delete()
            return redirect("/common/%s/%s/" % (app_name, table_name))
        selected_ids = ','.join([str(i.id) for i in querysets])
        return render(request,"common/table_delete.html", context={
        "objs": querysets,
        "admin_class": self,
        "app_name": app_name,
        'table_name': table_name,
        "selected_ids": selected_ids,
        "action": request._action
    })

class CustomerAdmin(BaseAdmin):
    list_display = ['id', 'qq','name','source','consultant','consult_course','date','status']
    list_filters = ['source','consultant','consult_course','status', 'date']
    search_filter = ['id', 'qq','name']
    list_per_page = 5   #自定义每页显示的页数
    ordering = "qq"
    filter_horizontal = ['tags']

class CustomerFollowUpAdmin(BaseAdmin):
    list_display = ['id', 'customer', 'content', 'consultant']
    list_filters = ['customer', 'content', 'consultant',]
    search_filter = ['id', 'content',]
    list_per_page =5

def register(model_class, admin_class=None):
    if model_class._meta.app_label not in enabled_admins:
        enabled_admins[model_class._meta.app_label] = {}
    admin_class.model = model_class
    enabled_admins[model_class._meta.app_label][model_class._meta.model_name] = admin_class

register(models.Customer, CustomerAdmin)
register(models.CustomerFollowUp, CustomerFollowUpAdmin)