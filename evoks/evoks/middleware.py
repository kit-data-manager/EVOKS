import hashlib
import base64
import os

from django.http import HttpRequest
from django.http.response import HttpResponseNotFound, HttpResponseForbidden
from django.utils.deprecation import MiddlewareMixin
from prometheus_client import Counter, Gauge

from vocabularies.models import Vocabulary
from django.shortcuts import redirect

MONITORING_EXEMPT_URLS = ['metrics/', 'health/']
LOGIN_EXEMPT_URLS = ['logout', 'signup', 'login', 'reset_password/', 'health/',
                     'reset_password_sent/', 'reset_password_complete/', 'ToS']

users_total_counter = Counter("evoks_users_total", "Total number of requests served")
users_unique_gauge = Gauge("evoks_unique_users", "Unique number of users, distinguished by IP")

class MonitoringMiddleware(MiddlewareMixin):
    stored_ips = set()

    @staticmethod
    def get_client_ip(request):
        """Extracts client IP address from request."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    def process_request(self, request):
        metrics_enabled = os.environ.get('METRICS_ENABLED', 'false')
        if metrics_enabled != 'true':
            return

        path = request.path_info.lstrip('/')
        if not any(url == path for url in MONITORING_EXEMPT_URLS):
            users_total_counter.inc()
            ip = self.get_client_ip(request)

            if ip:
                hashed_ip = hashlib.sha256(ip.encode()).hexdigest()
                self.stored_ips.add(hashed_ip)
                users_unique_gauge.set(len(self.stored_ips))


class LoginRequiredMiddleware(MiddlewareMixin):

    def __init__(self, get_response):
        super().__init__(get_response)
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    @staticmethod
    def basic_auth(request: HttpRequest):
        if 'HTTP_AUTHORIZATION' in request.META:
            auth = request.META['HTTP_AUTHORIZATION'].split()
            if len(auth) == 2:
                if auth[0].lower() == "basic":
                    uname, passwd = base64.b64decode(auth[1]).split(b':')
                    req_uname = os.environ.get('METRICS_USER', 'metrics')
                    req_passwd = os.environ.get('METRICS_PASS', 'metricsPass')
                    if uname.decode() == req_uname and passwd.decode() == req_passwd:
                        return True
        return False

    @staticmethod
    def process_view(request: HttpRequest, view_func, view_args, view_kwargs):
        assert hasattr(request, 'user')
        path = request.path_info.lstrip('/')
        if request.path.startswith('/reset/'):
            return None

        if path == "metrics/":
            if LoginRequiredMiddleware.basic_auth(request):
                return None
            else:
                return HttpResponseForbidden()

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
