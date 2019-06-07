from django.forms import ModelForm
from crm import models


class CustomerForm(ModelForm):
    def __new__(cls, *args, **kwargs):
        for field_name, field_obj in cls.base_fields.items():
            field_obj.widget.attrs['class'] = 'form-control'
            if field_name in cls.Meta.readonly_fields:
                field_obj.widget.attrs['disabled'] = 'disabled'

        return ModelForm.__new__(cls)
    class Meta:
        model = models.Customer
        fields = '__all__'
        exclude = ('tags','content','memo','status','referral_from','consult_course')

        #自己添加的只读属性，需要自己处理
        readonly_fields = ("qq", 'consultant','source')



class EnrollmentForm(ModelForm):
    def __new__(cls, *args, **kwargs):
        for field_name, field_obj in cls.base_fields.items():
            field_obj.widget.attrs['class'] = 'form-control'

        return ModelForm.__new__(cls)
    class Meta:
        model = models.Enrollment
        fields = ['enrolled_class', 'consultant']
