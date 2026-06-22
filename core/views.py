"""
Vues principales de l'application de location de voitures.
Chaque vue gère une fonctionnalité spécifique : accueil, dashboard,
CRUD voitures/clients/réservations, exports, PDF, statistiques, RBAC.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User, Group
from django.contrib.auth.views import (
    PasswordResetView, PasswordResetDoneView,
    PasswordResetConfirmView, PasswordResetCompleteView,
)
from django.contrib import messages
from django.core.paginator import Paginator
from django.db import models
from django.db.models import Count, Sum
from django.http import HttpResponse, JsonResponse
from datetime import date, timedelta
import csv

from .models import Voiture, Client, Reservation, Categorie, Paiement, Historique, Notification
from .forms import (
    VoitureForm, ClientForm, ReservationForm,
    ClientRegistrationForm, ClientReservationForm,
    CategorieForm, PaiementForm, TerminerReservationForm,
    ProfilForm,
)


# ═══════════════════════════════════════════════════════════
# FONCTIONS UTILITAIRES (helpers pour éviter la duplication)
# ═══════════════════════════════════════════════════════════

def _est_requete_ajax(request):
    """
    Vérifie si la requête est une requête AJAX.
    Une requête AJAX a soit l'en-tête X-Requested-With, soit le paramètre format=json.
    """
    return (
        request.headers.get('x-requested-with') == 'XMLHttpRequest'
        or request.GET.get('format') == 'json'
    )


def enregistrer_historique(action, description, utilisateur=None, reservation=None):
    """
    Enregistre une action dans l'historique.
    Helper pour éviter la duplication à chaque vue métier.
    """
    Historique.objects.create(
        action=action,
        description=description,
        utilisateur=utilisateur,
        reservation=reservation,
    )


def creer_notification(utilisateur, titre, message, lien=None):
    """
    Crée une notification persistante pour un utilisateur.
    """
    if utilisateur and utilisateur.is_authenticated:
        Notification.objects.create(
            utilisateur=utilisateur,
            titre=titre,
            message=message,
            lien=lien,
        )


def _reponse_action(request, succes, message, redirection, **extras):
    """
    Retourne une réponse adaptée au type de requête :
    - JSON si c'est de l'AJAX
    - Redirection HTTP avec message flash sinon

    Args:
        request: la requête HTTP
        succes (bool): True si l'action a réussi
        message (str): le message à afficher
        redirection (str): nom de l'URL de redirection
        **extras: données supplémentaires pour la réponse JSON
    """
    if _est_requete_ajax(request):
        reponse = {"status": "success" if succes else "error", "message": message}
        reponse.update(extras)
        return JsonResponse(reponse)
    else:
        if succes:
            messages.success(request, message)
        else:
            messages.error(request, message)
        return redirect(redirection)


def _valider_et_creer_reservation(request, form, client_impose=None):
    """
    Valide un formulaire de réservation et crée la réservation si tout est correct.
    Vérifie : dates valides, voiture pas en maintenance, pas de conflit de période.

    Args:
        request: la requête HTTP
        form: le formulaire de réservation (déjà lié aux données POST)
        client_impose: si fourni, impose ce client (pour l'espace client)

    Returns:
        (succes: bool, resultat: Reservation|dict) - La réservation créée ou un dict d'erreur
    """
    reservation = form.save(commit=False)

    # Attribuer le client si imposé (espace client)
    if client_impose is not None:
        reservation.client = client_impose

    # Vérification 1 : date de fin après date de début
    if reservation.date_fin <= reservation.date_debut:
        return False, {
            "message": "La date de fin doit être après la date de début.",
            "redirection": "liste_reservations" if client_impose is None else "client_dashboard",
        }

    # Vérification 2 : voiture pas en maintenance
    if reservation.voiture.statut == "maintenance":
        return False, {
            "message": "Cette voiture est en maintenance, elle ne peut pas être louée.",
            "redirection": "liste_reservations" if client_impose is None else "client_dashboard",
        }

    # Vérification 3 : pas de conflit de période
    conflit = Reservation.objects.filter(
        voiture=reservation.voiture,
        statut__in=["en_attente", "en_cours"],
        date_debut__lt=reservation.date_fin,
        date_fin__gt=reservation.date_debut,
    )
    if conflit.exists():
        return False, {
            "message": "Cette voiture n'est pas disponible sur cette période.",
            "redirection": "liste_reservations" if client_impose is None else "client_dashboard",
        }

    # Tout est OK : on sauvegarde
    reservation.statut = "en_attente"
    reservation.save()
    enregistrer_historique(
        "creation",
        f"Réservation créée pour {reservation.client} — {reservation.voiture} "
        f"(du {reservation.date_debut} au {reservation.date_fin}, {reservation.montant_total} DH)",
        utilisateur=request.user if request.user.is_authenticated else None,
        reservation=reservation,
    )
    # Notifier les admins
    for admin_user in User.objects.filter(is_superuser=True).exclude(pk=getattr(request.user, 'pk', None)):
        creer_notification(
            admin_user,
            "Nouvelle réservation",
            f"{reservation.client} a demandé une réservation pour {reservation.voiture} "
            f"du {reservation.date_debut} au {reservation.date_fin}.",
            lien=f"/reservations/{reservation.pk}/",
        )
    return True, reservation


def _calculer_ca_mensuel(nb_mois=6):
    """
    Calcule le chiffre d'affaires mensuel des réservations terminées
    sur les N derniers mois.
    """
    terminees = Reservation.objects.filter(statut="terminee")
    aujourdhui = date.today()
    ca_mensuel = []

    for i in range(nb_mois - 1, -1, -1):
        # Premier jour du mois cible
        debut_mois = aujourdhui.replace(day=1) - timedelta(days=i * 30)
        debut_mois = debut_mois.replace(day=1)

        # Dernier jour du mois cible
        if debut_mois.month == 12:
            fin_mois = debut_mois.replace(
                year=debut_mois.year + 1, month=1, day=1
            ) - timedelta(days=1)
        else:
            fin_mois = debut_mois.replace(
                month=debut_mois.month + 1, day=1
            ) - timedelta(days=1)

        ca = sum(
            r.montant_total
            for r in terminees.filter(
                date_creation__gte=debut_mois, date_creation__lte=fin_mois
            )
        )
        ca_mensuel.append({
            "mois": debut_mois.strftime("%B %Y"),
            "ca": ca,
        })
    return ca_mensuel


def _peut_annuler_reservation(reservation):
    """Une réservation peut être annulée si elle est 'en_attente' ou 'en_cours'."""
    return reservation.statut in ("en_attente", "en_cours")


def _peut_terminer_reservation(reservation):
    """Une réservation peut être terminée si elle est 'en_cours'."""
    return reservation.statut == "en_cours"


def _peut_accepter_ou_refuser(reservation):
    """Une réservation peut être acceptée/refusée si elle est 'en_attente'."""
    return reservation.statut == "en_attente"


# ═══════════════════════════════════════════════════════════
# PERMISSIONS (RBAC)
# ═══════════════════════════════════════════════════════════

def est_admin(user):
    """
    Vérifie si l'utilisateur est admin (superuser OU membre du groupe 'Admin').
    """
    return user.is_superuser or user.groups.filter(name="Admin").exists()


admin_required = user_passes_test(est_admin, login_url="dashboard")


def est_client(user):
    """
    Vérifie si l'utilisateur a un profil client associé.
    Plus fiable que hasattr(user, 'client') car vérifie l'existence en base.
    """
    return Client.objects.filter(user=user).exists()


# ═══════════════════════════════════════════════════════════
# CRUD CATÉGORIES
# ═══════════════════════════════════════════════════════════

@login_required
def liste_categories(request):
    """
    Liste paginée des catégories avec recherche.
    """
    query = request.GET.get("q", "")
    categories = Categorie.objects.all()

    if query:
        categories = categories.filter(nom__icontains=query)

    paginator = Paginator(categories, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "core/categories.html", {
        "page_obj": page_obj,
        "query": query,
    })


@admin_required
def ajouter_categorie(request):
    """Ajouter une nouvelle catégorie (admin uniquement)."""
    if request.method == "POST":
        form = CategorieForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Catégorie ajoutée avec succès.")
            return redirect("liste_categories")
    else:
        form = CategorieForm()
    return render(request, "core/form_categorie.html", {
        "form": form,
        "titre": "Ajouter une catégorie",
    })


@admin_required
def modifier_categorie(request, pk):
    """Modifier une catégorie existante (admin uniquement)."""
    categorie = get_object_or_404(Categorie, pk=pk)
    if request.method == "POST":
        form = CategorieForm(request.POST, instance=categorie)
        if form.is_valid():
            form.save()
            messages.success(request, "Catégorie modifiée avec succès.")
            return redirect("liste_categories")
    else:
        form = CategorieForm(instance=categorie)
    return render(request, "core/form_categorie.html", {
        "form": form,
        "titre": "Modifier la catégorie",
    })


@admin_required
def supprimer_categorie(request, pk):
    """Supprimer une catégorie (admin uniquement)."""
    categorie = get_object_or_404(Categorie, pk=pk)
    if request.method == "POST":
        categorie.delete()
        messages.success(request, "Catégorie supprimée.")
        return redirect("liste_categories")
    return render(request, "core/confirmer_suppression.html", {
        "objet": categorie,
        "type_objet": "la catégorie",
    })


# ═══════════════════════════════════════════════════════════
# CRUD PAIEMENTS
# ═══════════════════════════════════════════════════════════

@login_required
def liste_paiements(request):
    """
    Liste paginée des paiements avec filtres par statut et recherche.
    """
    statut_filter = request.GET.get("statut", "")
    query = request.GET.get("q", "")
    paiements = Paiement.objects.select_related("reservation__client", "reservation__voiture").all()

    if statut_filter:
        paiements = paiements.filter(statut=statut_filter)

    if query:
        paiements = paiements.filter(
            models.Q(reservation__client__nom__icontains=query)
            | models.Q(reservation__client__prenom__icontains=query)
            | models.Q(reservation__voiture__marque__icontains=query)
            | models.Q(reservation__voiture__modele__icontains=query)
        )

    paginator = Paginator(paiements, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "core/paiements.html", {
        "page_obj": page_obj,
        "statut_filter": statut_filter,
        "statuts": Paiement.STATUT_CHOICES,
        "query": query,
    })


@login_required
def detail_paiement(request, pk):
    """Affiche le détail d'un paiement."""
    paiement = get_object_or_404(Paiement, pk=pk)
    return render(request, "core/detail_paiement.html", {
        "paiement": paiement,
    })


@admin_required
def ajouter_paiement(request, reservation_pk=None):
    """
    Enregistrer un paiement pour une réservation.
    Si reservation_pk est fourni, la réservation est pré-sélectionnée.
    """
    reservation = None
    if reservation_pk:
        reservation = get_object_or_404(Reservation, pk=reservation_pk)

    if request.method == "POST":
        form = PaiementForm(request.POST)
        if form.is_valid():
            paiement = form.save(commit=False)
            if reservation is None:
                reservation_id = request.POST.get("reservation")
                reservation = get_object_or_404(Reservation, pk=reservation_id)
            paiement.reservation = reservation
            paiement.save()
            enregistrer_historique(
                "paiement",
                f"Paiement de {paiement.montant} DH enregistré pour la réservation #{reservation.pk} "
                f"(mode: {paiement.get_mode_paiement_display()})",
                utilisateur=request.user,
                reservation=reservation,
            )
            # Notifier le client
            if reservation.client.user:
                creer_notification(
                    reservation.client.user,
                    "Paiement enregistré",
                    f"Un paiement de {paiement.montant} DH a été enregistré pour votre réservation #{reservation.pk}.",
                    lien=f"/reservations/{reservation.pk}/",
                )
            messages.success(request, "Paiement enregistré avec succès.")
            return redirect("detail_reservation", pk=paiement.reservation.pk)
    else:
        form = PaiementForm()
        if reservation:
            form.fields["montant"].initial = reservation.montant_total

    return render(request, "core/form_paiement.html", {
        "form": form,
        "titre": "Enregistrer un paiement",
        "reservation": reservation,
        "reservations": Reservation.objects.filter(statut__in=["en_cours", "terminee"]) if not reservation else None,
    })


@admin_required
def modifier_paiement(request, pk):
    """Modifier un paiement existant (admin uniquement)."""
    paiement = get_object_or_404(Paiement, pk=pk)
    if request.method == "POST":
        form = PaiementForm(request.POST, instance=paiement)
        if form.is_valid():
            form.save()
            messages.success(request, "Paiement modifié avec succès.")
            return redirect("detail_paiement", pk=paiement.pk)
    else:
        form = PaiementForm(instance=paiement)
    return render(request, "core/form_paiement.html", {
        "form": form,
        "titre": "Modifier le paiement",
        "reservation": paiement.reservation,
        "reservations": None,
    })


# ═══════════════════════════════════════════════════════════
# PAGE D'ACCUEIL (publique)
# ═══════════════════════════════════════════════════════════

def accueil(request):
    """
    Page d'accueil publique.
    - Si l'utilisateur est déjà connecté : redirection vers son espace
      (dashboard admin ou dashboard client selon son profil)
    - Sinon : affiche les stats générales du parc auto
    """
    if request.user.is_authenticated:
        if est_client(request.user):
            return redirect("client_dashboard")
        return redirect("dashboard")

    total_voitures = Voiture.objects.count()
    voitures_dispo = Voiture.objects.filter(statut="disponible").count()

    return render(request, "core/accueil.html", {
        "total_voitures": total_voitures,
        "voitures_dispo": voitures_dispo,
    })


# ═══════════════════════════════════════════════════════════
# AUTHENTIFICATION
# ═══════════════════════════════════════════════════════════

def login_view(request):
    """
    Connexion utilisateur.
    - GET : affiche le formulaire de connexion
    - POST : authentifie l'utilisateur et le redirige vers son espace
    """
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            # Redirection selon le type de profil
            if est_client(user):
                return redirect("client_dashboard")
            return redirect("dashboard")
        else:
            messages.error(request, "Identifiants incorrects.")
    return render(request, "core/login.html")


def logout_view(request):
    """Déconnexion et redirection vers la page de login."""
    logout(request)
    return redirect("login")


@login_required
def modifier_profil(request):
    """
    Page de modification du profil utilisateur.
    Modifie les informations du User et du Client associé.
    """
    if request.method == "POST":
        form = ProfilForm(request.POST, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profil mis à jour avec succès.")
            return redirect("modifier_profil")
    else:
        form = ProfilForm(user=request.user)
    return render(request, "core/modifier_profil.html", {"form": form})


# Réinitialisation de mot de passe
password_reset_view = PasswordResetView.as_view(
    template_name="core/password_reset.html",
    email_template_name="core/password_reset_email.html",
    subject_template_name="core/password_reset_subject.txt",
    success_url="/password-reset/envoye/",
)

password_reset_done_view = PasswordResetDoneView.as_view(
    template_name="core/password_reset_done.html",
)

password_reset_confirm_view = PasswordResetConfirmView.as_view(
    template_name="core/password_reset_confirm.html",
    success_url="/password-reset/termine/",
)

password_reset_complete_view = PasswordResetCompleteView.as_view(
    template_name="core/password_reset_complete.html",
)


# ═══════════════════════════════════════════════════════════
# DASHBOARD ADMIN
# ═══════════════════════════════════════════════════════════

@login_required
def dashboard(request):
    """
    Tableau de bord pour le personnel (admin et employés).
    Affiche les indicateurs clés, les tops véhicules/clients,
    et les demandes en attente de validation.
    """
    # --- Indicateurs voitures ---
    total_voitures = Voiture.objects.count()
    voitures_disponibles = Voiture.objects.filter(statut="disponible").count()
    voitures_louees = Voiture.objects.filter(statut="louee").count()
    voitures_maintenance = Voiture.objects.filter(statut="maintenance").count()

    # --- Indicateurs clients ---
    total_clients = Client.objects.count()

    # --- Indicateurs réservations ---
    reservations_en_cours = Reservation.objects.filter(statut="en_cours").count()
    reservations_terminees = Reservation.objects.filter(statut="terminee").count()
    demandes_en_attente = Reservation.objects.filter(statut="en_attente").order_by("-date_creation")[:10]
    nb_demandes_attente = Reservation.objects.filter(statut="en_attente").count()

    # --- Chiffre d'affaires (réservations terminées) ---
    terminees = Reservation.objects.filter(statut="terminee")
    ca_total = sum(r.montant_total for r in terminees)

    # --- Top véhicule le plus loué ---
    top_voiture = (
        terminees
        .values("voiture__marque", "voiture__modele", "voiture__immatriculation")
        .annotate(nb=Count("id"))
        .order_by("-nb")
        .first()
    )

    # --- Top 5 clients (par CA généré) ---
    top_clients = (
        terminees
        .values("client__nom", "client__prenom")
        .annotate(nb=Count("id"), total=Sum("montant_total"))
        .order_by("-total")[:5]
    )

    # --- Indicateurs paiements ---
    paiements_recus = Paiement.objects.filter(statut="paye")
    total_recu = sum(p.montant for p in paiements_recus)
    paiements_en_attente = Paiement.objects.filter(statut="en_attente").count()

    # --- Derniers retours ---
    derniers_retours = Reservation.objects.filter(
        statut="terminee", date_retour_reelle__isnull=False
    ).order_by("-date_retour_reelle")[:5]

    context = {
        "total_voitures": total_voitures,
        "voitures_disponibles": voitures_disponibles,
        "voitures_louees": voitures_louees,
        "voitures_maintenance": voitures_maintenance,
        "total_clients": total_clients,
        "reservations_en_cours": reservations_en_cours,
        "reservations_terminees": reservations_terminees,
        "demandes_en_attente": demandes_en_attente,
        "nb_demandes_attente": nb_demandes_attente,
        "ca_total": ca_total,
        "top_voiture": top_voiture,
        "top_clients": top_clients,
        "total_recu": total_recu,
        "paiements_en_attente": paiements_en_attente,
        "derniers_retours": derniers_retours,
    }
    return render(request, "core/dashboard.html", context)


# ═══════════════════════════════════════════════════════════
# CRUD VOITURES
# ═══════════════════════════════════════════════════════════

@login_required
def liste_voitures(request):
    """
    Liste paginée des voitures avec recherche, filtre par statut et filtre par catégorie.
    Accessible à tous les utilisateurs connectés (admin et employés).
    """
    query = request.GET.get("q", "")
    statut_filter = request.GET.get("statut", "")
    categorie_filter = request.GET.get("categorie", "")
    voitures = Voiture.objects.all()

    # Recherche textuelle
    if query:
        voitures = voitures.filter(
            models.Q(marque__icontains=query)
            | models.Q(modele__icontains=query)
            | models.Q(immatriculation__icontains=query)
        )

    # Filtre par statut
    if statut_filter:
        voitures = voitures.filter(statut=statut_filter)

    # Filtre par catégorie
    if categorie_filter:
        voitures = voitures.filter(categorie_id=categorie_filter)

    # Pagination (10 par page)
    paginator = Paginator(voitures, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "core/voitures.html", {
        "page_obj": page_obj,
        "query": query,
        "statut_filter": statut_filter,
        "statuts": Voiture.STATUT_CHOICES,
        "categories": Categorie.objects.all(),
        "categorie_filter": categorie_filter,
        "is_admin": est_admin(request.user),
    })


@admin_required
def ajouter_voiture(request):
    """Ajouter une nouvelle voiture dans le parc (admin uniquement)."""
    if request.method == "POST":
        form = VoitureForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Voiture ajoutée avec succès.")
            return redirect("liste_voitures")
    else:
        form = VoitureForm()
    return render(request, "core/form_voiture.html", {
        "form": form,
        "titre": "Ajouter une voiture",
    })


@admin_required
def modifier_voiture(request, pk):
    """Modifier une voiture existante (admin uniquement)."""
    voiture = get_object_or_404(Voiture, pk=pk)
    if request.method == "POST":
        form = VoitureForm(request.POST, instance=voiture)
        if form.is_valid():
            form.save()
            messages.success(request, "Voiture modifiée avec succès.")
            return redirect("liste_voitures")
    else:
        form = VoitureForm(instance=voiture)
    return render(request, "core/form_voiture.html", {
        "form": form,
        "titre": "Modifier la voiture",
    })


@login_required
def detail_voiture(request, pk):
    """
    Affiche le détail d'une voiture et l'historique de ses réservations.
    """
    voiture = get_object_or_404(Voiture, pk=pk)
    reservations = Reservation.objects.filter(voiture=voiture).order_by("-date_creation")
    return render(request, "core/detail_voiture.html", {
        "voiture": voiture,
        "reservations": reservations,
    })


@admin_required
def supprimer_voiture(request, pk):
    """Supprimer une voiture du parc (admin uniquement)."""
    voiture = get_object_or_404(Voiture, pk=pk)
    if request.method == "POST":
        voiture.delete()
        messages.success(request, "Voiture supprimée.")
        return redirect("liste_voitures")
    return render(request, "core/confirmer_suppression.html", {
        "objet": voiture,
        "type_objet": "la voiture",
    })


# ═══════════════════════════════════════════════════════════
# CRUD CLIENTS
# ═══════════════════════════════════════════════════════════

@login_required
def liste_clients(request):
    """
    Liste paginée des clients avec recherche textuelle.
    """
    query = request.GET.get("q", "")
    clients = Client.objects.all()

    if query:
        clients = clients.filter(
            models.Q(nom__icontains=query)
            | models.Q(prenom__icontains=query)
            | models.Q(cin__icontains=query)
            | models.Q(telephone__icontains=query)
        )

    paginator = Paginator(clients, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "core/clients.html", {
        "page_obj": page_obj,
        "query": query,
        "is_admin": est_admin(request.user),
    })


@login_required
def ajouter_client(request):
    """Ajouter un nouveau client. Accessible aux admins et employés."""
    if request.method == "POST":
        form = ClientForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Client ajouté avec succès.")
            return redirect("liste_clients")
    else:
        form = ClientForm()
    return render(request, "core/form_client.html", {
        "form": form,
        "titre": "Ajouter un client",
    })


@admin_required
def modifier_client(request, pk):
    """Modifier un client existant (admin uniquement)."""
    client = get_object_or_404(Client, pk=pk)
    if request.method == "POST":
        form = ClientForm(request.POST, instance=client)
        if form.is_valid():
            form.save()
            messages.success(request, "Client modifié avec succès.")
            return redirect("liste_clients")
    else:
        form = ClientForm(instance=client)
    return render(request, "core/form_client.html", {
        "form": form,
        "titre": "Modifier le client",
    })


@login_required
def detail_client(request, pk):
    """
    Affiche le détail d'un client et l'historique de ses réservations.
    """
    client = get_object_or_404(Client, pk=pk)
    reservations = Reservation.objects.filter(client=client).order_by("-date_creation")
    return render(request, "core/detail_client.html", {
        "client": client,
        "reservations": reservations,
    })


@admin_required
def supprimer_client(request, pk):
    """Supprimer un client (admin uniquement)."""
    client = get_object_or_404(Client, pk=pk)
    if request.method == "POST":
        client.delete()
        messages.success(request, "Client supprimé.")
        return redirect("liste_clients")
    return render(request, "core/confirmer_suppression.html", {
        "objet": client,
        "type_objet": "le client",
    })


# ═══════════════════════════════════════════════════════════
# CRUD RÉSERVATIONS (PARTIE ADMIN)
# ═══════════════════════════════════════════════════════════

@login_required
def liste_reservations(request):
    """
    Liste paginée de toutes les réservations avec filtre par statut.
    """
    statut_filter = request.GET.get("statut", "")
    reservations = Reservation.objects.all().order_by("-date_creation")

    if statut_filter:
        reservations = reservations.filter(statut=statut_filter)

    paginator = Paginator(reservations, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "core/reservations.html", {
        "page_obj": page_obj,
        "statut_filter": statut_filter,
        "statuts": Reservation.STATUT_CHOICES,
        "is_admin": est_admin(request.user),
    })


@login_required
def ajouter_reservation(request):
    """
    Créer une nouvelle demande de réservation (côté admin).
    La réservation est créée avec le statut 'en_attente'.
    Si le formulaire est invalide ou la validation métier échoue,
    le formulaire est ré-affiché avec les erreurs (pas de redirection).
    """
    if request.method == "POST":
        form = ReservationForm(request.POST)
        if form.is_valid():
            succes, resultat = _valider_et_creer_reservation(request, form)
            if succes:
                msg = (
                    f"Demande de réservation envoyée. "
                    f"Montant estimé : {resultat.montant_total} DH. "
                    f"En attente de validation."
                )
                return _reponse_action(request, True, msg, "liste_reservations")
            else:
                # Erreur métier : on ré-affiche le formulaire avec l'erreur
                messages.error(request, resultat["message"])
                return render(request, "core/form_reservation.html", {
                    "form": form,
                    "titre": "Nouvelle réservation",
                })
    else:
        form = ReservationForm()

    return render(request, "core/form_reservation.html", {
        "form": form,
        "titre": "Nouvelle réservation",
    })


@login_required
def detail_reservation(request, pk):
    """Affiche le détail d'une réservation avec ses paiements et son historique."""
    reservation = get_object_or_404(Reservation, pk=pk)
    paiements = reservation.paiements.all().order_by("-date_creation")
    historiques = reservation.historiques.all().order_by("-date_action")
    return render(request, "core/detail_reservation.html", {
        "reservation": reservation,
        "paiements": paiements,
        "historiques": historiques,
    })


@admin_required
def modifier_reservation(request, pk):
    """Modifier une réservation existante (admin uniquement)."""
    reservation = get_object_or_404(Reservation, pk=pk)
    if request.method == "POST":
        form = ReservationForm(request.POST, instance=reservation)
        if form.is_valid():
            form.save()
            messages.success(request, "Réservation modifiée.")
            return redirect("liste_reservations")
    else:
        form = ReservationForm(instance=reservation)
    return render(request, "core/form_reservation.html", {
        "form": form,
        "titre": "Modifier la réservation",
    })


@login_required
def annuler_reservation(request, pk):
    """
    Annuler une réservation (admin/employé).
    Passe le statut à 'annulee' et libère la voiture si aucune autre
    réservation en cours n'utilise cette voiture.
    """
    reservation = get_object_or_404(Reservation, pk=pk)

    # Affichage de la page de confirmation si GET classique
    if request.method == "GET" and not _est_requete_ajax(request):
        return render(request, "core/confirmer_suppression.html", {
            "objet": reservation,
            "type_objet": "la réservation",
            "action": "annuler",
        })

    # Vérification : la réservation doit être annulable
    if not _peut_annuler_reservation(reservation):
        return _reponse_action(
            request, False,
            "Cette réservation ne peut pas être annulée.",
            "liste_reservations",
        )

    # Mise à jour du statut
    reservation.statut = "annulee"
    reservation.save()
    enregistrer_historique(
        "annulation",
        f"Réservation #{reservation.pk} annulée par {request.user}",
        utilisateur=request.user,
        reservation=reservation,
    )
    # Notifier le client
    if reservation.client.user:
        creer_notification(
            reservation.client.user,
            "Réservation annulée",
            f"Votre réservation #{reservation.pk} pour {reservation.voiture} a été annulée par le personnel.",
            lien=f"/reservations/{reservation.pk}/",
        )

    # Libérer la voiture si aucune autre réservation en cours
    voiture = reservation.voiture
    if not Reservation.objects.filter(
        voiture=voiture, statut="en_cours"
    ).exists():
        voiture.statut = "disponible"
        voiture.save()

    return _reponse_action(
        request, True,
        "Réservation annulée.",
        "liste_reservations",
        new_statut="annulee",
        new_statut_display="Annulée",
        voiture_statut=voiture.statut,
        voiture_statut_display=voiture.get_statut_display(),
    )


@login_required
def terminer_reservation(request, pk):
    """
    Marquer une réservation comme terminée.
    La voiture redevient disponible.
    """
    reservation = get_object_or_404(Reservation, pk=pk)

    # Affichage du formulaire de clôture si GET classique
    if request.method == "GET" and not _est_requete_ajax(request):
        form = TerminerReservationForm(initial={"date_retour_reelle": date.today()})
        return render(request, "core/terminer_reservation.html", {
            "reservation": reservation,
            "form": form,
        })

    # Vérification : doit être en cours
    if not _peut_terminer_reservation(reservation):
        return _reponse_action(
            request, False,
            "Seule une réservation en cours peut être terminée.",
            "liste_reservations",
        )

    # Mise à jour avec le formulaire
    form = TerminerReservationForm(request.POST)
    if form.is_valid():
        reservation.statut = "terminee"
        reservation.date_retour_reelle = form.cleaned_data["date_retour_reelle"]
        reservation.remarque = form.cleaned_data.get("remarque", "")
        reservation.save()
        enregistrer_historique(
            "retour",
            f"Réservation #{reservation.pk} terminée — retour le {reservation.date_retour_reelle} "
            f"par {request.user}" + (f" — {reservation.remarque}" if reservation.remarque else ""),
            utilisateur=request.user,
            reservation=reservation,
        )
        # Notifier le client
        if reservation.client.user:
            creer_notification(
                reservation.client.user,
                "Réservation terminée",
                f"Votre réservation #{reservation.pk} pour {reservation.voiture} est terminée. "
                f"Retour enregistré le {reservation.date_retour_reelle}.",
                lien=f"/reservations/{reservation.pk}/",
            )
        voiture = reservation.voiture
        voiture.statut = "disponible"
        voiture.save()

        return _reponse_action(
            request, True,
            "Réservation terminée. La voiture est de nouveau disponible.",
            "liste_reservations",
            new_statut="terminee",
            new_statut_display="Terminée",
            voiture_statut="disponible",
            voiture_statut_display="Disponible",
        )
    else:
        return _reponse_action(
            request, False,
            "Formulaire invalide.",
            "liste_reservations",
        )


@login_required
def accepter_reservation(request, pk):
    """
    Accepter une demande de réservation en attente.
    Passe le statut à 'en_cours' et la voiture à 'louee'.
    Vérifie les conflits de période avant d'accepter.
    """
    reservation = get_object_or_404(Reservation, pk=pk)

    # Vérification : doit être en attente
    if not _peut_accepter_ou_refuser(reservation):
        return _reponse_action(
            request, False,
            "Cette demande n'est plus en attente.",
            "liste_reservations",
        )

    # Vérification conflit (double sécurité)
    conflit = Reservation.objects.filter(
        voiture=reservation.voiture,
        statut="en_cours",
        date_debut__lt=reservation.date_fin,
        date_fin__gt=reservation.date_debut,
    )
    if conflit.exists():
        return _reponse_action(
            request, False,
            "Conflit : la voiture est déjà louée sur cette période.",
            "liste_reservations",
        )

    # Acceptation
    reservation.statut = "en_cours"
    reservation.save()
    enregistrer_historique(
        "validation",
        f"Réservation #{reservation.pk} acceptée par {request.user} — {reservation.client}",
        utilisateur=request.user,
        reservation=reservation,
    )
    # Notifier le client
    if reservation.client.user:
        creer_notification(
            reservation.client.user,
            "Réservation acceptée",
            f"Votre réservation #{reservation.pk} pour {reservation.voiture} a été acceptée. "
            f"Elle est maintenant en cours.",
            lien=f"/reservations/{reservation.pk}/",
        )
    voiture = reservation.voiture
    voiture.statut = "louee"
    voiture.save()

    return _reponse_action(
        request, True,
        f"Demande de {reservation.client} acceptée.",
        "liste_reservations",
        new_statut="en_cours",
        new_statut_display="En cours",
        voiture_statut="louee",
        voiture_statut_display="Louee",
    )


@login_required
def refuser_reservation(request, pk):
    """
    Refuser une demande de réservation en attente.
    Passe le statut à 'annulee'.
    """
    reservation = get_object_or_404(Reservation, pk=pk)

    # Affichage de la page de confirmation si GET classique
    if request.method == "GET" and not _est_requete_ajax(request):
        return render(request, "core/confirmer_suppression.html", {
            "objet": reservation,
            "type_objet": "la demande",
            "action": "refuser",
        })

    # Vérification : doit être en attente
    if not _peut_accepter_ou_refuser(reservation):
        return _reponse_action(
            request, False,
            "Cette demande n'est plus en attente.",
            "liste_reservations",
        )

    reservation.statut = "annulee"
    reservation.save()
    enregistrer_historique(
        "refus",
        f"Réservation #{reservation.pk} refusée par {request.user} — {reservation.client}",
        utilisateur=request.user,
        reservation=reservation,
    )
    # Notifier le client
    if reservation.client.user:
        creer_notification(
            reservation.client.user,
            "Réservation refusée",
            f"Votre réservation #{reservation.pk} pour {reservation.voiture} a été refusée.",
            lien=f"/reservations/{reservation.pk}/",
        )

    return _reponse_action(
        request, True,
        f"Demande de {reservation.client} refusée.",
        "liste_reservations",
        new_statut="annulee",
        new_statut_display="Annulée",
    )


# ═══════════════════════════════════════════════════════════
# NOTIFICATIONS
# ═══════════════════════════════════════════════════════════

@login_required
def liste_notifications(request):
    """
    Page des notifications de l'utilisateur connecté.
    """
    notifications = request.user.notifications.all()
    nb_non_lues = notifications.filter(lu=False).count()

    paginator = Paginator(notifications, 20)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "core/notifications.html", {
        "page_obj": page_obj,
        "nb_non_lues": nb_non_lues,
    })


@login_required
def lire_notification(request, pk):
    """
    Marquer une notification comme lue et rediriger vers le lien.
    """
    notification = get_object_or_404(Notification, pk=pk, utilisateur=request.user)
    notification.lu = True
    notification.save()
    if notification.lien:
        return redirect(notification.lien)
    return redirect("liste_notifications")


@login_required
def tout_marquer_lu(request):
    """
    Marquer toutes les notifications comme lues.
    """
    request.user.notifications.filter(lu=False).update(lu=True)
    messages.success(request, "Toutes les notifications ont été marquées comme lues.")
    return redirect("liste_notifications")


# ═══════════════════════════════════════════════════════════
# HISTORIQUE
# ═══════════════════════════════════════════════════════════

@login_required
def historique(request):
    """
    Page d'historique : liste de toutes les actions enregistrées.
    Filtrable par type d'action.
    """
    action_filter = request.GET.get("action", "")
    historiques = Historique.objects.select_related("utilisateur", "reservation").all()

    if action_filter:
        historiques = historiques.filter(action=action_filter)

    paginator = Paginator(historiques, 20)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "core/historique.html", {
        "page_obj": page_obj,
        "action_filter": action_filter,
        "actions": Historique.ACTION_CHOICES,
    })


# ═══════════════════════════════════════════════════════════
# EXPORTS CSV
# ═══════════════════════════════════════════════════════════

@login_required
def export_voitures_csv(request):
    """Exporte la liste des voitures au format CSV."""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="voitures.csv"'
    writer = csv.writer(response)
    writer.writerow(['Marque', 'Modèle', 'Immatriculation', 'Année', 'Prix/jour', 'Statut'])
    for v in Voiture.objects.all():
        writer.writerow([
            v.marque, v.modele, v.immatriculation,
            v.annee, v.prix_jour, v.get_statut_display(),
        ])
    return response


@login_required
def export_clients_csv(request):
    """Exporte la liste des clients au format CSV."""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="clients.csv"'
    writer = csv.writer(response)
    writer.writerow(['Nom', 'Prénom', 'CIN', 'Téléphone', 'Email', 'Adresse'])
    for c in Client.objects.all():
        writer.writerow([
            c.nom, c.prenom, c.cin, c.telephone,
            c.email or '', c.adresse or '',
        ])
    return response


@login_required
def export_reservations_csv(request):
    """Exporte la liste des réservations au format CSV."""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="reservations.csv"'
    writer = csv.writer(response)
    writer.writerow(['Client', 'Voiture', 'Date début', 'Date fin', 'Montant', 'Statut'])
    for r in Reservation.objects.all():
        writer.writerow([
            f"{r.client.nom} {r.client.prenom}",
            f"{r.voiture.marque} {r.voiture.modele}",
            r.date_debut.strftime('%d/%m/%Y'),
            r.date_fin.strftime('%d/%m/%Y'),
            r.montant_total,
            r.get_statut_display(),
        ])
    return response


# ═══════════════════════════════════════════════════════════
# FACTURE PDF (par réservation)
# ═══════════════════════════════════════════════════════════

@login_required
def facture_pdf(request, pk):
    """
    Génère une facture PDF pour une réservation spécifique.
    Utilise la bibliothèque ReportLab.
    """
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import A4

    reservation = get_object_or_404(Reservation, pk=pk)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="facture_{reservation.pk}.pdf"'

    p = canvas.Canvas(response, pagesize=A4)
    p.setFont("Helvetica-Bold", 18)
    p.drawString(50, 800, f"FACTURE N° {reservation.pk}")

    p.setFont("Helvetica", 12)
    y = 760
    p.drawString(50, y, f"Client : {reservation.client.nom} {reservation.client.prenom}")
    y -= 20
    p.drawString(50, y, f"CIN : {reservation.client.cin}")
    y -= 20
    p.drawString(50, y, f"Téléphone : {reservation.client.telephone}")
    y -= 30
    p.drawString(50, y, (
        f"Voiture : {reservation.voiture.marque} {reservation.voiture.modele} "
        f"({reservation.voiture.immatriculation})"
    ))
    y -= 20
    p.drawString(50, y, (
        f"Du {reservation.date_debut.strftime('%d/%m/%Y')} "
        f"au {reservation.date_fin.strftime('%d/%m/%Y')}"
    ))
    y -= 20
    nb_jours = (reservation.date_fin - reservation.date_debut).days or 1
    p.drawString(50, y, f"Durée : {nb_jours} jour(s) x {reservation.voiture.prix_jour} DH/jour")
    y -= 30
    p.setFont("Helvetica-Bold", 14)
    p.drawString(50, y, f"MONTANT TOTAL : {reservation.montant_total} DH")

    p.showPage()
    p.save()
    return response


# ═══════════════════════════════════════════════════════════
# STATISTIQUES
# ═══════════════════════════════════════════════════════════

@login_required
def statistiques(request):
    """
    Page de statistiques détaillées :
    - CA total
    - Taux d'occupation du parc
    - Répartition des réservations par statut
    - CA mensuel (6 derniers mois)
    """
    terminees = Reservation.objects.filter(statut="terminee")
    ca_total = sum(r.montant_total for r in terminees)

    total_voitures = Voiture.objects.count()
    maintenance = Voiture.objects.filter(statut="maintenance").count()
    louees = Voiture.objects.filter(statut="louee").count()
    parc_actif = total_voitures - maintenance
    taux_occupation = round((louees / parc_actif * 100) if parc_actif > 0 else 0)

    repartition = {
        "en_attente": Reservation.objects.filter(statut="en_attente").count(),
        "en_cours": Reservation.objects.filter(statut="en_cours").count(),
        "terminee": terminees.count(),
        "annulee": Reservation.objects.filter(statut="annulee").count(),
    }

    ca_mensuel = _calculer_ca_mensuel()

    return render(request, "core/statistiques.html", {
        "ca_total": ca_total,
        "taux_occupation": taux_occupation,
        "repartition": repartition,
        "ca_mensuel": ca_mensuel,
    })


# ═══════════════════════════════════════════════════════════
# ESPACE CLIENT
# ═══════════════════════════════════════════════════════════

def client_register(request):
    """
    Inscription d'un nouveau client.
    Crée à la fois un compte User et un profil Client associé.
    """
    if request.method == "POST":
        form = ClientRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(
                request,
                "Compte créé avec succès. Bienvenue dans votre espace client."
            )
            return redirect("client_dashboard")
    else:
        form = ClientRegistrationForm()
    return render(request, "core/client_register.html", {"form": form})


@login_required
def client_voitures(request):
    """
    Liste des voitures visibles par le client.
    Affiche seulement les voitures disponibles et louées (pas en maintenance).
    Présenté en cartes avec images.
    """
    try:
        client = request.user.client
    except Client.DoesNotExist:
        messages.error(request, "Vous n'avez pas de profil client.")
        logout(request)
        return redirect("login")

    query = request.GET.get("q", "")
    categorie_filter = request.GET.get("categorie", "")
    voitures = Voiture.objects.filter(statut__in=["disponible", "louee"])

    if query:
        voitures = voitures.filter(
            models.Q(marque__icontains=query)
            | models.Q(modele__icontains=query)
            | models.Q(immatriculation__icontains=query)
        )

    if categorie_filter:
        voitures = voitures.filter(categorie_id=categorie_filter)

    paginator = Paginator(voitures, 9)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "core/client_voitures.html", {
        "page_obj": page_obj,
        "query": query,
        "categories": Categorie.objects.all(),
        "categorie_filter": categorie_filter,
        "client": client,
    })


@login_required
def client_detail_voiture(request, pk):
    """Détail d'une voiture côté client (infos + bouton réserver)."""
    try:
        client = request.user.client
    except Client.DoesNotExist:
        messages.error(request, "Vous n'avez pas de profil client.")
        logout(request)
        return redirect("login")

    voiture = get_object_or_404(Voiture, pk=pk)
    return render(request, "core/client_detail_voiture.html", {
        "voiture": voiture,
        "client": client,
    })


@login_required
def client_dashboard(request):
    """
    Espace personnel du client : historique des réservations,
    compteurs par statut, actions disponibles.
    """
    # Vérifier que l'utilisateur a bien un profil client
    try:
        client = request.user.client
    except Client.DoesNotExist:
        messages.error(request, "Vous n'avez pas de profil client.")
        logout(request)
        return redirect("login")

    reservations = Reservation.objects.filter(client=client).order_by("-date_creation")
    en_cours = reservations.filter(statut="en_cours")
    en_attente = reservations.filter(statut="en_attente")
    terminees = reservations.filter(statut="terminee")
    total_depense = sum(r.montant_total for r in terminees)

    paginator = Paginator(reservations, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "core/client_dashboard.html", {
        "client": client,
        "page_obj": page_obj,
        "en_cours_count": en_cours.count(),
        "en_attente_count": en_attente.count(),
        "terminees_count": terminees.count(),
        "total_depense": total_depense,
    })


@login_required
def client_creer_reservation(request):
    """
    Permet à un client connecté de créer une demande de réservation.
    Le client est automatiquement associé (pas de choix dans le formulaire).
    """
    # Vérifier le profil client
    try:
        client = request.user.client
    except Client.DoesNotExist:
        return _reponse_action(
            request, False,
            "Vous n'avez pas de profil client.",
            "login",
        )

    if request.method == "POST":
        form = ClientReservationForm(request.POST)
        if form.is_valid():
            succes, resultat = _valider_et_creer_reservation(
                request, form, client_impose=client
            )
            if succes:
                msg = (
                    f"Demande de réservation envoyée. "
                    f"Montant estimé : {resultat.montant_total} DH. "
                    f"En attente de validation."
                )
                return _reponse_action(request, True, msg, "client_dashboard")
            else:
                # Erreur métier
                if _est_requete_ajax(request):
                    return JsonResponse({
                        "status": "error",
                        "message": resultat["message"],
                    })
                # Ré-afficher le formulaire avec l'erreur
                messages.error(request, resultat["message"])
                return render(request, "core/client_form_reservation.html", {
                    "form": form,
                    "titre": "Nouvelle demande de réservation",
                })
        else:
            # Formulaire invalide (erreurs de validation Django)
            if _est_requete_ajax(request):
                errors = ", ".join(
                    [f"{k}: {v[0]}" for k, v in form.errors.items()]
                )
                return JsonResponse({
                    "status": "error",
                    "message": f"Formulaire invalide: {errors}",
                })
    else:
        form = ClientReservationForm()

    return render(request, "core/client_form_reservation.html", {
        "form": form,
        "titre": "Nouvelle demande de réservation",
    })


@login_required
def client_annuler_demande(request, pk):
    """
    Permet à un client d'annuler sa propre demande de réservation
    (uniquement si elle est encore 'en_attente').
    """
    reservation = get_object_or_404(Reservation, pk=pk)

    # Vérifier que le client est bien le propriétaire
    if request.user.client != reservation.client:
        return _reponse_action(
            request, False,
            "Action non autorisée.",
            "client_dashboard",
        )

    # Vérifier que la demande est encore annulable
    if reservation.statut != "en_attente":
        return _reponse_action(
            request, False,
            "Cette demande ne peut plus être annulée.",
            "client_dashboard",
        )

    reservation.statut = "annulee"
    reservation.save()
    enregistrer_historique(
        "annulation",
        f"Réservation #{reservation.pk} annulée par le client {reservation.client}",
        utilisateur=request.user,
        reservation=reservation,
    )
    # Notifier les admins
    for admin_user in User.objects.filter(is_superuser=True).exclude(pk=request.user.pk):
        creer_notification(
            admin_user,
            "Réservation annulée par le client",
            f"{reservation.client} a annulé sa réservation #{reservation.pk} pour {reservation.voiture}.",
            lien=f"/reservations/{reservation.pk}/",
        )

    return _reponse_action(
        request, True,
        "Votre demande de réservation a été annulée.",
        "client_dashboard",
        new_statut="annulee",
        new_statut_display="Annulée",
    )


@login_required
def verifier_disponibilite_voiture(request):
    """
    Endpoint AJAX : vérifie en temps réel si une voiture est disponible
    pour une période donnée et retourne le montant estimé.
    """
    voiture_id = request.GET.get("voiture")
    date_debut_str = request.GET.get("date_debut")
    date_fin_str = request.GET.get("date_fin")

    if not voiture_id or not date_debut_str or not date_fin_str:
        return JsonResponse({
            "available": False,
            "message": "Sélectionnez un véhicule et des dates valides.",
        })

    try:
        voiture = Voiture.objects.get(pk=voiture_id)
        date_debut = date.fromisoformat(date_debut_str)
        date_fin = date.fromisoformat(date_fin_str)
    except (Voiture.DoesNotExist, ValueError):
        return JsonResponse({
            "available": False,
            "message": "Données invalides.",
        })

    if date_fin <= date_debut:
        return JsonResponse({
            "available": False,
            "message": "La date de fin doit être après la date de début.",
        })

    if voiture.statut == "maintenance":
        return JsonResponse({
            "available": False,
            "message": "Cette voiture est en maintenance, elle ne peut pas être louée.",
        })

    conflit = Reservation.objects.filter(
        voiture=voiture,
        statut__in=["en_attente", "en_cours"],
        date_debut__lt=date_fin,
        date_fin__gt=date_debut,
    )
    if conflit.exists():
        return JsonResponse({
            "available": False,
            "message": "Cette voiture n'est pas disponible sur cette période.",
        })

    nombre_jours = (date_fin - date_debut).days or 1
    montant_total = nombre_jours * voiture.prix_jour

    return JsonResponse({
        "available": True,
        "message": f"Véhicule disponible. Montant estimé : {montant_total} DH.",
        "montant": float(montant_total),
    })


# ═══════════════════════════════════════════════════════════
# GESTION DES RÔLES (RBAC)
# ═══════════════════════════════════════════════════════════

@admin_required
def gestion_roles(request):
    """
    Gestion des utilisateurs du personnel (RBAC).
    Permet de créer, modifier le rôle et supprimer des comptes staff.
    Seuls les admins peuvent y accéder.

    On filtre les utilisateurs staff mais on exclut ceux qui ont un profil client
    (ce sont des clients, pas du personnel).
    """
    # Récupérer seulement les utilisateurs du personnel (staff)
    # On exclut les utilisateurs qui ont un profil client associé
    users = (
        User.objects
        .filter(is_staff=True)
        .exclude(client__isnull=False)  # pas de profil client = membre du personnel
        .order_by("username")
    )
    groupes = Group.objects.all()

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "change_role":
            # Modifier le rôle d'un utilisateur existant
            user_id = request.POST.get("user_id")
            groupe_nom = request.POST.get("groupe")
            utilisateur = get_object_or_404(User, pk=user_id)
            utilisateur.groups.clear()
            if groupe_nom:
                groupe = Group.objects.get(name=groupe_nom)
                utilisateur.groups.add(groupe)
            messages.success(
                request,
                f"Rôle de {utilisateur.username} mis à jour → {groupe_nom or 'Aucun'}"
            )

        elif action == "add_user":
            # Créer un nouvel utilisateur staff
            username = request.POST.get("new_username", "").strip()
            password = request.POST.get("new_password", "")
            groupe_nom = request.POST.get("new_groupe", "")

            if not username or not password:
                messages.error(request, "Nom d'utilisateur et mot de passe obligatoires.")
            elif User.objects.filter(username=username).exists():
                messages.error(request, f"L'utilisateur '{username}' existe déjà.")
            else:
                user = User.objects.create_user(
                    username=username,
                    password=password,
                    is_staff=True,
                )
                if groupe_nom:
                    groupe = Group.objects.get(name=groupe_nom)
                    user.groups.add(groupe)
                messages.success(
                    request,
                    f"Utilisateur '{username}' créé avec le rôle {groupe_nom or 'Aucun'}."
                )

        elif action == "delete_user":
            # Supprimer un utilisateur (sauf le superuser)
            user_id = request.POST.get("user_id")
            utilisateur = get_object_or_404(User, pk=user_id)
            if utilisateur.is_superuser:
                messages.error(request, "Impossible de supprimer le superutilisateur.")
            else:
                username = utilisateur.username
                utilisateur.delete()
                messages.success(request, f"Utilisateur '{username}' supprimé.")

        return redirect("gestion_roles")

    # Préparer les données pour le template
    users_data = []
    for u in users:
        g = u.groups.first()
        users_data.append({
            "user": u,
            "groupe": g.name if g else "Aucun",
        })

    return render(request, "core/gestion_roles.html", {
        "users_data": users_data,
        "groupes": groupes,
    })


# ═══════════════════════════════════════════════════════════
# HANDLERS D'ERREUR
# ═══════════════════════════════════════════════════════════

def handler404(request, exception=None):
    """Page d'erreur 404 personnalisée."""
    return render(request, "core/404.html", status=404)


def handler500(request):
    """Page d'erreur 500 personnalisée."""
    return render(request, "core/500.html", status=500)


# ═══════════════════════════════════════════════════════════
# RAPPORT PDF GLOBAL
# ═══════════════════════════════════════════════════════════

@login_required
def rapport_pdf(request):
    """
    Génère un rapport PDF global avec :
    - Résumé (véhicules, clients, CA)
    - Top 5 véhicules
    - Top 5 clients
    - CA mensuel (6 derniers mois)
    """
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import A4

    terminees = Reservation.objects.filter(statut="terminee")
    ca_total = sum(r.montant_total for r in terminees)
    total_voitures = Voiture.objects.count()
    total_clients = Client.objects.count()

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="rapport.pdf"'

    p = canvas.Canvas(response, pagesize=A4)
    y = 800

    # Titre
    p.setFont("Helvetica-Bold", 20)
    p.drawString(50, y, "RAPPORT — Location de Voitures")
    y -= 10
    p.setFont("Helvetica", 10)
    p.drawString(50, y, f"Généré le {date.today().strftime('%d/%m/%Y')}")
    y -= 30

    # Résumé
    p.setFont("Helvetica-Bold", 14)
    p.drawString(50, y, "Résumé")
    y -= 20
    p.setFont("Helvetica", 12)
    p.drawString(
        50, y,
        f"Véhicules : {total_voitures}  |  Clients : {total_clients}  |  CA total : {ca_total} DH"
    )
    y -= 30

    # Top 5 véhicules
    p.setFont("Helvetica-Bold", 14)
    p.drawString(50, y, "Top 5 véhicules les plus loués")
    y -= 20
    p.setFont("Helvetica", 12)
    top_voitures = (
        terminees
        .values("voiture__marque", "voiture__modele")
        .annotate(nb=Count("id"))
        .order_by("-nb")[:5]
    )
    for v in top_voitures:
        p.drawString(
            50, y,
            f"  • {v['voiture__marque']} {v['voiture__modele']} — {v['nb']} location(s)"
        )
        y -= 18
    y -= 15

    # Top 5 clients
    p.setFont("Helvetica-Bold", 14)
    p.drawString(50, y, "Top 5 clients")
    y -= 20
    p.setFont("Helvetica", 12)
    top_clients = (
        terminees
        .values("client__nom", "client__prenom")
        .annotate(nb=Count("id"), total=Sum("montant_total"))
        .order_by("-total")[:5]
    )
    for c in top_clients:
        p.drawString(
            50, y,
            f"  • {c['client__nom']} {c['client__prenom']} — "
            f"{c['nb']} loc. — {c['total']} DH"
        )
        y -= 18
    y -= 15

    # CA mensuel (réutilisation du helper)
    p.setFont("Helvetica-Bold", 14)
    p.drawString(50, y, "CA mensuel (6 derniers mois)")
    y -= 20
    p.setFont("Helvetica", 12)
    for mois_data in _calculer_ca_mensuel():
        p.drawString(50, y, f"  {mois_data['mois']} : {mois_data['ca']} DH")
        y -= 18

    p.showPage()
    p.save()
    return response
