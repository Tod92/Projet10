from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser

# Create your models here.

class User(AbstractUser):
    pass

class Project(models.Model):
    title = models.CharField(max_length=30)
    description = models.CharField(max_length=1000)
    type = models.CharField(max_length=30)

    contributors = models.ManyToManyField(User,
                                          # limit_choices_to={'role': CREATOR},
                                          related_name='projects',
                                          through='Contributor',
                                          )


class Issue(models.Model):
    title = models.CharField(max_length=30)
    description = models.CharField(max_length=1000)
    tag = models.CharField(max_length=30)
    priority = models.CharField(max_length=30)
    status = models.CharField(max_length=30)

class Comment(models.Model):
    description = models.CharField(max_length=1000)

class Contributor(models.Model):
    """
    Pour relation many to many user <-> project
    """
    user = models.ForeignKey(to=settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE,
                             related_name='contrinutions')

    project = models.ForeignKey(to=Project,
                                on_delete=models.CASCADE,
                                related_name='contrinutions')

    time_created = models.DateTimeField(auto_now_add=True)
