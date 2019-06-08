from django.shortcuts import render,HttpResponse,redirect

import random
import string
import os
from crm import forms
from crm.models import Enrollment,Customer, Payment
from django.db import IntegrityError
from django.core.cache import cache

from SmallCRM.settings import ENROLLED_DATA
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
        random_str = "".join(random.sample(string.ascii_lowercase + string.digits, 16))
        if enroll_form.is_valid():
            try:
                enroll_form.cleaned_data["customer"] = customer_obj
                enroll_obj = Enrollment.objects.create(**enroll_form.cleaned_data)
                msgs["msgs"] = '''请让用户填写连接内容:http://127.0.0.1:8000/crm/customer/registration/%s/%s/''' % (enroll_obj.id, random_str)
            except  IntegrityError as  e:
                enroll_obj = Enrollment.objects.get(customer_id=customer_obj.id, enrolled_class_id=enroll_form.cleaned_data.get("enrolled_class").id)

                if enroll_obj.contract_agreed:
                    return redirect("/crm/contract_review/%s/" % enroll_obj.id)
                    #payment_form = forms.PaymentForm()

                enroll_form.add_error("__all__", "该记录已经存在")
                msgs["msgs"] = '''请让用户填写连接内容:http://127.0.0.1:8000/crm/customer/registration/%s/%s/''' % (enroll_obj.id, random_str)
            cache.set(enroll_obj.id, random_str, 1800)
    else:
        enroll_form = forms.EnrollmentForm()
    return  render(request, "sales/enrollment.html", context={
        "enroll_form": enroll_form,
        "customer_obj": customer_obj,
        "msgs": msgs
    })


#验证用户填写的个人信息
def registration(request, enroll_id, random_str):

    #从缓存中获取随机的标识
    enroll_random_str = cache.get(enroll_id)

    print(enroll_random_str)

    if enroll_random_str == random_str:

        enroll_obj = Enrollment.objects.get(id=enroll_id)
        #标志报名状态
        status = 0
        if request.method == "POST":

            #判断是否为ajax请求
            if request.is_ajax():
                enroll_data_dir = "%s/%s" % (ENROLLED_DATA, enroll_id)
                if not os.path.exists(enroll_data_dir):
                    os.makedirs(enroll_data_dir, exist_ok=True)

                #从请求中获取上传的文件信息
                for k,file_obj in request.FILES.items():
                    with open("%s/%s" % (enroll_data_dir, file_obj.name), "wb") as f:
                        for chunk in file_obj.chunks():
                            f.write(chunk)
                return HttpResponse("Up Success!")


            customer_form = forms.CustomerForm(request.POST, instance=enroll_obj.customer)
            if customer_form.is_valid():
                customer_form.save()
                #修改报名表合同状态（用户是否同意合同）
                enroll_obj.contract_agreed = True
                enroll_obj.save()
                status = 1
                return render(request, "sales/stu_registration.html", context={
                    "status": status
                })
        else:
            if enroll_obj.contract_agreed == True:
                status = 1
            else:
                status = 0
            customer_form = forms.CustomerForm(instance=enroll_obj.customer)
        return render(request, "sales/stu_registration.html", context={
                "customer_form": customer_form,
                "enroll_obj": enroll_obj,
                "status": status
            })
    else:
        return HttpResponse("链接失效！")


#生成审核页面
def contract_review(request, enroll_id):
    enroll_obj = Enrollment.objects.get(id = enroll_id)
    enroll_form = forms.EnrollmentForm(instance=enroll_obj)
    customer_form = forms.CustomerForm(instance=enroll_obj.customer)

    return render(request, 'sales/contract_review.html', context={
        "enroll_form": enroll_form,
        "enroll_obj": enroll_obj,
        "customer_form": customer_form
    })


#驳回报名申请，返回报名页面
def enrollment_rejection(request,enroll_id ):
    enroll_obj = Enrollment.objects.get(id=enroll_id)
    enroll_obj.contract_agreed = False
    enroll_obj.save()

    return  redirect("/crm/customer/%s/enrollment/" % enroll_obj.id)

#用户缴费，并生成记录
def payment(request, enroll_id):
    errors = []
    enroll_obj = Enrollment.objects.get(id=enroll_id)

    if request.method == "POST":
        payment_amount = request.POST.get("amount")
        if payment_amount:
            payment_amount = int(payment_amount)
            if payment_amount < 500:
                errors.append("缴费金额太小，不能低于500")
            else:
                payment_obj = Payment.objects.create(
                    customer = enroll_obj.customer,
                    course = enroll_obj.enrolled_class.course,
                    amount = payment_amount,
                    consultant = enroll_obj.consultant
                )
                enroll_obj.contract_approved = True
                enroll_obj.save()

                enroll_obj.customer.status = 0
                enroll_obj.customer.save()

                return redirect("/common/crm/customer/")
        else:
            errors.append("缴费金额太小，不能低于500")
    return render(request, "sales/payment.html", context={
        "enroll_obj": enroll_obj,
        "errors": errors
    })
