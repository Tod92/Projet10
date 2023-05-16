from django.contrib.auth.models import Group
from rest_framework import serializers
from .models import User, Project, Issue, Contributor


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

    def update(self, instance, validated_data):
        instance.title = validated_data.get('title', instance.title)
        instance.description = validated_data.get('description', instance.description)
        instance.type = validated_data.get('type', instance.type)
        instance.save()
        return instance

class ContributorSerializer(serializers.HyperlinkedModelSerializer):
    # Nous redéfinissons l'attribut 'product' qui porte le même nom que dans la liste des champs à afficher
    # en lui précisant un serializer paramétré à 'many=True' car les produits sont multiples pour une catégorie
    class Meta:
        model = Contributor
        fields = ['user_id','project_id']
