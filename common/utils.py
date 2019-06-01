#!-*- coding:utf8 -*-
from django.db.models import Q
#实现查询结果的过滤
def table_filter(request, admin_class):
    filter_conditions = {}
    for k, v in request.GET.items():
        if k == "page" or k == 'o' or k=="_q": #分页关键字和排序关键字不能用作查询条件
            continue
        if v:
            filter_conditions[k] = v
    #自定义排序
    default_order = "-%s" % admin_class.ordering if admin_class.ordering else "-id"
    return admin_class.model.objects.filter(**filter_conditions).order_by(default_order), filter_conditions


def sort_table(request, object_list):
    #根据请求获取需要排序的字段
    orderby_key = request.GET.get("o")
    if orderby_key:
        #如果排序的字段存在，则根据字段对查询结果进行排序
        object_list = object_list.order_by(orderby_key)
        #对排序条件取反
        if orderby_key.startswith("-"):
            orderby_key = orderby_key.strip("-")
        else:
            orderby_key = "-%s" % orderby_key
    #返回排序后的结果，和取反后的查询条件
    return object_list, orderby_key

def search_table(request, admin_class, object_list):
    search_key = request.GET.get("_q","")
    q = Q()
    q.connector = "OR"
    for column in admin_class.search_filter:
        q.children.append(("%s__contains" % column, search_key))
    search_result = object_list.filter(q)
    return  search_result
