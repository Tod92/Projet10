from django.contrib.auth.models import Group
from rest_framework import serializers
from .models import User, Project, Issue


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "username", "password"]

    def create(self, validated_data):
        user = User.objects.create(username=validated_data['username']
                                   )
        user.set_password(validated_data['password'])
        user.save()
        return user


class IssueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Issue
        fields = ['id', 'project_id', 'title', 'description', 'tag', 'priority', 'status']

class ProjectSerializer(serializers.HyperlinkedModelSerializer):
    # Nous redéfinissons l'attribut 'product' qui porte le même nom que dans la liste des champs à afficher
    # en lui précisant un serializer paramétré à 'many=True' car les produits sont multiples pour une catégorie
    class Meta:
        model = Project
        fields = ['id', 'title', 'description', 'type']
    # def create(self, validated_data):
    #     project = Project.objects.create(
    #         title=validated_data['title'],
    #         description=validated_data['description'],
    #     )
