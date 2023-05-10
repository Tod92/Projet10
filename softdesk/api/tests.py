from django.urls import reverse_lazy
from django.test import TestCase
from rest_framework.test import APITestCase

from api.models import User, Project, Issue

class TestIssue(APITestCase):
    # Nous stockons l’url de l'endpoint dans un attribut de classe pour pouvoir
    # l’utiliser plus facilement dans chacun de nos tests
    # Le '-list' est la complétude faite par le routeur
    url = reverse_lazy('issue-list')

    def format_datetime(self, value):
        # Cette méthode est un helper permettant de formater une date en chaine
        # de caractères sous le même format que celui de l’api
        return value.strftime("%Y-%m-%dT%H:%M:%S.%fZ")

    def test_list(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        login = self.client.login(username='testuser', password='12345')
        self.project = Project.objects.create(
            author_user_id=self.user,
            type="BACK",
            title="Project Test1",
            )

        # Créons deux issues dont une seule est status : 'TODO'
        issue = Issue.objects.create(
            project_id=self.project,
            author_user_id=self.user,
            assignee_user_id=self.user,
            title='Issue Test1',
            description='test numero 1',
            priority='LOW',
            tag='BUG',
            status='TODO'
            )
        Issue.objects.create(
            project_id=self.project,
            author_user_id=self.user,
            assignee_user_id=self.user,
            title='Issue Test2',
            description='test numero 2',
            priority='LOW',
            tag='BUG',
            status='CLOSED'
            )

        # On réalise l’appel en GET en utilisant le client de la classe de test
        response = self.client.get(self.url)
        # Nous vérifions que le status code est bien 200
        # et que les valeurs retournées sont bien celles attendues
        self.assertEqual(response.status_code, 200)
        excepted = [
            {
                'id': issue.pk,
                'project_id': issue.project_id.pk,
                'title': issue.title,
            }
        ]
        self.assertEqual(excepted, response.json())

    def test_create(self):
        # Nous vérifions qu’aucune catégorie n'existe avant de tenter d’en créer une
        self.assertFalse(Issue.objects.exists())
        response = self.client.post(self.url, data={'title': 'Nouvelle Issue'})
        # Vérifions que le status code est bien en erreur et nous empêche de créer une catégorie
        self.assertEqual(response.status_code, 405)
        # Enfin, vérifions qu'aucune nouvelle catégorie n’a été créée malgré le status code 405
        self.assertFalse(Issue.objects.exists())
