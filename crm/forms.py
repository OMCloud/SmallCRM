from django.forms import ModelForm
from crm import models


class CustomerForm(ModelForm):
    def __new__(cls, *args, **kwargs):
        for field_name, field_obj in cls.base_fields.items():
            field_obj.widget.attrs['class'] = 'form-control'
            if field_name in cls.Meta.readonly_fields:
                field_obj.widget.attrs['disabled'] = 'disabled'

        return ModelForm.__new__(cls)

    #验证qq是否与后台一致
    def clean_qq(self):
        if self.instance.qq != self.cleaned_data['qq']:
            self.add_error("qq","qq号码与后台不一致")
        return self.cleaned_data['qq']

    def clean_source(self):
        if self.instance.source != self.cleaned_data['source']:
            self.add_error('source', "客户来源与后台不一致")
        return self.cleaned_data['source']

    def clean_consultant(self):
        if self.instance.consultant != self.cleaned_data['consultant']:
            self.add_error("consultant", "信息与后台不一致")
        return  self.cleaned_data['consultant']


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
