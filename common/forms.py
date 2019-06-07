from django.forms import forms,ModelForm
from django.forms import ValidationError
from django.utils.translation import ugettext as _
from crm import models

class CustomerModelForm(ModelForm):
    class Meta:
        model = models.Customer
        fields = "__all__"


def create_model_form(request, admin_class):
    '''
    动态生成modelform
    :param request: 
    :param admin_class: 
    :return: 
    '''
    def __new__(cls, *args, **kwargs):
        #实现动态添加样式
        for field_name, field_obj in cls.base_fields.items():
            field_obj.widget.attrs['class'] = 'form-control'

            #由于前端是直接由django渲染的，所以这里需要在modelform中为字段添加属性
            if not hasattr(admin_class, "is_add_form"):
                if field_name in admin_class.readonly_fields:
                    field_obj.widget.attrs['disabled'] = 'disabled'

            #自定义字段验证
            if hasattr(admin_class, "clean_%s" % field_name):
                clean_func = getattr(admin_class, "clean_%s" % field_name)
                setattr(cls, "clean_%s" % field_name, clean_func)

        return  ModelForm.__new__(cls)

    #表单验证默认执行的方法
    def default_clean(self):
        error_list = []

        #验证表的是否只读
        if admin_class.readonly_table:
            raise ValidationError(
                            _('table % (table_name)s is readonly'),
                            code='invalid',
                            params={'table_name': admin_class.model._meta.model_name }
                        )

        if self.instance.id:  #根据instance.id 验证表单是添加还是修改
            for field in admin_class.readonly_fields:
                val = getattr(self.instance, field)  #从数据库取当前对象的字段值
                #针对多对多字段
                if hasattr(val, "select_related"):
                    m2m_obj = getattr(val, "select_related")().select_related()
                    m2m_values = [o[0] for o in m2m_obj.values_list("id")]
                    #将列表转换成set集合，便于比较
                    set_m2m_vals = set(m2m_values)
                    set_m2m_vals_form_frontend = set([i.id for i in self.cleaned_data.get(field)])
                    if set_m2m_vals != set_m2m_vals_form_frontend:
                        error_list.append(ValidationError(
                            _('Field % (field)s is readonly'),
                            code='invalid',
                            params={'field': field}
                        ))
                    continue

                #常规字段
                val_from_frontend = self.cleaned_data.get(field) #获取从前端传入的字段值
                if val != val_from_frontend:
                    error_list.append(ValidationError(
                        _('Field % (field)s is readonly, data should be %(val)'),
                        code='invalid',
                        params={'field': field, 'val':val}
                    ))

        self.ValidationError = ValidationError

        #实现用户的自定义验证
        valid_response = admin_class.default_form_validation(self)
        if valid_response:
            error_list.append(valid_response)

        #抛出验证异常
        if error_list:
            raise ValidationError(error_list)

    class Meta:
        model = admin_class.model
        fields = "__all__"
        exclude = admin_class.modelform_exclude_fields
    attrs = {"Meta":Meta}
    #通过type动态生成类
    _model_form_class = type("DynamicModelForm", (ModelForm,), attrs)
    setattr(_model_form_class, '__new__', __new__)
    setattr(_model_form_class, 'clean', default_clean)
    return _model_form_class