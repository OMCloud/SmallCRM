from django.shortcuts import render, HttpResponse
import os
import json
import time

from crm import models
from SmallCRM import settings

# Create your views here.

def index(request):
    return render(request, "student/index.html")


def stu_my_classes(request):
    return render(request, "student/my_classes.html")


def studyrecords(request, enroll_id):
    enroll_obj = models.Enrollment.objects.get(id = enroll_id )
    return render(request,"student/studyrecords.html", context={"enroll_obj": enroll_obj})

def homework_detail(request, studyrecord_id):
    studyrecord_obj = models.StudyRecord.objects.get(id = studyrecord_id)
    homework_path = "{base_dir}/{class_id}/{course_record_id}/{studyrecord_id}/" \
        .format(base_dir=settings.HOMEWORKS_DATA,
                class_id=studyrecord_obj.student.enrolled_class_id,
                course_record_id=studyrecord_obj.course_record_id,
                studyrecord_id=studyrecord_obj.id
                )
    if not os.path.exists(homework_path):
        os.makedirs(homework_path, exist_ok=True)
    if request.method == "POST":
        for k, file_obj in request.FILES.items():
            with open("%s/%s" % (homework_path, file_obj.name), "wb") as f:
                for chunk in file_obj.chunks():
                    f.write(chunk)

    file_lists = []
    for file_name in os.listdir(homework_path):
        file_path = "%s/%s" % (homework_path, file_name)
        modify_time = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(os.stat(file_path).st_mtime))
        file_lists.append([file_name,  os.stat(file_path).st_size,modify_time])

    if request.method == "POST":
        return HttpResponse(json.dumps({"status": 0,
                                        "msg": "file upload success",
                                        "file_lists": file_lists}))



    return render(request, "student/homework_detail.html", context={
        "studyrecord_obj": studyrecord_obj,
        "file_lists": file_lists
    })
