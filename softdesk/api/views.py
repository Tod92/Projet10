from django.shortcuts import render
from django.db.models import Q
from django.shortcuts import get_object_or_404
# from rest_framework.decorators import permission_classes
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework.response import Response

from api.permissions import (
    IsAuthenticated,
    IsAuthor,
    IsContributor,
    CustomIsProjectAuthorOrContrib
)
from api.models import (
    Project,
    User,
    Issue,
    Comment,
    Contributor
)

from api.serializers import (
    UserSerializer,
    ProjectSerializer,
    ProjectListSerializer,
    IssueSerializer,
    IssueListSerializer,
    CommentSerializer,
    CommentListSerializer,
    ContributorSerializer,
    ContributorListSerializer
)



class MultipleSerializerMixin:
    # Mixin dont les views devront hériter afin de viser un serializer different
    # pour le détail
    """
    actions :
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
        if self.action in self.detail_actions and self.detail_serializer_class is not None:
            return self.detail_serializer_class
        else:
            return self.serializer_class


class RegisterView(APIView):
    permission_classes = []
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

class UserAPIView(APIView):
    """
    test docstring (affichage sur la page web de l'api)
    """
    def get(self, *args, **kwargs):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)


class ProjectViewset(MultipleSerializerMixin,
                     ModelViewSet):

    serializer_class = ProjectListSerializer
    detail_serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated,IsAuthor|IsContributor]
    # Pas de methode PATCH
    http_method_names = ['get','post','put','delete']
    def get_permissions(self):
        print(self.action)
        if self.action in ['destroy', 'update']:
            self.permission_classes = [IsAuthor,]

        return super(ProjectViewset, self).get_permissions()


    def get_queryset(self):
        user = self.request.user
        # On affiche uniquement les projets dont l'utilisateur est contributeur
        # ou auteur
        if self.action == 'list'and user.is_staff is False:
            queryset = Project.objects.filter(Q(contributors=user)|Q(author_user_id=user))
        else:
            queryset = Project.objects.all()
        # si ajout dans la requete HTTP de ?type=
        type = self.request.GET.get('type')
        if type is not None:
            queryset = queryset.filter(type=type)
        return queryset

    def perform_create(self, serializer):
        serializer.save(author_user_id=self.request.user)


class IssueViewset(MultipleSerializerMixin,
                   ModelViewSet):

    serializer_class = IssueListSerializer
    detail_serializer_class = IssueSerializer
    http_method_names = ['get','post','put','delete']
    # Pas de methode PATCH

    queryset = Issue.objects.all()

    def get_permissions(self):
        """
        Surcharge de la fonction afin de verifier les droits sur le projet
        auquel est lié l'Issue
        """
        self.project_id = self.kwargs.get("project_pk")
        self.project = get_object_or_404(Project, pk=self.project_id)

        return [IsAuthenticated(), CustomIsProjectAuthorOrContrib(project=self.project)]

    def get_queryset(self, *args, **kwargs):
        return Issue.objects.filter(project_id=self.project_id)

    def perform_create(self, serializer):
        serializer.save(author_user_id=self.request.user,
                        project_id=self.project)

class CommentViewset(MultipleSerializerMixin,
                     ModelViewSet):

    serializer_class = CommentListSerializer
    detail_serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated,IsAuthor]
    # Pas de methode PATCH
    http_method_names = ['get','post','put','delete']

    queryset = Comment.objects.all()

    def get_permissions(self):
        """
        Surcharge de la fonction afin de verifier les droits sur le projet
        auquel est lié le commentaire
        """
        self.project_id = self.kwargs.get("project_pk")
        self.project = get_object_or_404(Project, pk=self.project_id)

        return [IsAuthenticated(), CustomIsProjectAuthorOrContrib(project=self.project)]

    def get_queryset(self, *args, **kwargs):
        issue_id = self.kwargs.get("issue_pk")
        return Comment.objects.filter(issue_id=issue_id)

    def perform_create(self, serializer):
        issue_id = self.kwargs.get("issue_pk")
        issue = Issue.objects.get(id=issue_id)
        serializer.save(author_user_id=self.request.user,
                        issue_id=issue)

class ContributorViewset(MultipleSerializerMixin,
                         ModelViewSet):

    serializer_class = ContributorListSerializer
    detail_serializer_class = ContributorSerializer
    # permission_classes = [IsAuthenticated,]
    # Pas de methode PATCH ni PUT
    http_method_names = ['get','post','delete']

    queryset = Contributor.objects.all()

    def get_permissions(self):
        """
        Surcharge de la fonction afin de verifier les droits sur le projet
        auquel est lié le commentaire
        """
        self.project_id = self.kwargs.get("project_pk")
        self.project = get_object_or_404(Project, pk=self.project_id)
        return [IsAuthenticated(), CustomIsProjectAuthorOrContrib(project=self.project)]

    def get_queryset(self, *args, **kwargs):
        project_id = self.kwargs.get("project_pk")
        return Contributor.objects.filter(project_id=project_id)

    def perform_create(self, serializer):
        project_id = self.kwargs.get("project_pk")
        project = Project.objects.get(id=project_id)
        serializer.save(project_id=project)

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

# class IssueListCreate(APIView):
#     """
#     supports get and post
#     """
#     def get(self, request, project_id):
#         issues = Issue.objects.filter(project_id=project_id)
#         serializer = IssueListSerializer(issues, many=True)
#         return Response(serializer.data)
#
#     def post(self, request, project_id):
#         project = Project.objects.get(id=project_id)
#         serializer = IssueSerializer(data=request.data)
#         # serializer.data.user_author_id = request.user
#         serializer.is_valid(raise_exception=True)
#         serializer.save(
#             author_user_id=request.user,
#             project_id=project)
#         return Response(serializer.data)
#
# class IssueUpdateDelete(APIView):
#     permission_classes = [IsAuthenticated&IsAuthor]
#
#     def put(self, request, project_id, issue_id):
#         issue = Issue.objects.get(id=issue_id)
#         serializer = IssueSerializer(issue, data=request.data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response(serializer.data)
#
#     def delete(self, request, project_id, issue_id):
#         issue = Issue.objects.get(id=issue_id)
#         issue.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)
#
# class CommentListCreate(APIView):
#     """
#     supports get and post
#     """
#     def get(self, request, project_id, issue_id):
#         comments = Comment.objects.filter(issue_id=issue_id)
#         serializer = CommentListSerializer(comments, many=True)
#         return Response(serializer.data)
#
#     def post(self, request, project_id, issue_id):
#         issue = Issue.objects.get(id=issue_id)
#         serializer = CommentSerializer(data=request.data)
#         # serializer.data.user_author_id = request.user
#         serializer.is_valid(raise_exception=True)
#         serializer.save(
#             author_user_id=request.user,
#             issue_id=issue)
#         return Response(serializer.data)
#
# class CommentDetailUpdateDelete(APIView):
#     permission_classes = [IsAuthenticated&IsAuthor]
#
#     def get(self, request, project_id, issue_id, comment_id):
#         comment = Comment.objects.get(id=comment_id)
#         serializer = CommentListSerializer(comment)
#         return Response(serializer.data)
#
#     def put(self, request, project_id, issue_id, comment_id):
#         comment = Comment.objects.get(id=comment_id)
#         serializer = CommentSerializer(comment, data=request.data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response(serializer.data)
#
#     def delete(self, request, project_id, issue_id, comment_id):
#         comment = Comment.objects.get(id=comment_id)
#         comment.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)

# class ContributorListCreateDelete(APIView):
#     def get(self, request, project_id):
#         contributors = Contributor.objects.filter(project_id=project_id)
#         serializer = ContributorSerializer(contributors, many=True)
#         return Response(serializer.data)
#
#     def post(self, request, project_id):
#         project = Project.objects.get(id=project_id)
#         serializer = ContributorSerializer(data=request.data)
#         # serializer.data.user_author_id = request.user
#         serializer.is_valid(raise_exception=True)
#         serializer.save(project_id=project)
#         return Response(serializer.data)
#
#     def delete(self, request, project_id, user_id):
#         contributor = Contributor.objects.filter(
#             project_id=project_id,
#             user_id=user_id
#         )
#         contributor.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)
#


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
