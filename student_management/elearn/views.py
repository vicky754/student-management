from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import TemplateView
from django.contrib import auth
from django.contrib.auth import authenticate
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth import logout
from django.urls import reverse_lazy
from django.views import generic
#from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic import ListView, DetailView 
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.http import HttpResponse, Http404
#from .models import Customer, Profile
from .forms import *
from django.http import HttpResponseRedirect, HttpResponse
from django.template import loader
from django.urls import reverse
from django.utils import timezone
from django.core import serializers
from django.conf import settings
import os
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib import auth
from datetime import datetime, date
from django.core.exceptions import ValidationError
from . import models
import operator
import itertools
from django.db.models import Avg, Count, Sum
from django.forms import inlineformset_factory
from .models import *
from django.db import transaction
from django.contrib.auth.hashers import make_password
from django.core.files.storage import FileSystemStorage
from django.contrib.auth.forms import (AuthenticationForm, UserCreationForm,
                                       PasswordChangeForm)

from django.contrib.auth import update_session_auth_hash                                       


from bootstrap_modal_forms.generic import (
    BSModalLoginView,
    BSModalFormView,
    BSModalCreateView,
    BSModalUpdateView,
    BSModalReadView,
    BSModalDeleteView
)




# Shared Views

def home(request):
	return render(request, 'home.html')




@login_required
def logoutView(request):
	logout(request)
	return redirect('login_form')


def login_form(request):
    return render(request, 'login.html')





def loginView(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        user = authenticate(request, email=email, password=password)

        if user is not None and user.is_active:
            request.session['userId']=user.id
            request.session['email']=email
            login(request,user)

            auth.login(request, user)
            if user.is_admin or user.is_superuser:
                return redirect('dashboard')
                
            elif user.is_instructor:
                return redirect('instructor')
            elif user.is_learner:
                return redirect('learner')
            else:
                return redirect('login_form')
        else:
            messages.info(request, "Invalid Uname or Pass")
            return redirect('login_form')




# Admin Views
@login_required
def dashboard(request):
    learner = User.objects.filter(is_learner=True).count()
    instructor = User.objects.filter(is_instructor=True).count()
    users = User.objects.all().count()
    context = {'learner':learner, 'instructor':instructor, 'users':users}

    return render(request, 'dashboard/admin/home.html', context)


class InstructorSignUpView(LoginRequiredMixin,CreateView):
    model = User
    form_class = InstructorSignUpForm
    template_name = 'dashboard/admin/signup_form.html'

    def get_context_data(self, **kwargs):
        kwargs['user_type'] = 'instructor'
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        user = form.save()
        messages.success(self.request, 'Instructor Was Added Successfully')
        return redirect('isign')

class AdminLearner(LoginRequiredMixin,CreateView):
    model = User
    form_class = LearnerSignUpForm
    template_name = 'dashboard/admin/learner_signup_form.html'

    def get_context_data(self, **kwargs):
        kwargs['user_type'] = 'learner'
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        user = form.save()
        messages.success(self.request, 'Learner Was Added Successfully')
        return redirect('addlearner')

@login_required
def create_user_form(request):
    return render(request, 'dashboard/admin/add_user.html')


@login_required
def create_user(request):
    if request.method == 'POST':
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password = make_password(password)

        a = User(first_name=first_name, last_name=last_name, username=username, password=password, email=email, is_admin=True)
        a.save()
        messages.success(request, 'Admin Was Created Successfully')
        return redirect('aluser')
    else:
        messages.error(request, 'Admin Was Not Created Successfully')
        return redirect('create_user_form')



@login_required
def acreate_profile(request):
    if request.method == 'POST':
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        email=request.POST['email']
        birth_date = request.POST['birth_date']
        phonenumber = request.POST['phonenumber']
        avatar = request.FILES['avatar']
        current_user = request.user
        user_id = current_user.id
        print(user_id)

        Profile.objects.filter(id = user_id).create(user_id=user_id,phonenumber=phonenumber, first_name=first_name, last_name=last_name,email=email,birth_date=birth_date, avatar=avatar)
        messages.success(request, 'Your Profile Was Created Successfully')
        return redirect('auser_profile')
    else:
        current_user = request.user
        user_id = current_user.id
        users = Profile.objects.filter(user_id = user_id)
        users = {'users': users}
        return render(request, 'dashboard/admin/create_profile.html', users)     


@login_required
def auser_profile(request):
    current_user = request.user
    user_id = current_user.id
    users = Profile.objects.filter(user_id = user_id)
    users = {'users': users}
    return render(request, 'dashboard/admin/user_profile.html', users)   

class ListUserView(LoginRequiredMixin, ListView):
    model = User
    template_name = 'dashboard/admin/list_users.html'
    context_object_name = 'users'
    paginated_by = 10


    def get_queryset(self):
        return User.objects.order_by('-id')

class ADeleteuser(SuccessMessageMixin, DeleteView):
    model = User
    template_name = 'dashboard/admin/confirm_delete2.html'
    success_url = reverse_lazy('aluser')
    success_message = "User Was Deleted Successfully"





# Teachers Views
@login_required
def home_instructor(request):
    learner = User.objects.filter(is_learner=True).count()
    instructor = User.objects.filter(is_instructor=True).count()
    users = User.objects.all().count()
    context = {'learner':learner,'instructor':instructor, 'users':users}

    return render(request, 'dashboard/instructor/home.html', context)

@login_required
def user_profile(request):
    current_user = request.user
    user_id = current_user.id
    #print(user_id)
    users = Profile.objects.filter(user_id=user_id)
    users = {'users':users}
    return render(request, 'dashboard/instructor/user_profile.html', users)

@login_required
def create_profile(request):
    if request.method == 'POST':
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        email=request.POST['email']
        phonenumber = request.POST['phonenumber']
        birth_date = request.POST['birth_date']
        avatar = request.FILES['avatar']
        current_user = request.user
        user_id = current_user.id
        print(user_id)

        Profile.objects.filter(id = user_id).create(user_id=user_id,first_name=first_name, last_name=last_name,email=email, phonenumber=phonenumber, birth_date=birth_date, avatar=avatar)
        messages.success(request, 'Profile was created successfully')
        return redirect('user_profile')
    else:
        current_user = request.user
        user_id = current_user.id
        print(user_id)
        users = Profile.objects.filter(user_id=user_id)
        users = {'users':users}
        return render(request, 'dashboard/instructor/create_profile.html', users)




# Learner Views
@login_required
def home_learner(request):
    learner = User.objects.filter(is_learner=True).count()
    instructor = User.objects.filter(is_instructor=True).count()
    users = User.objects.all().count()

    context = {'learner':learner,'instructor':instructor, 'users':users}

    return render(request, 'dashboard/learner/home.html', context)


    
class LearnerSignUpView(LoginRequiredMixin,CreateView):
    model = User
    form_class = LearnerSignUpForm
    template_name = 'signup_form.html'

    def get_context_data(self, **kwargs):
        kwargs['user_type'] = 'learner'
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        #return redirect('learner')
        return redirect('home')



@login_required
def luser_profile(request):
    current_user = request.user
    user_id = current_user.id
    #print(user_id)
    users = Profile.objects.filter(user_id=user_id)
    users = {'users':users}
    return render(request, 'dashboard/learner/user_profile.html', users)



@login_required
def lcreate_profile(request):
    if request.method == 'POST':
        
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        email = request.POST['email']
        phonenumber = request.POST['phonenumber']
        birth_date = request.POST['birth_date']
        avatar = request.FILES['avatar']
        current_user = request.user
        user_id = current_user.id
        print(user_id)

        Profile.objects.filter(id = user_id).create(user_id=user_id ,first_name=first_name, last_name=last_name,email=email, phonenumber=phonenumber,birth_date=birth_date, avatar=avatar)
        messages.success(request, 'Profile was created successfully')
        return redirect('luser_profile')
    else:
        current_user = request.user
        user_id = current_user.id
        print(user_id)
        users = Profile.objects.filter(user_id=user_id)
        users = {'users':users}
        return render(request, 'dashboard/learner/create_profile.html', users)

@login_required
def lcreate_photo(request):
    if request.method == 'POST':
        #first_name = request.POST['first_name']
        user=(request.session.get('userId'))
        avatar = request.FILES.getlist('avatar')
        current_user = request.user
        print(current_user)
        user_id = current_user.id
        print(user_id)
        for avatars in avatar:
            Photo.objects.filter(id = user_id).create(user_id=user_id, user=User(id=user) ,avatar=avatars)
            messages.success(request, 'Photo was created successfully')
        return redirect('luser_photo')
    else:
        current_user = request.user
        user_id = current_user.id
        print(user_id)
        users = Photo.objects.filter(user_id=user_id)
        users = {'users':users}
        return render(request, 'dashboard/learner/create_photo.html', users)




@login_required
def luser_photo(request):
    uid=request.session.get('userId')
    current_user = request.user
    user_id = current_user.id
    #print(user_id)
    users = Photo.objects.filter(user_id=uid)
    users = {'users':users}
    return render(request, 'dashboard/learner/user_photo.html', users)



@login_required
def lcreate_tphoto(request):
    if request.method == 'POST':
        #first_name = request.POST['first_name']
        user=(request.session.get('userId'))
        avatar = request.FILES.getlist('avatar')
        current_user = request.user
        user_id = current_user.id
        print(user_id)
        for avatars in avatar:
            Tphoto.objects.filter(id = user_id).create(user_id=user_id, user=User(id=user) ,avatar=avatars)
            messages.success(request, 'Photo was created successfully')
        return redirect('luser_tphoto')
    else:
        current_user = request.user
        user_id = current_user.id
        print(user_id)
        users = Tphoto.objects.filter(user_id=user_id)
        users = {'users':users}
        return render(request, 'dashboard/instructor/create_tphoto.html', users)




@login_required
def luser_tphoto(request):
    uid=request.session.get('userId')
    current_user = request.user
    user_id = current_user.id
    #print(user_id)
    users = Tphoto.objects.filter(user_id=uid)
    users = {'users':users}
    return render(request, 'dashboard/instructor/user_tphoto.html', users)



# def studentimages(request):
   
#     if request.method == 'POST':
#         form = ImageForm(request.POST,request.FILES)
#         if form.is_valid():
#             form.save()
#     form = ImageForm()

#     return render(request,'dashboard/learner/studentimages.html',{'form':form})

