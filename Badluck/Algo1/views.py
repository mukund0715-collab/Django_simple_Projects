from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth import authenticate, login, logout
from .forms import SignUpForm
from django.contrib import messages
from .models import DemoRequest
# Create your views here.

def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Automatically log in user after signup
            return redirect('home')  # Redirect after signup
        else:
            messages.error(request, "Please correct the error below.")
    else:
        form = SignUpForm()
    return render(request, 'signin.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "Invalid username or password")
    return render(request, 'login.html')

def home(request):
    return render(request, 'home.html')

def demo_register(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        email = request.POST.get('email')

        # Optionally save to DB
        DemoRequest.objects.create(name=name, phone=phone, email=email)

        # You can also send an email or log it
        print(f"Demo Request: {name}, {phone}, {email}")
        return render(request,"success.html",{'success_message': "We'll Contact you shortly"})
    
    return render(request, 'demo_register.html')