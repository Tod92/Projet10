from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser

# Create your models here.

class User(AbstractUser):
    """
    En héritant de la classe AbstractUser de Django, on récupère bien les
    attribus souhaités : first_name, last_name, email, password
    time_created ajouté pour correspondre au nom de l'attribut utilisé sur les
    autres classes, quitte à faire doublon avec 'date_joined' hérité
    """
    time_created = models.DateTimeField(auto_now_add=True)


class Project(models.Model):
    BACKEND = "BACK"
    FRONTEND = "FRONT"
    IOS = "IOS"
    ANDROID = "ANDROID"
    TYPE_CHOICES = [
        (BACKEND, "Back-end"),
        (FRONTEND, "Front-end"),
        (IOS, "Ios"),
        (ANDROID, "Android"),
    ]

    # ProtectedError si on supprime le user, un projet perdu peut poser pb
    author_user_id = models.ForeignKey(settings.AUTH_USER_MODEL,
                                       on_delete=models.PROTECT)

    type = models.CharField(
        max_length=10,
        choices=TYPE_CHOICES,
        # default=BACKEND,
    )
    title = models.CharField(max_length=30)
    description = models.CharField(max_length=1000)
    time_created = models.DateTimeField(auto_now_add=True)
    contributors = models.ManyToManyField(User,
                                          # limit_choices_to={'role': CREATOR},
                                          related_name='projects',
                                          through='Contributor',
                                          )


class Issue(models.Model):

    """
    Chaque problème doit avoir un titre, une description, un assigné (l’assigné
    par défaut étant l'auteur lui-même), une priorité (FAIBLE, MOYENNE ou
     ÉLEVÉE), une balise (BUG, AMÉLIORATION ou TÂCHE), un statut (À faire,
      En cours ou Terminé), le project_id auquel il est lié et un created_time
      (horodatage), ainsi que d'autres attributs mentionnés dans le diagramme
      de classe.
    """
    LOW = "LOW"
    MEDIUM = "MED"
    HIGH = "HIGH"
    PRIORITY_CHOICES = [
        (LOW, "Faible"),
        (MEDIUM, "Moyenne"),
        (HIGH, "Élevée")
        ]

    BUG = "BUG"
    FEATURE = "FEAT"
    TASK = "TASK"
    TAG_CHOICES = [
        (BUG, "Bug"),
        (FEATURE, "Amélioration"),
        (TASK, "Tâche")
        ]

    TODO = "TODO"
    IN_PROGRESS = "IN_PRGRS"
    CLOSED = "CLOSED"
    STATUS_CHOICES = [
        (TODO, "À faire"),
        (IN_PROGRESS, "En cours"),
        (CLOSED, "Terminée")
        ]

    project_id = models.ForeignKey(
        Project,
        on_delete=models.CASCADE
        )
    # ProtectedError si on supprime le user, un commenteire perdu peut poser pb
    author_user_id = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="author"
        )
    # TODO : createur du problème doit etre l'assigné par défaut
    assignee_user_id = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        )

    title = models.CharField(max_length=30)
    description = models.CharField(max_length=1000)
    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES
        )
    tag = models.CharField(
        max_length=10,
        choices=TAG_CHOICES
        )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES
        )
    time_created = models.DateTimeField(auto_now_add=True)

class Comment(models.Model):
    # ProtectedError si on supprime le user, un commenteire perdu peut poser pb
    author_user_id = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT
        )
    issue_id = models.ForeignKey(
        Issue,
        on_delete=models.CASCADE
        )

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
