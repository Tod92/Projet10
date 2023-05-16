"""
URL configuration for softdesk project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

from rest_framework import routers
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from api.views import (
    UserAPIView,
    RegisterView,
    ProjectListCreate,
    ProjectDetailUpdateDelete,
    ContributorListCreate,
    IssueViewset
)
# Ici nous créons notre routeur
router = routers.SimpleRouter()
# Puis lui déclarons une url basée sur le mot clé ‘category’ et notre view
# afin que l’url générée soit celle que nous souhaitons ‘/api/category/’
router.register('issue', IssueViewset, basename='issue')


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/signup/', RegisterView.as_view(), name="sign_up"),
    path('api-auth/', include('rest_framework.urls')),
    path('api/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/user/', UserAPIView.as_view()),
    path('api/projects/', ProjectListCreate.as_view()),
    path('api/projects/<int:project_id>/', ProjectDetailUpdateDelete.as_view()),
    path('api/projects/<int:project_id>/users/', ContributorListCreate.as_view()),

    path('api/', include(router.urls))  # Il faut bien penser à ajouter les urls du router dans la liste des urls disponibles.
]
