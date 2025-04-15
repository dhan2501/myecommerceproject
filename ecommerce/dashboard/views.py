from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User, Group
# from .models import Customer, Subscriber

from .forms import ChangePasswordForm


def dashboard_home(request):
    return render(request, 'dashboard/home.html')



def change_password(request, user_id):
    user = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        form = ChangePasswordForm(request.POST)
        if form.is_valid():
            new_password = form.cleaned_data['new_password']
            user.set_password(new_password)
            user.save()
            messages.success(request, f"Password for {user.username} changed successfully!")
            return redirect('dashboard:user_list') 
    else: 
        form = ChangePasswordForm()

    return render(request, 'dashboard/change_password.html', {'form': form, 'user': user})

def dashboard_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard:user_list')
        else:
            messages.error(request, 'Invalid credentials.')
    return render(request, 'dashboard/login.html')

def dashboard_logout(request):
    logout(request)
    return redirect('dashboard:dashboard_login')

@login_required
def dashboard_home(request):
    return render(request, 'dashboard/home.html')


@login_required
def user_list(request):
    # Superadmins
    superadmins = User.objects.filter(is_superuser=True)

    # Customers (assigned to 'Customer' group)
    customers = User.objects.filter(groups__name='Customer')

    # Subscribers (assigned to 'Subscriber' group)
    subscribers = User.objects.filter(groups__name='Subscriber')

    context = {
        'superadmins': superadmins,
        'customers': customers,
        'subscribers': subscribers,
    }
    return render(request, 'dashboard/users.html', context)

# @login_required
# def user_list(request):
#     return render(request, 'dashboard/users.html')

# def user_list_view(request):
#     superadmins = User.objects.filter(is_superuser=True)
#     customers = Customer.objects.all()
#     subscribers = Subscriber.objects.all()

#     return render(request, 'your_template.html', {
#         'superadmins': superadmins,
#         'customers': customers,
#         'subscribers': subscribers,
#     })

@login_required
def reports(request):
    return render(request, 'dashboard/reports.html')
