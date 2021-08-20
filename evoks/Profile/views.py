from django.shortcuts import render
from django.shortcuts import redirect
from django.http import HttpResponse
from django.contrib.auth.forms import PasswordResetForm
from django.http.request import HttpRequest
from evoks.settings import EMAIL_HOST_USER


def profile_view(request):

    if request.user.is_authenticated:

        user = request.user

        if request.method == 'POST':

            if 'save' in request.POST:
                # changes content of name and description
                name = request.POST.get('name')
                description = request.POST.get('about')
                user.profile.name = name
                user.profile.description = description
                user.save()
            elif 'change-password' in request.POST:
                # changes password
                form = PasswordResetForm({'email': user.email})
                if form.is_valid():
                    form.save(
                        request=request,
                        use_https=False, # reverse proxy should redirect http to https automatically (ONLY ON PORT 80)
                        from_email=EMAIL_HOST_USER,
                        email_template_name='password_reset_email/password_res_email.html')

            elif 'delete' in request.POST:
                # deletes the session user
                try:
                    user.delete()
                except:
                    return HttpResponse('Your account may be Owner of a Group')

            elif 'data' in request.POST:
                # exports the userdata
                user.profile.export_data()

        return render(request=request,
                      template_name="profile.html",
                      context={
                          'profile': user.profile
                      })

    return redirect('/login')
    # redirect to login page if user is not authenticated
