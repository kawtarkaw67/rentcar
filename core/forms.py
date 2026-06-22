"""
Formulaires de l'application de location de voitures.
Chaque formulaire correspond à un modèle ou une action métier.
"""

from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Voiture, Client, Reservation, Categorie, Paiement


class CategorieForm(forms.ModelForm):
    """
    Formulaire de création/modification d'une catégorie.
    """
    class Meta:
        model = Categorie
        fields = ["nom", "description"]


class VoitureForm(forms.ModelForm):
    """
    Formulaire de création/modification d'une voiture.
    Tous les champs du modèle sont inclus.
    """
    class Meta:
        model = Voiture
        fields = ["marque", "modele", "immatriculation", "annee", "prix_jour", "statut", "categorie", "image"]


class ClientForm(forms.ModelForm):
    """
    Formulaire de création/modification d'un client.
    Les champs email et adresse sont optionnels.
    """
    class Meta:
        model = Client
        fields = ["nom", "prenom", "cin", "telephone", "email", "adresse"]


class ReservationForm(forms.ModelForm):
    """
    Formulaire de création/modification d'une réservation (côté admin/employé).
    Permet de choisir le client, la voiture et les dates.
    Les widgets date utilisent des inputs HTML5 de type 'date'.
    """
    class Meta:
        model = Reservation
        fields = ["client", "voiture", "date_debut", "date_fin"]
        widgets = {
            "date_debut": forms.DateInput(attrs={"type": "date"}),
            "date_fin": forms.DateInput(attrs={"type": "date"}),
        }


class ClientReservationForm(forms.ModelForm):
    """
    Formulaire de création de réservation côté client.
    Le client n'est pas un champ à remplir : il est automatiquement
    associé dans la vue (request.user.client).
    """
    class Meta:
        model = Reservation
        fields = ["voiture", "date_debut", "date_fin"]
        widgets = {
            "date_debut": forms.DateInput(attrs={"type": "date"}),
            "date_fin": forms.DateInput(attrs={"type": "date"}),
        }


class ClientRegistrationForm(UserCreationForm):
    """
    Formulaire d'inscription d'un nouveau client.
    Crée simultanément un compte User et un profil Client.
    Les champs obligatoires sont : username, nom, prénom, CIN, téléphone, password.
    L'email est optionnel.
    """
    nom = forms.CharField(max_length=100, required=True, label="Nom")
    prenom = forms.CharField(max_length=100, required=True, label="Prénom")
    cin = forms.CharField(max_length=50, required=True, label="CIN")
    telephone = forms.CharField(max_length=30, required=True, label="Téléphone")
    email = forms.EmailField(required=False, label="Email")

    class Meta:
        model = User
        fields = ["username", "nom", "prenom", "cin", "telephone", "email", "password1", "password2"]

    def clean_cin(self):
        """
        Vérifie que le CIN n'est pas déjà utilisé par un autre client.
        """
        cin = self.cleaned_data.get("cin")
        if Client.objects.filter(cin=cin).exists():
            raise forms.ValidationError("Ce CIN est déjà utilisé.")
        return cin

    def save(self, commit=True):
        """
        Sauvegarde : crée le User puis le profil Client associé.
        """
        # Créer le User d'abord (sans le sauvegarder tout de suite)
        user = super().save(commit=False)
        user.email = self.cleaned_data.get("email", "")

        if commit:
            user.save()
            # Créer le profil Client lié
            Client.objects.create(
                user=user,
                nom=self.cleaned_data["nom"],
                prenom=self.cleaned_data["prenom"],
                cin=self.cleaned_data["cin"],
                telephone=self.cleaned_data["telephone"],
                email=self.cleaned_data.get("email", ""),
            )
        return user


class PaiementForm(forms.ModelForm):
    """
    Formulaire d'enregistrement d'un paiement pour une réservation.
    Le montant est pré-rempli avec le montant de la réservation.
    """
    class Meta:
        model = Paiement
        fields = ["montant", "date_paiement", "mode_paiement", "statut"]
        widgets = {
            "date_paiement": forms.DateInput(attrs={"type": "date"}),
        }


class TerminerReservationForm(forms.Form):
    """
    Formulaire de clôture d'une réservation.
    Enregistre la date réelle de retour et une remarque éventuelle.
    """
    date_retour_reelle = forms.DateField(
        label="Date réelle de retour",
        widget=forms.DateInput(attrs={"type": "date"}),
    )
    remarque = forms.CharField(
        label="Remarque",
        required=False,
        widget=forms.Textarea(attrs={"rows": 3}),
    )


class ProfilForm(forms.Form):
    """
    Formulaire de modification du profil utilisateur.
    Modifie à la fois le User (username, email, nom, prénom) et le Client (téléphone, adresse).
    """
    username = forms.CharField(max_length=150, label="Nom d'utilisateur")
    email = forms.EmailField(required=False, label="Email")
    first_name = forms.CharField(max_length=30, required=False, label="Prénom")
    last_name = forms.CharField(max_length=30, required=False, label="Nom")
    telephone = forms.CharField(max_length=30, required=False, label="Téléphone")
    adresse = forms.CharField(required=False, label="Adresse", widget=forms.Textarea(attrs={"rows": 3}))

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        if user:
            self.fields["username"].initial = user.username
            self.fields["email"].initial = user.email
            self.fields["first_name"].initial = user.first_name
            self.fields["last_name"].initial = user.last_name
            if hasattr(user, "client"):
                self.fields["telephone"].initial = user.client.telephone
                self.fields["adresse"].initial = user.client.adresse

    def clean_username(self):
        username = self.cleaned_data.get("username")
        if User.objects.filter(username=username).exclude(pk=self.user.pk).exists():
            raise forms.ValidationError("Ce nom d'utilisateur est déjà pris.")
        return username

    def save(self):
        self.user.username = self.cleaned_data["username"]
        self.user.email = self.cleaned_data.get("email", "")
        self.user.first_name = self.cleaned_data.get("first_name", "")
        self.user.last_name = self.cleaned_data.get("last_name", "")
        self.user.save()
        if hasattr(self.user, "client"):
            self.user.client.telephone = self.cleaned_data.get("telephone", "")
            self.user.client.adresse = self.cleaned_data.get("adresse", "")
            self.user.client.save()
        return self.user
