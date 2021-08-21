from django.shortcuts import render
from django.shortcuts import redirect
from django.http import HttpResponse
from guardian.shortcuts import assign_perm, remove_perm, get_perms
from evoks.fuseki import fuseki_dev
from evoks.settings import SKOSMOS_LIVE_URI, SKOSMOS_DEV_URI
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
                #deletes the session user
                # sets a random group owner in groups where session user is the owner. deletes groups where groupowner is only member
                for group in user.groups.all():
                    if group.groupprofile.group_owner == user:
                        if group.groupprofile.size>1:
                            group.groupprofile.remove_user(user)
                            group.groupprofile.group_owner=group.user_set.first()
                            group.save()
                        else:
                            group.delete()
                # sets a random user voc owner where session user is only owner. deletes vocabularies where session user is only member        
                for voc in user.profile.vocabulary_set.all():
                    voc.profiles.remove(user.profile)
                    if voc.profiles.all().count()==0 and voc.groups.all().count()==0:
                        if voc.state == 'Review':
                            skosmos_dev.delete_vocabulary(voc.name)
                        fuseki_dev.delete_vocabulary(voc)
                        voc.delete()         
                    else:
                        hasowner=False
                        hasgroup=False
                        for mem in voc.profiles.all():
                            if 'owner' in get_perms(mem.user, voc):
                                hasowner=True
                            else:
                                pass    

                        for group in voc.groups.all():
                                if 'owner' in get_perms(group.group, voc):
                                    hasgroup=True
                                else:
                                    pass 

                        if not hasowner and not hasgroup:
                            if voc.profiles.all().count()==0:
                                assign_perm('owner', voc.groups.first().group, voc)
                            else:                              
                                assign_perm('owner', voc.profiles.first().user, voc)
                #try:
                user.delete()
                #except:
                #    return HttpResponse('Deletion failed')
                return redirect('/login')

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
