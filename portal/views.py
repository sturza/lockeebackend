from django.core.urlresolvers import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.list import ListView
from random import choice
from string import ascii_uppercase
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views.generic import View
from forms import UserReg, UserLogin, AddLock, VerifyAndro, LockSecret, AndroidOpenLock
from django.contrib.auth.mixins import LoginRequiredMixin
from portal.models import Owner, LockAbsVal, Lock
from portal.forms import AndroLogin, AndroRegister

# SERVER SIDE ####


class Register(View):
    """This view handles the register requests on the web page."""
    form_class = UserReg
    template_name = 'portal/registration-form.html'

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
            name = form.cleaned_data['first_name']
            new_user.username = username
            new_user.set_password(password)
            new_user.first_name = name
            new_user.save()
            new_owner = Owner(owner=new_user)
            new_owner.save()
            user = authenticate(username=username, password=password)
            login(request, user)
            return redirect('portal:my-locks')

        return render(request, self.template_name, {'form': form})


class Login(View):
    """This view handles the login requests on the web page."""
    form_class = UserLogin
    template_name = 'portal/login-form.html'

    def get(self, request):
        """This function displays the form for user login."""
        if request.user.is_authenticated():
            return redirect('portal:my-locks')
        else:
            form = self.form_class(None)
            return render(request, self.template_name, {'form': form})

    def post(self, request):
        """This function submits the form for DB processing and logs in the user if successful."""
        form = self.form_class(request.POST)
        error = ''

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return redirect('portal:my-locks')
                else:
                    error = 'User is inactive'
            else:
                error = 'Invalid username or password'

        return render(request, self.template_name, {'form': form, 'error': error})


class Display_My_Locks(LoginRequiredMixin, ListView):
    """This view displays the locks of the logged in user."""
    login_url = 'portal:login'
    redirect_field_name = 'redirect_to'
    template_name = 'portal/my-locks.html'

    def get_queryset(self):
        locks_of_logged_in_user = Owner.objects.get(owner=self.request.user)
        return locks_of_logged_in_user.locks.all()


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
        form = self.form_class(request.POST)

        if form.is_valid():
            lock_id = form.cleaned_data['lock_id']
            new_lock_nickname = form.cleaned_data['nickname']
            owner = Owner.objects.get(owner=request.user)
            absolute_lock = LockAbsVal.objects.get(lock_inner_id=lock_id)
            try:
                owner.locks.get(abs_lock=absolute_lock)
                return render(request, self.template_name, {'form': form, 'error': 'Lock already added'})
            except Lock.DoesNotExist:
                new_relative_lock = Lock()
                new_relative_lock.nickname = new_lock_nickname
                new_relative_lock.abs_lock = absolute_lock
                new_relative_lock.save()
                owner.locks.add(new_relative_lock)
                owner.save()
                return redirect('portal:my-locks')
        else:
            return HttpResponse('Form error')


@login_required(login_url='portal:login')
def log_out(request):
    """This view logs the user out."""
    logout(request)
    return render(request, 'portal/logout.html', {})


@login_required(login_url='portal:login')
def share(request, lock_nickname):
    """This view redirects the user to the share menu of a lock."""
    logged_in_owner = Owner.objects.get(owner=request.user)
    lock_to_be_shared = logged_in_owner.locks.get(nickname=lock_nickname)
    return render(request, 'portal/share.html', {'what_lock': lock_to_be_shared})


@login_required(login_url='portal:login')
def generate_code(request, lock_nickname):
    """This view generates a new share code at user's demand."""
    logged_in_owner = Owner.objects.get(owner=request.user)
    lock_to_change = logged_in_owner.locks.get(nickname=lock_nickname)
    lock_to_change.share_id = ''
    for i in range(0, 11):
        lock_to_change.share_id += choice(ascii_uppercase)
    lock_to_change.save()
    logged_in_owner.save()
    return redirect(reverse('portal:share', kwargs={'lock_nickname': lock_to_change.nickname}))


@login_required(login_url='portal:login')
def profile(request):
    """This view handles the user's profile on the web site."""
    return render(request, 'portal/profile.html', {'name': request.user.first_name})


def about(request):
    """This view presents the details of this project's godlike developers."""
    return render(request, 'portal/about.html', {})


@login_required(login_url='portal:login')
def portal_mechanic(request, lock_inner_id):
    """This view opens/closes a lock via the website."""
    what_lock = LockAbsVal.objects.get(lock_inner_id=lock_inner_id)
    arduino_url = str(what_lock.ip_address)
    if what_lock.is_opened:
        payload = {'action': 'close'}
        what_lock.is_opened = False
        what_lock.save()
    else:
        payload = {'action': 'open'}
        what_lock.is_opened = True
        what_lock.save()
    response = request.post(arduino_url, params=payload)
    if response == 'ok':
        return render(request, 'portal/my-locks.html', {})
    else:
        return render(request, 'portal/error.html',
                      {'title': 'Connection error', 'message': "The arduino can't be reached"})


# ANDROID SIDE ###


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
            return HttpResponse('Form Error')
    else:
        return render(request, 'portal/error.html',
                      {'title': 'Forbidden', 'message': 'You are not supposed to be here ^_^'})


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
            new_user.username = username
            new_user.set_password(password)
            new_user.first_name = full_name
            new_user.save()
            create_owner = Owner(owner=new_user.username)
            create_owner.save()
            return HttpResponse('register success')
        else:
            return HttpResponse('wow')
    else:
        return render(request, 'portal/error.html',
                      {'title': 'Forbidden', 'message': 'You are not supposed to be here ^_^'})


@csrf_exempt
def andro_verify(request):
    """This view helps the android terminal check username availability in real time."""
    if request.method == 'POST':
        form = VerifyAndro(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            try:
                User.objects.get(username=username)
                return HttpResponse('email already taken')
            except User.DoesNotExist:
                return HttpResponse('verify success')
        else:
            return HttpResponse('wow')
    else:
        return render(request, 'portal/error.html',
                      {'title': 'Forbidden', 'message': 'You are not supposed to be here ^_^'})


@csrf_exempt
def android_mechanic(request):
    """This view opens/closes a lock via an android terminal."""
    if request.method == 'POST':
        form = AndroidOpenLock(request.POST)
        if form.is_valid():
            what_owner = form.cleaned_data['username']
            what_lock_id = form.cleaned_data['lock_id']
            what_owner = Owner.objects.get(owner=what_owner)
            what_lock = what_owner.locks.get(lock_inner_id=what_lock_id)
            arduino_url = str(what_lock.ip_address)
            if what_lock.is_opened:
                payload = {'action': 'close'}
                what_lock.is_opened = False
                what_lock.save()
            else:
                payload = {'action': 'open'}
                what_lock.is_opened = True
                what_lock.save()
            response = request.post(arduino_url, params=payload)
            if response == 'ok':
                return HttpResponse('ok')
            else:
                return HttpResponse("arduino can't be reached")
        else:
            return HttpResponse('form error')
    else:
        return render(request, 'portal/error.html',
                      {'title': 'Forbidden', 'message': 'You are not supposed to be here ^_^'})


@csrf_exempt
def android_locks_query(request):
    """This view sends to the android terminal the locks the user has access to."""
    if request.method == 'POST':
        form = LockSecret(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            secret_key = form.cleaned_data['secret']
            if secret_key == 'bibg#eL483%9vHoEOn8y(J%e':  # NASA is jelly
                owner = Owner.objects.get(owner=username)
                user_locks = owner.objects.all()
                response = ''
                lock_cardinal = 0
                for x in user_locks:
                    lock_cardinal += 1
                    response += ('#lock' + str(lock_cardinal) + ' ')
                    response += (str(x.nickname) + ' ')
                    response += (str(x.share_id) + ' ')
                    response += (str(x.is_opened) + ' ')
                return HttpResponse(response)
            else:
                return HttpResponse('why u hack')
        else:
            return HttpResponse('form error')
    else:
        return HttpResponse(
            '<title> Error </title> <body> <h1> Forbidden </h1> <p> Now that was silly ^_^ </p> </body>')


# ARDUINO SIDE


def arduino_register_lock(lock_inner_id, lock_ip):
    """This view registers/updates locks at the lock's(the arduino) request"""
    try:
        already_registered_lock = LockAbsVal.objects.get(lock_inner_id=lock_inner_id)
        already_registered_lock.ip_address = lock_ip
        already_registered_lock.save()
        return HttpResponse('lock_ip updated')
    except LockAbsVal.DoesNotExist:
        new_registration_lock = LockAbsVal(lock_inner_id=lock_inner_id, ip_address=lock_ip)
        new_registration_lock.save()
        return HttpResponse('new lock registered')

