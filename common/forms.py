from django.forms import forms,ModelForm

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
        return  ModelForm.__new__(cls)

    class Meta:
        model = admin_class.model
        fields = "__all__"
    attrs = {"Meta":Meta}
    #通过type动态生成类
    _model_form_class = type("DynamicModelForm", (ModelForm,), attrs)
    setattr(_model_form_class, '__new__', __new__)
    return _model_form_class