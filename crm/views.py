from django.shortcuts import render

from crm import forms
from crm.models import Enrollment,Customer
from django.db import IntegrityError
# Create your views here.

def index(request):
    return  render(request, "index.html")

def customer_list(request):
    return  render(request, "sales/customers.html")

def enrollment(request, customer_id):
    customer_obj = Customer.objects.get(id=customer_id)
    msgs = {}
    if request.method == "POST":
        enroll_form = forms.EnrollmentForm(request.POST)
        if enroll_form.is_valid():
            try:
                enroll_form.cleaned_data["customer"] = customer_obj
                enroll_obj = Enrollment.objects.create(**enroll_form.cleaned_data)
                msgs["msgs"] = '''请让用户填写连接内容:http://127.0.0.1:8000/crm/customer/registration/%s/''' % enroll_obj.id
            except  IntegrityError as  e:
                enroll_obj = Enrollment.objects.get(customer_id=customer_obj.id, enrolled_class_id=enroll_form.cleaned_data.get("enrolled_class").id)
                enroll_form.add_error("__all__", "该记录已经存在")
                msgs["msgs"] = '''请让用户填写连接内容:http://127.0.0.1:8000/crm/customer/enrollment/%s/''' % enroll_obj.id
    else:
        enroll_form = forms.EnrollmentForm()
    return  render(request, "sales/enrollment.html", context={
        "enroll_form": enroll_form,
        "customer_obj": customer_obj,
        "msgs": msgs
    })


def registration(request, enroll_id):
    enroll_obj = Enrollment.objects.get(id=enroll_id)
    customer_form = forms.CustomerForm(instance=enroll_obj.customer)
    return render(request, "sales/stu_registration.html", context={
        "customer_form": customer_form,
        "enroll_obj": enroll_obj
    })