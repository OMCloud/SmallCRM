from django import template
from django.db.models import Sum

register = template.Library()

@register.simple_tag
def get_score(enroll_obj, stu_account):
    # study_records = enroll_obj.studyrecord_set.filter(course_record__from_class_id=enroll_obj.enrolled_class.id)
    study_records = enroll_obj.studyrecord_set.filter(course_record__from_class_id=enroll_obj.enrolled_class.id)
    return study_records.aggregate(Sum('socre'))
    #return study_records