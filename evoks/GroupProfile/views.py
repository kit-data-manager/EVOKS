from django.shortcuts import render, redirect
from django.contrib.auth.models import Group
from django.contrib.auth.models import User
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import HttpResponse

def teams_view(request):
    if request.user.is_authenticated:
        user = request.user
        teams = user.groups.all()
        pagesize=10
        paginator = Paginator(teams, pagesize)
        page = request.POST.get('page')
        #tests if page number is within the range
        try:        
            posts = paginator.page(page) 
        except PageNotAnInteger: 
            posts = paginator.page(1) 
        except EmptyPage:
             posts = paginator.page(paginator.num_pages) 

        return render(request=request,
                      template_name="teams.html",
                      context={'teams':teams,'member':user, 'page_obj':posts})


    return redirect('/login')
    # redirect to login page if user is not authenticated

def team_detail_view(request, name):
    if 'create-team' in request.POST:
        #creates a team with the content of team-name
        name = request.POST.get('team-name')
        if Group.objects.filter(name=name).exists():
            return HttpResponse('already exists')
        else:           
            group=Group.objects.create(name=name)
            group.groupprofile.group_owner=request.user
            group.save()
            group.groupprofile.add_user(request.user) 
            return redirect('/teams/'+name)

    if request.user.is_authenticated:
        user = request.user
        team = Group.objects.get(name=name) 
        if user in team.user_set.all():      
            pagesize=2
            member_all = team.user_set.all()
            member = Paginator(member_all,pagesize)
            page = request.POST.get("page") 
            #tests if page number is within the range
            try:        
                posts = member.page(page) 
            except PageNotAnInteger: 
                posts = member.page(1) 
            except EmptyPage: 
                posts = member.page(member.num_pages) 
            
            if request.method == 'POST':
                if  'save' in request.POST:
                    #changes description of the team. can be accessed by every memeber of the team
                    team.groupprofile.description = request.POST.get('description')
                    team.save()

                elif  'invite' in request.POST:
                    #invites the user with given email. can only be accessed from the owner and gives error if user not exists 
                    if team.groupprofile.group_owner==user: 
                        if User.objects.filter(email=request.POST.get('email')).exists():
                            new_member=User.objects.get(email=request.POST.get('email'))
                            team.groupprofile.add_user(new_member)
                            return redirect('/teams/'+name)
                        else:
                            return HttpResponse('error: does not exist') 
                    else: 
                        return HttpResponse('insufficient permission') 

                elif 'kick_all' in request.POST: 
                    #removes all not-Owner from the group. can only be accessed from the owner
                    if team.groupprofile.group_owner==user: 
                        for mem in member_all:
                            if team.groupprofile.group_owner!=mem:
                                team.groupprofile.remove_user(mem)
                        return redirect('/teams/'+name)
                    else: 
                        return HttpResponse('insufficient permission')

                elif 'delete' in request.POST:
                    #deletes the team. can only be accessed from the owner
                    if team.groupprofile.group_owner==user:
                        team.delete()
                        return redirect('/teams')
                    else: 
                        return HttpResponse('insufficient permission')  

                elif 'kick' in request.POST:
                    #kickes the given member. can only be accessed from the owner and cannot ckick the owner
                    if team.groupprofile.group_owner==user:
                        kick_mem_email=request.POST.get('kick')
                        kick_mem=User.objects.get(email=kick_mem_email)
                        if kick_mem==team.groupprofile.group_owner:
                            return HttpResponse('can\'t kick yourself')
                        else:
                            team.groupprofile.remove_user(kick_mem)
                            return redirect('/teams/'+name)
                    else: 
                        return HttpResponse('insufficient permission') 
                    

            return render(request=request,
                        template_name="team_detail.html",
                        context={'team' : team, 'owner': team.groupprofile.group_owner,'member' : member , 'member_page' : posts  })
        
        return HttpResponse('insufficient permission')
        # user not in group

    return redirect('/login')
    # redirect to login page if user is not authenticated

