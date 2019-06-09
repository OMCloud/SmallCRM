from django.shortcuts import render,redirect
from django.contrib.auth import authenticate,login, logout

# Create your views here.

# def index(request):
#     return  render(request, "index.html")
#
# def customer_list(request):
#     return  render(request, "sales/customers.html")

def user_login(request):
    errors = {}
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        #基于django自带的验证，进行用户验证，如果验证存在则返回用户对象，如果不存在则返回空

        user = authenticate(username = email, password = password)
        if user:
            print("####################")
            login(request, user)
            next_url = request.GET.get("next", "/crm/")
            return redirect(next_url)
        else:
            errors['error']  = "用户名或密码不正确"
    return render(request, "login.html", context={
        "errors" : errors
    })

def user_logout(request):
    logout(request)
    return redirect("/login/")


def index(request):
    return render(request, "index.html")

