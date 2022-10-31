from django.views.generic import DetailView

from .models import Profile


class ProfileUser(DetailView):
    template_name = 'users/profile.html'
    model = Profile
    context_object_name = 'profile'
