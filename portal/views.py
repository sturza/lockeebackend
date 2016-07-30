from django.views.decorators.csrf import csrf_exempt
from django.views.generic.list import ListView
from random import choice
from string import ascii_uppercase
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import View
from forms import UserReg, UserLogin, AddLock, VerifyAndro, LockSecret
from django.contrib.auth.mixins import LoginRequiredMixin
from portal.models import Lock
from portal.forms import AndroLogin, AndroRegister


class Register(View):
    """This view handles the register requests on the web page."""
    form_class = UserReg
    template_name = 'portal/registration_form.html'

    def get(self, request):
        """This function displays the form for user registration."""
        form = self.form_class(None)
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        """This function submits the form for DB processing and logs in the user if successful."""
        form = self.form_class(request.POST)

        if form.is_valid():
            new_user = form.save(commit=False)
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            full_name = form.cleaned_data['full_name']
            new_user.set_password(password)
            new_user.first_name = full_name
            new_user.save()

            user = authenticate(username=username, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return redirect('portal:my-locks')

        return render(request, self.template_name, {'form': form})


class Login(View):
    """This view handles the login requests on the web page."""
    form_class = UserLogin
    template_name = 'portal/login_form.html'

    def get(self, request):
        """This function displays the form for user login."""
        if self.request.user.is_authenticated():
            return redirect('portal:my-locks')
        else:
            form = self.form_class(None)
            return render(request, self.template_name, {'form': form})

    def post(self, request):
        """This function submits the form for DB processing and logs in the user if succesful."""
        form = self.form_class(request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return redirect('portal:my-locks')

        return render(request, self.template_name, {'form': form})


class Display_My_Locks(LoginRequiredMixin, ListView):
    """This view displays the locks of the user."""
    login_url = 'portal:login'
    redirect_field_name = 'redirect_to'
    template_name = 'portal/my-locks.html'

    def get_queryset(self):
        return Lock.objects.filter(owner='qwerty@gmail.com')


@login_required(login_url='portal:login')
def log_out(request):
    """This view logs the user out."""
    logout(request)
    return render(request, 'portal/logout.html', {})


class Add_Lock(LoginRequiredMixin, View):
    """This view processes the user request for the ownership of a lock."""
    login_url = 'portal:login'
    redirect_field_name = 'redirect_to'
    form_class = AddLock
    template_name = 'portal/add-lock-form.html'

    def get(self, request):
        """This function displays the form for adding a new lock."""
        form = self.form_class(None)
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        """This function submits the form for DB processing."""
        error = ''
        form = self.form_class(request.POST)

        if form.is_valid():
            lock_id = form.cleaned_data['lock_id']
            nickname = form.cleaned_data['nickname']
            exists = get_object_or_404(Lock, lock_inner_id=lock_id)
            if exists.is_available:
                exists.is_available = False
                exists.owner = request.user.get_username()
                exists.nickname = nickname
                exists.save()
                return redirect('portal:my-locks')
            else:
                error = 'Lock already in use'

        return render(request, self.template_name, {'form': form, 'error': error})


@login_required(login_url='portal:login')
def share(request, lock_inner_id):
    """This view redirects the user to the share menu of a lock."""
    what_lock = Lock.objects.get(lock_inner_id=str(lock_inner_id))
    return render(request, 'portal/share.html', {'what_lock': what_lock})


@login_required(login_url='portal:login')
def generate_code(request, lock_inner_id):
    """This view generates a new share code at user's demand.
    """
    lock_to_change = Lock.objects.get(lock_inner_id=str(lock_inner_id))
    lock_to_change.share_id = ''.join(choice(ascii_uppercase) for i in range(12))
    lock_to_change.save()
    return redirect('portal:share lock_to_change.lock_inner_id')


@csrf_exempt
def andro_login(request):
    """This view handles the login requests that come from the android terminal."""
    if request.method == 'POST':
        form = AndroLogin(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user is not None:
                return HttpResponse('login success')
            else:
                return HttpResponse('fail')
        else:
            return HttpResponse('wow')  #LEL
    else:
        return HttpResponse('<title> Error </title> <body> <h1> Forbidden </h1> <p> Now that was silly ^_^ </p> </body>')


@csrf_exempt
def andro_register(request):
    """This view handles the register requests that come from the an android terminal."""
    if request.method == 'POST':
        form = AndroRegister(request.POST)
        if form.is_valid():
            new_user = form.save(commit=False)
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            full_name = form.cleaned_data['name']
            new_user.set_password(password)
            new_user.first_name = full_name
            new_user.save()
            return HttpResponse('register success')
        else:
            return HttpResponse('wow')
    else:
        return HttpResponse(
            '<title> Error </title> <body> <h1> Forbidden </h1> <p> Now that was silly ^_^ </p> </body>')


@csrf_exempt
def andro_verify(request):
    if request.method == 'POST':
        form = VerifyAndro(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            try:
                used_username_check = User.objects.get(username=username)
                return HttpResponse('email already taken')
            except User.DoesNotExist:
                return HttpResponse('verify success')
        else:
            return HttpResponse('wow')
    else:
        return HttpResponse(
            '<title> Error </title> <body> <h1> Forbidden </h1> <p> Now that was silly ^_^ </p> </body>')


def profile(request):
    """This view handles the user's profile on the web site."""
    return render(request, 'portal/profile.html', {'user': request.user})


def about(request):
    """This view presents the details of this project's godlike developers."""
    return render(request, 'portal/about.html', {})


@csrf_exempt
def lock_query(request, what_user):
    """This view sends to the android terminal the locks the user has access to."""
    if request.method == 'POST':
        form = LockSecret(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            secret_key = form.cleaned_data['secret']
            if secret_key == 'bibg#eL483%9vHoEOn8y(J%e':  # NASA is jelly
                user_locks = Lock.object.get(owner=username)
                response = ''   #lock1 safas asdha 0/1 #lock2 asdkas asada 0/1
                contor = 0
                for x in user_locks:
                    contor += 1
                    response += ('#lock' + str(contor) + ' ')
                    response += (str(x.nickname) + ' ')
                    response += (str(x.share_id) + ' ')
                    response += (str(x.is_opened) + ' ')
                return HttpResponse(response)
            else:
                return HttpResponse('why u hack')
        else:
            return HttpResponse('fail')
    else:
        return HttpResponse(
            '<title> Error </title> <body> <h1> Forbidden </h1> <p> Now that was silly ^_^ </p> </body>')


def portal_mechanic(request, lock_inner_id):
    """This view opens/closes a lock via the website."""
    what_lock = Lock.objects.get(lock_inner_id=str(lock_inner_id))
    if what_lock.is_opened:
        what_lock.is_opened = False
        what_lock.save()
    else:
        what_lock.is_opened = True
        what_lock.save()
    return render(request, 'portal/mechanic.html', {'is_opened': what_lock.is_opened})


@csrf_exempt
def android_mechanic(request, lock_inner_id):
    """This view opens/closes a lock via an android terminal."""
    pass


def arduino_register_lock(request, what_lock):
    """This view registers a lock as available in the database - the url is called by arduino automatically."""
    try:
        lock = Lock.objects.get(lock_inner_id=what_lock)
        return HttpResponse('already added')
    except Lock.DoesNotExist:
        lock = Lock()
        lock.lock_inner_id = what_lock
        lock.save()
    return HttpResponse('lock success')


def arduino_mechanic(request, what_lock):
    """This view sends the open/close signal to the arduino-lock."""
    url = 'http://arduinosomething.co/%s' % what_lock
    lock = Lock.objects.get(lock_inner_id=what_lock)
    if lock.is_opened:
        payload = {'action': 'close'}
    else:
        payload = {'action': 'open'}
    response = request.post(url, params=payload)
    return redirect('portal:my-locks')


