from crm import models

enabled_admins = {}

class BaseAdmin(object):
    list_display = []
    list_filters = []
    search_filter = []
    list_per_page = 10
    ordering = None

class CustomerAdmin(BaseAdmin):
    list_display = ['id', 'qq','name','source','consultant','consult_course','date','status']
    list_filters = ['source','consultant','consult_course','status', 'date']
    search_filter = ['id', 'qq','name']
    list_per_page = 5   #自定义每页显示的页数
    ordering = "qq"

class CustomerFollowUpAdmin(BaseAdmin):
    list_display = ['customer', 'consultant', 'date']
    search_filter = ['customer', 'consultant']
    list_per_page =5

def register(model_class, admin_class=None):
    if model_class._meta.app_label not in enabled_admins:
        enabled_admins[model_class._meta.app_label] = {}
    admin_class.model = model_class
    enabled_admins[model_class._meta.app_label][model_class._meta.model_name] = admin_class

register(models.Customer, CustomerAdmin)
register(models.CustomerFollowUp, CustomerFollowUpAdmin)