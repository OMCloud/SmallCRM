from django.shortcuts import render

from common import common_admin
from common.utils import table_filter
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
# Create your views here.

def index(request):
    return render(request, "common/table_index.html", context={
        'table_list': common_admin.enabled_admins
    })



def display_table_objs(request, app_name, table_name):
    admin_class = common_admin.enabled_admins[app_name][table_name]


    object_list, filter_conditions = table_filter(request, admin_class)
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
        "filter_conditions": filter_conditions
    })