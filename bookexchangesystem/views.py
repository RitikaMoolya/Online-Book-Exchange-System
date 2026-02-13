#from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import login
# from .forms import LoginForm
from books.models import Category

def homepage(request):
    # Get the first 10 categories (excluding 'Others')
    categories = Category.objects.exclude(name="Others")[:10]
    
    return render(request, 'home.html', {
        'categories': categories,
    })

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