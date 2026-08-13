from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Utilisateur


class UtilisateurAdmin(UserAdmin):
    model = Utilisateur
    list_display = ("email", "prenom", "nom", "role", "is_active", "is_staff")
    list_filter = ("role", "is_active", "is_staff")
    ordering = ("email",)
    search_fields = ("email", "prenom", "nom")

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Informations personnelles", {"fields": ("prenom", "nom", "role")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Dates importantes", {"fields": ("last_login", "date_creation", "date_modification")}),
    )
    readonly_fields = ("date_creation", "date_modification", "last_login")

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "prenom", "nom", "role", "password1", "password2"),
        }),
    )


admin.site.register(Utilisateur, UtilisateurAdmin)