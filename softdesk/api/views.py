from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from rest_framework.response import Response

from api.models import Project, User, Issue
from api.serializers import ProjectSerializer, UserSerializer, IssueSerializer


class UserAPIView(APIView):

    def get(self, *args, **kwargs):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)
class ProjectAPIView(APIView):

    def get(self, *args, **kwargs):
        projects = Project.objects.all()
        serializer = ProjectSerializer(projects, many=True)
        return Response(serializer.data)

class IssueViewset(ModelViewSet):

    serializer_class = IssueSerializer
    def get_queryset(self):
        return Issue.objects.all()
