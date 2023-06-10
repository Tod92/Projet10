from django.shortcuts import render

# Create your views here.
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework.mixins import UpdateModelMixin, ListModelMixin
from rest_framework.response import Response
from rest_framework.permissions import BasePermission, IsAuthenticated, SAFE_METHODS


from api.models import (
    Project,
    User,
    Issue,
    Comment,
    Contributor
)

from api.serializers import (
    ProjectSerializer,
    ProjectListSerializer,
    UserSerializer,
    IssueSerializer,
    IssueListSerializer,
    CommentSerializer,
    CommentListSerializer,
    ContributorSerializer
)

class IsAuthorOrReadOnly(BasePermission):
    """
    Object-level permission to only allow owners of an object to edit it.
    Assumes the model instance has an `author_user_id` attribute.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in SAFE_METHODS:
            return True

        return obj.author_user_id == request.user

class IsAuthor(BasePermission):
    """
    Object-level permission to only allow owners of an object to edit it.
    Assumes the model instance has an `author_user_id` attribute.
    """

    def has_object_permission(self, request, view, obj):
        # Instance must have an attribute named `owner`.
        return obj.author_user_id == request.user

class IsContributor(BasePermission):
    """
    """
    def has_object_permission(self, request, view, obj):
        pass


class MultipleSerializerMixin:
    # Mixin dont les views devront hériter afin de viser un serializer different
    # pour le détail
    """
    list : appel en GET  sur l’URL de liste ;
    retrieve : appel en GET  sur l’URL de détail (qui comporte alors un identifiant) ;
    create : appel en POST  sur l’URL de liste ;
    update : appel en PUT  sur l’URL de détail ;
    partial_update : appel en PATCH  sur l’URL de détail ;
    destroy : appel en DELETE  sur l’URL de détail.
    """

    detail_serializer_class = None
    detail_actions = [
        'retrieve',
        'create',
        'update'
    ]
    def get_serializer_class(self):
        print('h2')
        if self.action in self.detail_actions and self.detail_serializer_class is not None:
            return self.detail_serializer_class
        else:
            return self.serializer_class

class ProjectViewset(MultipleSerializerMixin,
                     ModelViewSet):
                     # UpdateModelMixin,
                     # ListModelMixin):
    serializer_class = ProjectListSerializer
    detail_serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated,]

    def get_queryset(self):
        # On filtre les projets auxquels l'utilisateur contribue dès la requete
        # en base de donnée
        queryset = Project.objects.filter(contributors=self.request.user)
        # si ajout dans la requete HTTP de ?type=
        type = self.request.GET.get('type')
        if type is not None:
            queryset = queryset.filter(type=type)
        return queryset

    def perform_create(self, serializer):
        serializer.save(author_user_id=self.request.user)

#
# class ProjectListCreate(APIView):
#     """
#     supports get and post
#     """
#     def get(self, request):
#         projects = Project.objects.all()
#         serializer = ProjectListSerializer(projects, many=True)
#         return Response(serializer.data)
#
#     def post(self, request):
#         serializer = ProjectSerializer(data=request.data)
#         # serializer.data.user_author_id = request.user
#         serializer.is_valid(raise_exception=True)
#         serializer.save(author_user_id=request.user)
#         return Response(serializer.data)
#
# class ProjectDetailUpdateDelete(APIView):
#     permission_classes = [IsAuthenticated&IsAuthor]
#
#     def get(self, request, project_id):
#         project = Project.objects.get(id=project_id)
#         serializer = ProjectSerializer(project)
#         return Response(serializer.data)
#
#     def put(self, request, project_id):
#         project = Project.objects.get(id=project_id)
#         serializer = ProjectSerializer(project, data=request.data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response(serializer.data)
#
#     def delete(self, request, project_id):
#         project = Project.objects.get(id=project_id)
#         project.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)

class IssueListCreate(APIView):
    """
    supports get and post
    """
    def get(self, request, project_id):
        issues = Issue.objects.filter(project_id=project_id)
        serializer = IssueListSerializer(issues, many=True)
        return Response(serializer.data)

    def post(self, request, project_id):
        project = Project.objects.get(id=project_id)
        serializer = IssueSerializer(data=request.data)
        # serializer.data.user_author_id = request.user
        serializer.is_valid(raise_exception=True)
        serializer.save(
            author_user_id=request.user,
            project_id=project)
        return Response(serializer.data)

class IssueUpdateDelete(APIView):
    permission_classes = [IsAuthenticated&IsAuthor]

    def put(self, request, project_id, issue_id):
        issue = Issue.objects.get(id=issue_id)
        serializer = IssueSerializer(issue, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, project_id, issue_id):
        issue = Issue.objects.get(id=issue_id)
        issue.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class CommentListCreate(APIView):
    """
    supports get and post
    """
    def get(self, request, project_id, issue_id):
        comments = Comment.objects.filter(issue_id=issue_id)
        serializer = CommentListSerializer(comments, many=True)
        return Response(serializer.data)

    def post(self, request, project_id, issue_id):
        issue = Issue.objects.get(id=issue_id)
        serializer = CommentSerializer(data=request.data)
        # serializer.data.user_author_id = request.user
        serializer.is_valid(raise_exception=True)
        serializer.save(
            author_user_id=request.user,
            issue_id=issue)
        return Response(serializer.data)

class CommentDetailUpdateDelete(APIView):
    permission_classes = [IsAuthenticated&IsAuthor]

    def get(self, request, project_id, issue_id, comment_id):
        comment = Comment.objects.get(id=comment_id)
        serializer = CommentListSerializer(comment)
        return Response(serializer.data)

    def put(self, request, project_id, issue_id, comment_id):
        comment = Comment.objects.get(id=comment_id)
        serializer = CommentSerializer(comment, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, project_id, issue_id, comment_id):
        comment = Comment.objects.get(id=comment_id)
        comment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class ContributorListCreateDelete(APIView):
    def get(self, request, project_id):
        contributors = Contributor.objects.filter(project_id=project_id)
        serializer = ContributorSerializer(contributors, many=True)
        return Response(serializer.data)

    def post(self, request, project_id):
        project = Project.objects.get(id=project_id)
        serializer = ContributorSerializer(data=request.data)
        # serializer.data.user_author_id = request.user
        serializer.is_valid(raise_exception=True)
        serializer.save(project_id=project)
        return Response(serializer.data)

    def delete(self, request, project_id, user_id):
        contributor = Contributor.objects.filter(
            project_id=project_id,
            user_id=user_id
        )
        contributor.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class RegisterView(APIView):
    permission_classes = []
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


# class IssueViewset(ModelViewSet):
#
#     serializer_class = IssueSerializer
#     def get_queryset(self):
#         queryset = Issue.objects.filter(status='TODO')
#         # http://127.0.0.1:8000/api/issue/?priority=1
#         project_id = self.request.GET.get('project_id')
#         if project_id:
#             queryset = queryset.filter(project_id=project_id)
#         return queryset
#     # def perform_create(self, serializer):
#     #     serializer.save(user=self.request.user)
