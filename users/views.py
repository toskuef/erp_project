from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic import DetailView

from .models import Profile


class LoginRequired(View):
    """
    Redirects to login if user is anonymous
    """
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(LoginRequired, self).dispatch(*args, **kwargs)


class ProfileUser(LoginRequired, DetailView):
    template_name = 'users/profile.html'
    model = Profile
    context_object_name = 'profile'
