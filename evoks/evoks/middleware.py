from vocabularies.models import Vocabulary
from django.shortcuts import redirect


class LoginRequiredMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response
    
    def process_view(self, request, view_func, view_args, view_kwargs):
        LOGIN_EXEMPT_URLS = ['logout', 'signup', 'login', 'reset']
        assert hasattr(request, 'user')
        path = request.path_info.lstrip('/')

        if not request.user.is_authenticated:
            if not any(url == path for url in LOGIN_EXEMPT_URLS):
                print(path)
                return redirect('login')



class PartOfVocabularyMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response
    
    def process_view(self, request, view_func, view_args, view_kwargs):
        if len(view_kwargs) != 0:
            if 'name' in view_kwargs:
                name = view_kwargs.get('name')
                print(name)
                assert Vocabulary.objects.filter(name=name).exists()
                voc = Vocabulary.objects.get(name=name)
                part = voc.state == 'Review'
                for key in voc.profiles.all():
                    if key.user == request.user:
                        part = True
                if not part:
                    return redirect('dashboard')