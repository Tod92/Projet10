from django.shortcuts import render
from django.db.models import Q
from django.db import IntegrityError
from django.shortcuts import get_object_or_404
# from rest_framework.decorators import permission_classes
from rest_framework import status
from rest_framework.throttling import UserRateThrottle
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


# Mixin dont les views devront hériter afin de viser un serializer different
# pour le détail
class MultipleSerializerMixin:

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


class ProjectViewset(MultipleSerializerMixin,
                     ModelViewSet):

    serializer_class = ProjectListSerializer
    detail_serializer_class = ProjectSerializer
    throttle_classes = [UserRateThrottle]
    permission_classes = [IsAuthenticated,IsAuthor|IsContributor]
    # Pas de methode PATCH
    http_method_names = ['get','post','put','delete']
    def get_permissions(self):
        if self.action in ['destroy', 'update']:
            self.permission_classes = [IsAuthenticated,IsAuthor]
        return super().get_permissions()


    def get_queryset(self):
        user = self.request.user
        # On affiche uniquement les projets dont l'utilisateur est contributeur
        # ou auteur
        if self.action == 'list'and user.is_staff is False:
            queryset = Project.objects.filter(Q(contributors=user)|Q(author_user_id=user))
        else:
            queryset = Project.objects.all()
        # Si ajout dans la requete HTTP de ?type=
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
    throttle_classes = [UserRateThrottle]
    # permission_classes = [IsAuthenticated,]
    http_method_names = ['get','post','put','delete']

    queryset = Issue.objects.all()

    def get_permissions(self):
        print('action demandée : ', self.action)
        # Verification des droits sur le projet
        self.project_id = self.kwargs.get("project_pk")
        self.project = get_object_or_404(Project, pk=self.project_id)
        if self.action in ['destroy', 'update']:
            return [IsAuthenticated(),IsAuthor()]

        return [IsAuthenticated(), CustomIsProjectAuthorOrContrib(project=self.project)]

    def get_queryset(self, *args, **kwargs):
        return Issue.objects.filter(project_id=self.project_id)

    def perform_create(self, serializer):
        serializer.save(author_user_id=self.request.user,
                        assignee_user_id=self.request.user,
                        project_id=self.project)

class CommentViewset(MultipleSerializerMixin,
                     ModelViewSet):

    serializer_class = CommentListSerializer
    detail_serializer_class = CommentSerializer
    throttle_classes = [UserRateThrottle]
    permission_classes = [IsAuthenticated,IsAuthor]
    # Pas de methode PATCH
    http_method_names = ['get','post','put','delete']

    queryset = Comment.objects.all()

    def get_permissions(self):
        """
        Surcharge de la fonction afin de verifier les droits sur le projet
        auquel est lié le commentaire
        """
        print(self.action)
        self.project_id = self.kwargs.get("project_pk")
        self.project = get_object_or_404(Project, pk=self.project_id)
        if self.action in ['destroy', 'update']:
                return [IsAuthenticated(),IsAuthor()]

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
    throttle_classes = [UserRateThrottle]
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
        # project_id = self.kwargs.get("project_pk")
        return Contributor.objects.filter(project_id=self.project_id)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try :
            self.perform_create(serializer) # Calls serializer.save()
        except IntegrityError:
            return Response({"Error": "this user is already a contributor for this project" }, status=status.HTTP_400_BAD_REQUEST)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class ReplaceUserView(APIView):
    """
    Vue pour faire disparaitre toute trace d'un utilisateur suite à demande rgpd

    """

    def post(self, request, user_id):
        if request.user.is_staff != True:
            print('nope')
            return None
        user = User.objects.get(id=user_id)
        projects = Project.objects.filter(author_user_id=user_id)

        issues = Issue.objects.filter(author_user_id=user_id)
        # TODO : assignee
        comments = Comment.objects.filter(author_user_id=user_id)

        #return Response(status=status.HTTP_200_OK)



#     def perform_create(self, serializer):
#         project_id = self.kwargs.get("project_pk")
#         project = Project.objects.get(id=project_id)
#         try:
#             serializer.save(project_id=project)
#             print('la')
#         except IntegrityError:
#             print('ici')
#             Response({"Fail": "blablal" }, status=status.HTTP_400_BAD_REQUEST)
# #

# class UserAPIView(APIView):
#     """
#     test docstring (affichage sur la page web de l'api)
#     """
#     def get(self, *args, **kwargs):
#         users = User.objects.all()
#         serializer = UserSerializer(users, many=True)
#         return Response(serializer.data)
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
