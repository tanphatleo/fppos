from django.contrib.auth.models import User, Group
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin

from rest_framework import viewsets
from .serializers import UserSerializer, GroupSerializer


class UserViewSet( viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class GroupViewSet( viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer