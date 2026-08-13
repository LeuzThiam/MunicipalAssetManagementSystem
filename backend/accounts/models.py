from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.db import models


class UtilisateurManager(BaseUserManager):
    def create_user(self, email, password=None, **champs_supplementaires):
        if not email:
            raise ValueError("L'adresse email est obligatoire.")
        email = self.normalize_email(email)
        utilisateur = self.model(email=email, **champs_supplementaires)
        utilisateur.set_password(password)
        utilisateur.save(using=self._db)
        return utilisateur

    def create_superuser(self, email, password=None, **champs_supplementaires):
        champs_supplementaires.setdefault("is_staff", True)
        champs_supplementaires.setdefault("is_superuser", True)
        champs_supplementaires.setdefault("role", Utilisateur.Role.ADMIN)
        return self.create_user(email, password, **champs_supplementaires)


class Utilisateur(AbstractBaseUser, PermissionsMixin):
    class Role(models.TextChoices):
        ADMIN = "ADMIN", "Administrateur"
        GESTIONNAIRE = "GESTIONNAIRE", "Gestionnaire"
        INSPECTEUR = "INSPECTEUR", "Inspecteur"
        LECTEUR = "LECTEUR", "Lecteur"

    email = models.EmailField(unique=True)
    prenom = models.CharField(max_length=150)
    nom = models.CharField(max_length=150)
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.LECTEUR)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    objects = UtilisateurManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["prenom", "nom"]

    def __str__(self):
        return self.email