from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Project, Issue, Contributor


# Register your models here.
admin.site.register(User, UserAdmin)
admin.site.register(Project)
admin.site.register(Issue)
admin.site.register(Contributor)
