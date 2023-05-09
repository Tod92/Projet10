from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework.response import Response

from api.models import Project, User, Issue
from api.serializers import ProjectSerializer, UserSerializer, IssueSerializer


class UserAPIView(APIView):

    def get(self, *args, **kwargs):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

class ProjectViewset(ReadOnlyModelViewSet):

    serializer_class = ProjectSerializer
    def get_queryset(self):
        return Project.objects.all()

class IssueViewset(ModelViewSet):

    serializer_class = IssueSerializer
    def get_queryset(self):
        queryset = Issue.objects.filter(status="active")
        # http://127.0.0.1:8000/api/issue/?priority=1
        project_id = self.request.GET.get('project_id')
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        return queryset
    # def perform_create(self, serializer):
    #     serializer.save(user=self.request.user)
