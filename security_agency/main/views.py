
from django.shortcuts import render, get_object_or_404, redirect
from .models import Guard
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages

def home(request):
    featured_guards = Guard.objects.all()[:3]  # Get 3 guards
    return render(request, 'home.html', {'featured_guards': featured_guards})


def services(request):
    return render(request, 'services.html')

def guards(request):
    all_guards = Guard.objects.all()
    return render(request, 'guards.html', {'guards': all_guards})

def guard_detail(request, pk):
    guard = get_object_or_404(Guard, pk=pk)
    return render(request, 'guard_details.html', {'guard': guard})

def contact(request):
    return render(request, 'contact.html')

from django.shortcuts import render
from .models import Guard

def guard_list(request):
    corporate_guards = Guard.objects.filter(category="Corporate")[:3]  # show only 3
    residential_guards = Guard.objects.filter(category="Residential")[:3]
    event_guards = Guard.objects.filter(category="Event")[:3]

    context = {
        "corporate_guards": corporate_guards,
        "residential_guards": residential_guards,
        "event_guards": event_guards,
    }
    return render(request, "guards/guards_preview.html", context)


def guard_category(request, category):
    guards = Guard.objects.filter(category=category)
    return render(request, "guards/guards_category.html", {"guards": guards, "category": category})

def signup_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password != confirm_password:
            messages.error(request, "Passwords do not match!")
            return redirect('signup')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists!")
            return redirect('signup')

        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()
        messages.success(request, "Account created successfully! Please log in.")
        return redirect('login')
    return render(request, 'signup.html')


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome back, {username}!")
            return redirect('/')  # redirect to home
        else:
            messages.error(request, "Invalid username or password")
            return redirect('login')
    return render(request, 'login.html')


def logout_view(request):
    logout(request)
    messages.info(request, "You have logged out successfully.")
    return redirect('login')
