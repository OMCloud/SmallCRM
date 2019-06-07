from django.shortcuts import render, redirect

from common import common_admin
from common.utils import table_filter, sort_table, search_table
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
# Create your views here.
from common.forms import create_model_form

def index(request):
    return render(request, "common/table_index.html", context={
        'table_list': common_admin.enabled_admins
    })



def display_table_objs(request, app_name, table_name):
    admin_class = common_admin.enabled_admins[app_name][table_name]
    if request.method == "POST":
        selected_ids = request.POST.get("selected_ids")
        action = request.POST.get("action")
        if selected_ids:
            selected_obj = admin_class.model.objects.filter(id__in=selected_ids.split(","))
        else:
            raise KeyError("No object select!")
        if hasattr(admin_class, action):
            action_func = getattr(admin_class, action)
            request._action = action
            return action_func(admin_class, request, selected_obj)

    #获取过滤后的结果集合
    object_list, filter_conditions = table_filter(request, admin_class)

    #获取排序后的结果和取反后的查询条件
    object_list,orderby_key = sort_table(request, object_list)

    object_list = search_table(request, admin_class, object_list)
    #分页
    paginator = Paginator(object_list, admin_class.list_per_page)

    page = request.GET.get('page')
    try:
        query_sets = paginator.page(page)
    except PageNotAnInteger:
        query_sets = paginator.page(1)
    except EmptyPage:
        query_sets = paginator.page(paginator.num_pages)


    return  render(request, "common/table_objs.html", context={
        "admin_class": admin_class,
        "query_sets": query_sets,
        "filter_conditions": filter_conditions,
        "orderby_key": orderby_key,
        "pre_orderby_key": request.GET.get("o", ""),
        "search_text": request.GET.get("_q", "")
    })



def table_obj_change(request, app_name, table_name, id):
    '''
    修改表
    :param request: 
    :param app_name: 
    :param table_name: 
    :param id: 
    :return: 
    '''
    admin_class = common_admin.enabled_admins[app_name][table_name]
    model_form_class = create_model_form(request, admin_class)
    obj = admin_class.model.objects.get(id=id)
    if request.method == "POST":
        form_obj = model_form_class(request.POST, instance=obj)
        if form_obj.is_valid():
            form_obj.save()
    else:
        form_obj = model_form_class(instance=obj)
    return render(request, "common/table_change.html", context={
        "form_obj": form_obj,
        "admin_class":admin_class,
        "app_name":app_name,
        "table_name": table_name
    })

def table_obj_add(request, app_name, table_name):
    admin_class = common_admin.enabled_admins[app_name][table_name]
    model_form_class = create_model_form(request, admin_class)
    admin_class.is_add_form = True
    if request.method == "POST":
        form_obj = model_form_class(request.POST)
        if form_obj.is_valid():
            form_obj.save()
            return redirect(request.path.replace("/add/","/"))
    else:
        form_obj = model_form_class()
    return render(request, "common/table_add.html", context={
        "form_obj": form_obj,
        "admin_class": admin_class,
    })


def table_obj_delete(request, app_name, table_name, id):
    admin_class = common_admin.enabled_admins[app_name][table_name]
    obj = admin_class.model.objects.get(id=id)
    errors = ""
    if request.method == "POST":
        if not admin_class.readonly_table:
            obj.delete()
            return redirect("/common/%s/%s" % (app_name, table_name))
        else:
            errors = "table %s read only!" % admin_class.model._meta.model_name

    #与批量删除功能相兼容
    objs = [obj,]
    return render(request, "common/table_delete.html", context={
        "objs": objs,
        "admin_class": admin_class,
        "app_name": app_name,
        'table_name': table_name,
        'errors': errors
    })


def change_password(request, app_name, table_name, id):
    admin_class = common_admin.enabled_admins[app_name][table_name]
    obj = admin_class.model.objects.get(id=id)
    error = {}
    if request.method == "POST":
        print(request.method)
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")
        if password2 == password1:
            #更新设置密码
            obj.set_password(password1)
            obj.save()
            return redirect(request.path.rstrip("password/"))
        else:
            error['invalid_password'] = "password not the same"
    return render(request, "common/change_password.html", context={
        "obj": obj,
        "errors": error
    })
