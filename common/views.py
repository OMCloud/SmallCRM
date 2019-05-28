from django.shortcuts import render

from common import common_admin
from common.utils import table_filter, sort_table, search_table
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
# Create your views here.

def index(request):
    return render(request, "common/table_index.html", context={
        'table_list': common_admin.enabled_admins
    })



def display_table_objs(request, app_name, table_name):
    admin_class = common_admin.enabled_admins[app_name][table_name]

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