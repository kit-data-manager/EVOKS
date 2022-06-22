from django.contrib.auth import authenticate, login, logout
from django.http.request import HttpRequest
from django.http.response import HttpResponseBadRequest
from django.shortcuts import render
from .forms import LoginForm, SignupForm, SetPasswordForm
from django.http import HttpResponse
from django.shortcuts import redirect
from django.contrib.auth.models import User
from django.core.mail import send_mail
from evoks.settings import EMAIL_HOST_USER
import django.contrib.auth.views
from django.contrib.auth.models import User
from django.contrib import admin
from django.urls import reverse


class PasswordResetView(django.contrib.auth.views.PasswordResetView):

    email_template_name = 'password_reset_email/password_res_email.html'


class PasswordResetConfirmView(django.contrib.auth.views.PasswordResetConfirmView):

    form_class = SetPasswordForm


def login_view(request: HttpRequest) -> HttpResponse:
    """The login page

    Args:
        request (HttpRequest): The request

    Returns:
        A rendered page
    """
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = LoginForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(username=email, password=password)
            if user is not None and user.is_active:
                login(request, user)
                # redirect to homepage/dashboard
                return redirect('base')

            return HttpResponse('Unauthorized', status=401)

    form = LoginForm()
    return render(request, 'login.html', {'form': form})


def signup_view(request: HttpRequest) -> HttpResponse:
    """The signup page

    Args:
        request (HttpRequest): The request

    Returns:
        A rendered page
    """
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = SignupForm(request.POST)
        # check whether it's valid:
        if form.is_valid():

            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            if User.objects.filter(username=email).exists():
                return HttpResponseBadRequest('An account with the given email already exists', status=400)

            if not 'tos' in request.POST:
                return HttpResponseBadRequest('You have to accept the ToS if you want to create an account', status=400)

            user = User.objects.create_user(username=email,
                                            email=email)
            user.set_password(password)

            # safe full name in corresponding profile
            user.profile.name = name
            user.save()

            # get all emails from superusers
            superusers = User.objects.filter(
                is_superuser=True).values_list('email')
            emails = []

            for su in superusers:
                if su[0] != '':
                    emails.append(su[0])

            # build url to profile in admin panel
            url = request.build_absolute_uri(reverse("admin:%s_%s_change" % (
                user.profile._meta.app_label, user.profile._meta.model_name), args=(user.profile.id,)))

            # send_mail(
            #     'Verify a new Evoks account',
            #     'Please visit the evoks admin panel {0} and verify the new user'.format(
            #         url),
            #     EMAIL_HOST_USER,
            #     emails,
            #     fail_silently=False,
            # )

            return HttpResponse('Your account will be usable as soon as an admin verifies it!')

    else:
        form = SignupForm()

    return render(request, 'signup.html', {'form': form})


def logout_view(request: HttpRequest):
    logout(request)
    return redirect('login')
