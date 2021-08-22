from django.http.response import Http404, HttpResponse, HttpResponseNotFound
from vocabularies.models import Vocabulary
from django.shortcuts import redirect


class LoginRequiredMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        LOGIN_EXEMPT_URLS = ['logout', 'signup', 'login', 'reset_password/',
                             'reset_password_sent/', 'reset_password_complete/', 'ToS']
        assert hasattr(request, 'user')
        path = request.path_info.lstrip('/')
        if request.path.startswith('/reset/'):
            return None

        if not request.user.is_authenticated:
            if not any(url == path for url in LOGIN_EXEMPT_URLS):
                return redirect('login')


class PartOfVocabularyMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        if len(view_kwargs) != 0:
            if 'voc_name' in view_kwargs:
                name = view_kwargs.get('voc_name')
                try:
                    assert Vocabulary.objects.filter(name=name).exists()
                except AssertionError:
                    return HttpResponseNotFound('The vocabulary you`re looking for doesn`t exist')

                voc = Vocabulary.objects.get(name=name)
                part = voc.state == 'Review'
                for profile in voc.profiles.all():
                    if profile.user == request.user:
                        part = True
                for group_profile in voc.groups.all():
                    for user in group_profile.group.user_set.all():
                        if user == request.user:
                            part = True
                if not part:
                    return redirect('base')
