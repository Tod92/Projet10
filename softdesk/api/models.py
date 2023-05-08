from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser

# Create your models here.

"""
TODO : on_delete SET_NULL ou SET_DEFAULT (voir rgpd)
"""
class User(AbstractUser):
    time_created = models.DateTimeField(auto_now_add=True)


class Project(models.Model):
    # ProtectedError si on supprime le user, un commenteire perdu peut poser pb
    author_user_id = models.ForeignKey(settings.AUTH_USER_MODEL,
                                       on_delete=models.PROTECT)
    title = models.CharField(max_length=30)
    description = models.CharField(max_length=1000)
    type = models.CharField(max_length=30)
    time_created = models.DateTimeField(auto_now_add=True)

    contributors = models.ManyToManyField(User,
                                          # limit_choices_to={'role': CREATOR},
                                          related_name='projects',
                                          through='Contributor',
                                          )


class Issue(models.Model):
    project_id = models.ForeignKey(Project,
                                   on_delete=models.CASCADE)
    # ProtectedError si on supprime le user, un commenteire perdu peut poser pb
    author_user_id = models.ForeignKey(settings.AUTH_USER_MODEL,
                                       on_delete=models.PROTECT,
                                       related_name="author"
                                       )
    assignee_user_id = models.ForeignKey(settings.AUTH_USER_MODEL,
                                         on_delete=models.SET_NULL,
                                         null=True,
                                         )

    title = models.CharField(max_length=30)
    description = models.CharField(max_length=1000)
    tag = models.CharField(max_length=30)
    priority = models.CharField(max_length=30)
    status = models.CharField(max_length=30)
    time_created = models.DateTimeField(auto_now_add=True)

class Comment(models.Model):
    # ProtectedError si on supprime le user, un commenteire perdu peut poser pb
    author_user_id = models.ForeignKey(settings.AUTH_USER_MODEL,
                                       on_delete=models.PROTECT)
    issue_id = models.ForeignKey(Issue,
                                 on_delete=models.CASCADE)

    description = models.CharField(max_length=1000)
    time_created = models.DateTimeField(auto_now_add=True)

class Contributor(models.Model):
    """
    Pour relation many to many : user <-> project
    """
    user_id = models.ForeignKey(to=settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE,
                             related_name='contributor')

    project_id = models.ForeignKey(to=Project,
                                on_delete=models.CASCADE,
                                related_name='contributing_to')

    time_created = models.DateTimeField(auto_now_add=True)
