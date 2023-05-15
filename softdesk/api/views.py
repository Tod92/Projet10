from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from api.models import Project, User, Issue
from api.serializers import ProjectSerializer, UserSerializer, IssueSerializer

#
# class MultipleSerializerMixin:
#
#     detail_serializer_class = None
#
#     def get_serializer_class(self):
#         if self.action == 'retrieve' and self.detail_serializer_class is not None:
#             return self.detail_serializer_class
#         return super().get_serializer_class()
#
# class AdminProjectViewset(MultipleSerializerMixin, ModelViewSet):
#
#     serializer_class = CategoryListSerializer
#     detail_serializer_class = CategoryDetailSerializer
#     # Nous avons simplement à appliquer la permission sur le viewset
#     permission_classes = [IsAuthenticated]
#
#     def get_queryset(self):
#         return Category.objects.all()
# view for registering users

class RegisterView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

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
        queryset = Issue.objects.filter(status='TODO')
        # http://127.0.0.1:8000/api/issue/?priority=1
        project_id = self.request.GET.get('project_id')
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        return queryset
    # def perform_create(self, serializer):
    #     serializer.save(user=self.request.user)
