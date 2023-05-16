from django.shortcuts import render

# Create your views here.
from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework.response import Response

from api.models import (
    Project,
    User,
    Issue,
    Contributor
)
from api.serializers import (
    ProjectSerializer,
    UserSerializer,
    IssueSerializer,
    ContributorSerializer
)

class IsAuthorOrReadOnly(permissions.BasePermission):
    """
    Object-level permission to only allow owners of an object to edit it.
    Assumes the model instance has an `author_user_id` attribute.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Instance must have an attribute named `owner`.
        return obj.author_user_id == request.user

class ProjectListCreate(APIView):
    """
    supports get and post
    """
    def get(self, request):
        projects = Project.objects.all()
        serializer = ProjectSerializer(projects, many=True)
        return Response(serializer.data)

    def post(self, request):

        serializer = ProjectSerializer(data=request.data)
        # serializer.data.user_author_id = request.user
        serializer.is_valid(raise_exception=True)
        serializer.save(author_user_id=request.user)
        return Response(serializer.data)

class ProjectDetailUpdateDelete(APIView):
    permission_classes = [IsAuthorOrReadOnly]
    
    def get(self, request, project_id):
        project = Project.objects.get(id=project_id)
        serializer = ProjectSerializer(project)
        return Response(serializer.data)

    def put(self, request, project_id):
        project = Project.objects.get(id=project_id)
        serializer = ProjectSerializer(project, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, project_id):
        project = Project.objects.get(id=project_id)
        project.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ContributorListCreate(APIView):
    def get(self, request, project_id):
        contributors = Contributor.objects.filter(project_id=project_id)
        serializer = ContributorSerializer(contributors, many=True)
        return Response(serializer.data)

    def post(self, request, project_id):
        pass

class RegisterView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

class UserAPIView(APIView):
    """
    test docstring
    """
    def get(self, *args, **kwargs):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)


class IssueViewset(ModelViewSet):

    serializer_class = IssueSerializer
    def get_queryset(self):
        queryset = Issue.objects.filter(status='TODO')
        # http://127.0.0.1:8000/api/issue/?priority=1
        project_id = self.request.GET.get('project_id')
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        return queryset
    # def perform_create(self, serializer):
    #     serializer.save(user=self.request.user)
