from django.contrib.auth import authenticate, login
from django.http.request import HttpRequest
from django.shortcuts import render
from .forms import LoginForm, SignupForm
from django.http import HttpResponse
from django.shortcuts import redirect
from django.contrib.auth.models import User
from django.core.mail import EmailMessage, message, send_mass_mail


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
            if user is not None:
                if user.is_active:
                    login(request, user)
                    # redirect to homepage/dashboard
                    return redirect('dashboard')

            return HttpResponse('Unauthorized', status=401)

    else:
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

            user = User.objects.create_user(username=email,
                                            email=email)
            user.set_password(password)

            # safe full name in corresponding profile
            user.profile.fullname = name
            user.save()

            # email setup
            #mail_subject = 'Verify User Account'
            #current_site = get_current_site(request)
            #uid = urlsafe_base64_encode(force_bytes(user.pk))
            #token = account_verification_token.make_token(user)
            #verification_link = '{0}/?uid={1}&token{2}'.format(current_site, uid, token)
            # add admin name?
            #message = 'Hello,\n A User with email {0} requests an account verification.\n click the following link to activate his account: {1}'.format(user.email, verification_link)
            #admin_list = list(User.objects.filter(is_staff=True))
            # missing from email
            #to_email = 'bonzjojo0@gmail.com'
            #email = EmailMessage(mail_subject, message, to_email)
            # email.send()
            #send_mass_mail(mail_subject, message, admin_list)

            return HttpResponse('Your account will be usable as soon as an admin has verified it!')

    else:
        form = SignupForm()

    return render(request, 'signup.html', {'form': form})

# def VerificationView(View):
    # def get(self, request, uidb64, token):
    # try:
    #uid = force_text(urlsafe_base64_decode(uidb64).decode())
    #user = User.objects(pk=uid)
    # except(TypeError, ValueError, OverflowError, User.DoesNotExist):
    #user = None
    # if user is not None and account_verification_token.check_token(user, token):
    # user.profile.verify()
    # user.save()
    # else:
    # return HttpResponse('Invalid Verification Link!')
