from django import template

register = template.Library()

@register.simple_tag
def render_enroll_contract(enroll_obj):
    #格式化合同模板，自动填充用户信息
    #return enroll_obj.enrolled_class.contract.template.format(QQ=enroll_obj.customer.qq)
    return enroll_obj.enrolled_class.contract.template.format()