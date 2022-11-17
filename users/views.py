from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic import DetailView

from .models import Profile, AnySettingsUser


class LoginRequired(View):
    """
    Redirects to login if user is anonymous
    """
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(LoginRequired, self).dispatch(*args, **kwargs)


class LoginUserCustom(LoginView):
    def get_success_url(self):
        if not Profile.objects.filter(user=self.request.user).exists():
            Profile.objects.create(user=self.request.user)
        if not AnySettingsUser.objects.filter(user=self.request.user).exists():
            AnySettingsUser.objects.create(user=self.request.user,
                                           filter_customer_list=[1, 2, 3, 4, 5,
                                                                 6])
        return super().get_success_url()


class ProfileUser(LoginRequired, DetailView):
    template_name = 'users/profile.html'
    model = Profile
    context_object_name = 'profile'
