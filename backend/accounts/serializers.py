from rest_framework import serializers

from .models import Utilisateur


class UtilisateurSerializer(serializers.ModelSerializer):
    mot_de_passe = serializers.CharField(
        source="password", write_only=True, required=False, min_length=8
    )

    class Meta:
        model = Utilisateur
        fields = (
            "id", "email", "prenom", "nom", "role", "is_active",
            "mot_de_passe", "date_creation",
        )
        read_only_fields = ("id", "date_creation")

    def validate(self, attrs):
        if self.instance is None and not attrs.get("password"):
            raise serializers.ValidationError({
                "mot_de_passe": "Un mot de passe est requis pour créer un utilisateur."
            })
        return attrs

    def create(self, validated_data):
        mot_de_passe = validated_data.pop("password")
        return Utilisateur.objects.create_user(password=mot_de_passe, **validated_data)

    def update(self, instance, validated_data):
        mot_de_passe = validated_data.pop("password", None)
        for attribut, valeur in validated_data.items():
            setattr(instance, attribut, valeur)
        if mot_de_passe:
            instance.set_password(mot_de_passe)
        instance.save()
        return instance
