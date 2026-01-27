#from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import login
# from .forms import LoginForm

def homepage(request):
    #return HttpResponse("Hello World! This is home page.")
    return render(request,'home.html')

def services(request):
    #return HttpResponse("This is services page.")
    return render(request,'services.html')

def contactus(request):
    #return HttpResponse("This is services page.")
    return render(request,'contactus.html')

# def login_view(request):
#     if request.method == "POST":
#         form = LoginForm(request, data=request.POST)
#         if form.is_valid():
#             login(request, form.get_user())
#             return redirect("home")  # change to your page
#     else:
#         form = LoginForm()

#     return render(request, "login.html", {"form": form})