"""
Modèles de données pour l'application de location de voitures.
Trois modèles principaux : Voiture, Client, Réservation.
"""

from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.contrib.auth.models import User
from datetime import date


class Categorie(models.Model):
    """
    Catégorie de biens (ex: Berline, SUV, Utilitaire, etc.).
    Permet de classifier les voitures.
    """
    nom = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Catégories"
        ordering = ["nom"]

    def __str__(self):
        return self.nom


class Voiture(models.Model):
    """
    Représente un véhicule du parc automobile.
    Chaque voiture a un statut : disponible, louée ou en maintenance.
    L'immatriculation est unique.
    """
    STATUT_CHOICES = [
        ("disponible", "Disponible"),
        ("louee", "Louee"),
        ("maintenance", "Maintenance"),
    ]

    marque = models.CharField(max_length=100)
    modele = models.CharField(max_length=100)
    immatriculation = models.CharField(max_length=50, unique=True)
    annee = models.IntegerField(
        validators=[
            MinValueValidator(1990, message="L'année doit être >= 1990."),
            MaxValueValidator(date.today().year + 1, message=f"L'année ne peut pas dépasser {date.today().year + 1}."),
        ]
    )
    prix_jour = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0, message="Le prix par jour doit être positif.")],
    )
    statut = models.CharField(
        max_length=20,
        choices=STATUT_CHOICES,
        default="disponible",
    )
    image = models.ImageField(upload_to='voitures/', blank=True, null=True)
    categorie = models.ForeignKey(
        Categorie,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="voitures",
    )

    def __str__(self):
        return f"{self.marque} {self.modele} - {self.immatriculation}"


class Client(models.Model):
    """
    Représente un client de l'agence.
    Peut être lié à un compte utilisateur (User) pour l'espace client,
    ou exister sans compte (client ajouté par le personnel).
    Le CIN est unique.
    """
    # Lien optionnel vers le compte utilisateur Django
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    cin = models.CharField(max_length=50, unique=True)
    telephone = models.CharField(max_length=30)
    email = models.EmailField(blank=True, null=True)
    adresse = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.nom} {self.prenom}"


class Reservation(models.Model):
    """
    Représente une réservation de voiture par un client.
    Le statut évolue : en_attente → en_cours → terminée (ou annulée).
    Le montant total est calculé automatiquement à la sauvegarde.
    """
    STATUT_CHOICES = [
        ("en_attente", "En attente"),
        ("en_cours", "En cours"),
        ("terminee", "Terminee"),
        ("annulee", "Annulee"),
    ]

    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    voiture = models.ForeignKey(Voiture, on_delete=models.CASCADE)
    date_debut = models.DateField()
    date_fin = models.DateField()
    montant_total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
    )
    statut = models.CharField(
        max_length=20,
        choices=STATUT_CHOICES,
        default="en_attente",
    )
    date_retour_reelle = models.DateField(null=True, blank=True)
    remarque = models.TextField(blank=True, null=True)
    date_creation = models.DateTimeField(auto_now_add=True)

    def calculer_montant(self):
        """Calcule le montant total : nombre de jours × prix par jour."""
        nombre_jours = (self.date_fin - self.date_debut).days
        # Minimum 1 jour même si les dates sont identiques
        if nombre_jours <= 0:
            nombre_jours = 1
        return nombre_jours * self.voiture.prix_jour

    def save(self, *args, **kwargs):
        """Recalcule automatiquement le montant avant chaque sauvegarde."""
        self.montant_total = self.calculer_montant()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Reservation {self.client} - {self.voiture}"


class Paiement(models.Model):
    """
    Représente un paiement associé à une réservation.
    Un statut simple : paye, en_attente, annule.
    """
    STATUT_CHOICES = [
        ("paye", "Paye"),
        ("en_attente", "En attente"),
        ("annule", "Annule"),
    ]
    MODE_CHOICES = [
        ("especes", "Especes"),
        ("virement", "Virement"),
        ("carte", "Carte bancaire"),
    ]

    reservation = models.ForeignKey(Reservation, on_delete=models.CASCADE, related_name="paiements")
    montant = models.DecimalField(max_digits=10, decimal_places=2)
    date_paiement = models.DateField()
    mode_paiement = models.CharField(max_length=20, choices=MODE_CHOICES, default="especes")
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default="en_attente")
    date_creation = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Paiement {self.montant} DH - {self.get_statut_display()}"


class Historique(models.Model):
    """
    Journal d'audit des actions importantes du système.
    Enregistre chaque action : création, validation, refus, paiement, retour, annulation.
    """
    ACTION_CHOICES = [
        ("creation", "Création"),
        ("validation", "Validation"),
        ("refus", "Refus"),
        ("annulation", "Annulation"),
        ("paiement", "Paiement"),
        ("retour", "Retour"),
        ("inscription", "Inscription"),
        ("connexion", "Connexion"),
        ("modification", "Modification"),
    ]

    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    description = models.TextField()
    utilisateur = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    reservation = models.ForeignKey(Reservation, on_delete=models.SET_NULL, null=True, blank=True, related_name="historiques")
    date_action = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Historiques"
        ordering = ["-date_action"]

    def __str__(self):
        return f"[{self.get_action_display()}] {self.description}"


class Notification(models.Model):
    """
    Notification persistante pour un utilisateur.
    Créée à chaque action importante (nouvelle réservation, validation, paiement, etc.).
    """
    utilisateur = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")
    titre = models.CharField(max_length=200)
    message = models.TextField()
    lu = models.BooleanField(default=False)
    lien = models.CharField(max_length=255, blank=True, null=True)
    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Notifications"
        ordering = ["-date_creation"]

    def __str__(self):
        return f"[{'Lu' if self.lu else 'Non lu'}] {self.titre}"
