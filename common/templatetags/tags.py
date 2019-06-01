from django import template
from django.utils.safestring import mark_safe
from django.utils.timezone import datetime,timedelta
register = template.Library()

@register.simple_tag
def render_app_name(admin_class):
    return admin_class.model._meta.verbose_name


@register.simple_tag
def get_query_sets(admin_class):
    return admin_class.model.objects.all()


@register.simple_tag
def build_table_row(obj, admin_class, request):
    row_ele = ""
    for index, column in enumerate(admin_class.list_display):
        field_obj = obj._meta.get_field(column)
        if field_obj.choices: #判断是不是为空
            column_data = getattr(obj, "get_%s_display" % column)()
        else:
            column_data = getattr(obj, column)
        if type(column_data).__name__ == 'datetime':
            column_data = column_data.strftime("%Y-%m-%d %H:%M:%S")

        if index == 0: #为第一列添加跳转
            column_data = "<a href='%s%s/change/'>%s</a>" % (request.path, obj.id, column_data)

        row_ele += "<td>%s</td>" % column_data
    return mark_safe(row_ele)

@register.simple_tag
def render_page_ele(loop_counter, query_sets, filter_conditions):
    filters = ''
    for k, v in filter_conditions.items():
        filters += "&%s=%s" % (k,v)

    #前两页和后两页直接显示
    if loop_counter < 3 or loop_counter > query_sets.paginator.num_pages -2:
        ele_class = ""
        if query_sets.number == loop_counter:
            ele_class = "active"
        ele = '''<li class="%s"><a href="?page=%s%s">%s</a></li>''' % (ele_class, loop_counter, filters, loop_counter)
        return mark_safe(ele)

    #当前页的前后页也直接显示
    if abs(query_sets.number - loop_counter) <= 1:
        ele_class = ""
        if query_sets.number == loop_counter:
            ele_class = "active"
        ele = '''<li class="%s"><a href="?page=%s%s">%s</a></li>''' % (ele_class, loop_counter, filters, loop_counter)

        return mark_safe(ele)
    return ''

@register.simple_tag
def render_filter_ele(condition, admin_class, filter_conditions):
    select_ele = '''<select class="form-control" name='%s' ><option value=''>---</option>''' % condition
    field_obj = admin_class.model._meta.get_field(condition)
    if field_obj.choices:
        selected = ''
        for choice_item in field_obj.choices:
            if filter_conditions.get(condition) == str(choice_item[0]):
                selected = "selected"

            select_ele += '''<option value='%s' %s>%s</option>''' % (choice_item[0], selected, choice_item[1])
            selected = ''

    if type(field_obj).__name__ == "ForeignKey":
        selected = ''
        for choice_item in field_obj.get_choices()[1:]:
            if filter_conditions.get(condition) == str(choice_item[0]):
                selected = "selected"
            select_ele += '''<option value='%s' %s>%s</option>''' % (choice_item[0], selected, choice_item[1])
            selected = ''

    if type(field_obj).__name__ in ["DateTimeField", "DateField"]:
        select_ele = '''<select class="form-control" name='%s' ><option value=''>---</option>''' % ("%s__gte" % condition)
        date_list = []
        current_date = datetime.now().date()
        date_list.append(["今天", current_date])
        last_one_day = current_date - timedelta(days=1)
        date_list.append(["昨天", last_one_day])
        last_seven_day = current_date - timedelta(days=7)
        date_list.append(["近七天", last_seven_day])
        mtd = current_date.replace(day=1)
        date_list.append(["本月", mtd])
        last_month_day = current_date - timedelta(days=30)
        date_list.append(["近30天", last_month_day])
        last_180day = current_date - timedelta(days=180)
        date_list.append(["近180天", last_180day])

        selected = ""
        for item in date_list:

            select_ele += '''<option value='%s' %s>%s</option>''' % (item[1], selected, item[0])

    select_ele += "</select>"

    return mark_safe(select_ele)


@register.simple_tag
def build_paginators(query_sets, filter_conditions, pre_orderby_key, search_text):
    flag = True  #用来标识当出现不要展示的页码时，是否使用...
    filters = ''
    for k, v in filter_conditions.items():
        filters += "&%s=%s" % (k, v)

    ele_list = ""


    # 前两页和后两页直接显示
    for loop_counter in query_sets.paginator.page_range:
        if loop_counter < 3 or loop_counter > query_sets.paginator.num_pages - 2:
            ele_class = ""
            if query_sets.number == loop_counter:
                flag = True
                ele_class = "active"
            ele_list += '''<li class="%s"><a href="?page=%s%s&o=%s">%s</a></li>''' % (
            ele_class, loop_counter, filters, pre_orderby_key, loop_counter)
        # 当前页的前一页和后一页也直接显示
        elif abs(query_sets.number - loop_counter) <= 1:
            ele_class = ""
            if query_sets.number == loop_counter:
                flag = True
                ele_class = "active"
            ele_list += '''<li class="%s"><a href="?page=%s%s&o=%s_q=%s">%s</a></li>''' % (
            ele_class, loop_counter, filters, pre_orderby_key, search_text, loop_counter)
        else:
            if flag:
                ele_list += '<li><a>...</a></li>'
                flag = False
    flag = True
    return mark_safe(ele_list)


@register.simple_tag
def build_table_column(column, orderby_key, filter_conditions):
    filters = ''
    for k, v in filter_conditions.items():
        filters += "&%s=%s" % (k, v)

    #根据排序字段重新设置排序条件（取反）
    ele = '''<th><a href="?o=%s%s">%s</a>%s
    </th>'''
    if orderby_key:
        if orderby_key.startswith("-"):
            icon = '''<span class="glyphicon glyphicon-chevron-up" aria-hidden="true"></span>'''
        else:
            icon = '''<span class="glyphicon glyphicon-chevron-down" aria-hidden="true"></span>'''
        #判断是否为排序的字段
        if orderby_key.strip("-") != column:
            orderby_key = column
            icon = ''
    else:
        orderby_key = column
        icon = ''

    ele = ele % (orderby_key, filters, column, icon)


    return mark_safe(ele)


@register.simple_tag
def get_table_name(admin_class):
    '''
    获取表名称
    :param admin_class: 
    :return: 
    '''
    table_name = admin_class.model._meta.verbose_name
    return table_name

@register.simple_tag
def get_m2m_obj_list(admin_class, field, form_obj):
    '''
    获取多对多所有可选数据
    :param admin_class: 
    :param field: 
    :return: 
    '''
    #多对多中某字段的全部选项
    field_obj = getattr(admin_class.model, field.name)
    all_list = field_obj.rel.to.objects.all()

    #判断instance方法是否存在
    if form_obj.instance.id:
        #数据对象中的选中的选项
        instance_field = getattr(form_obj.instance, field.name)
        selected_list = instance_field.all()
    else:
        return all_list

    diff_list = []
    #取差集 == low方法
    for obj in all_list:
        if obj in selected_list:
            pass
        else:
            diff_list.append(obj)
    return diff_list


@register.simple_tag
def get_m2m_selected_obj_list(form_obj, field):
    '''
    返回已选的数据
    :param form_obj: 
    :param field: 
    :return: 
    '''
    if form_obj.instance.id:
        field_obj = getattr(form_obj.instance, field.name)
        return field_obj.all()