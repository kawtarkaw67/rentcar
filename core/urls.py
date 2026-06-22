from django.urls import path
from . import views

urlpatterns = [
    path("", views.accueil, name="accueil"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("profil/", views.modifier_profil, name="modifier_profil"),

    # Réinitialisation de mot de passe
    path("password-reset/", views.password_reset_view, name="password_reset"),
    path("password-reset/envoye/", views.password_reset_done_view, name="password_reset_done"),
    path("password-reset/<uidb64>/<token>/", views.password_reset_confirm_view, name="password_reset_confirm"),
    path("password-reset/termine/", views.password_reset_complete_view, name="password_reset_complete"),

    # Catégories
    path("categories/", views.liste_categories, name="liste_categories"),
    path("categories/ajouter/", views.ajouter_categorie, name="ajouter_categorie"),
    path("categories/<int:pk>/modifier/", views.modifier_categorie, name="modifier_categorie"),
    path("categories/<int:pk>/supprimer/", views.supprimer_categorie, name="supprimer_categorie"),

    # Voitures
    path("voitures/", views.liste_voitures, name="liste_voitures"),
    path("voitures/ajouter/", views.ajouter_voiture, name="ajouter_voiture"),
    path("voitures/<int:pk>/", views.detail_voiture, name="detail_voiture"),
    path("voitures/<int:pk>/modifier/", views.modifier_voiture, name="modifier_voiture"),
    path("voitures/<int:pk>/supprimer/", views.supprimer_voiture, name="supprimer_voiture"),
    path("voitures/export/", views.export_voitures_csv, name="export_voitures_csv"),

    # Clients
    path("clients/", views.liste_clients, name="liste_clients"),
    path("clients/ajouter/", views.ajouter_client, name="ajouter_client"),
    path("clients/<int:pk>/", views.detail_client, name="detail_client"),
    path("clients/<int:pk>/modifier/", views.modifier_client, name="modifier_client"),
    path("clients/<int:pk>/supprimer/", views.supprimer_client, name="supprimer_client"),
    path("clients/export/", views.export_clients_csv, name="export_clients_csv"),

    # Réservations
    path("reservations/", views.liste_reservations, name="liste_reservations"),
    path("reservations/ajouter/", views.ajouter_reservation, name="ajouter_reservation"),
    path("reservations/<int:pk>/modifier/", views.modifier_reservation, name="modifier_reservation"),
    path("reservations/<int:pk>/accepter/", views.accepter_reservation, name="accepter_reservation"),
    path("reservations/<int:pk>/refuser/", views.refuser_reservation, name="refuser_reservation"),
    path("reservations/<int:pk>/annuler/", views.annuler_reservation, name="annuler_reservation"),
    path("reservations/<int:pk>/terminer/", views.terminer_reservation, name="terminer_reservation"),
    path("reservations/<int:pk>/", views.detail_reservation, name="detail_reservation"),
    path("reservations/<int:pk>/facture/", views.facture_pdf, name="facture_pdf"),
    path("reservations/<int:reservation_pk>/paiement/", views.ajouter_paiement, name="ajouter_paiement_reservation"),
    path("reservations/export/", views.export_reservations_csv, name="export_reservations_csv"),

    # Paiements
    path("paiements/", views.liste_paiements, name="liste_paiements"),
    path("paiements/ajouter/", views.ajouter_paiement, name="ajouter_paiement"),
    path("paiements/<int:pk>/", views.detail_paiement, name="detail_paiement"),
    path("paiements/<int:pk>/modifier/", views.modifier_paiement, name="modifier_paiement"),

    # Espace client
    path("client/register/", views.client_register, name="client_register"),
    path("client/dashboard/", views.client_dashboard, name="client_dashboard"),
    path("client/reserver/", views.client_creer_reservation, name="client_creer_reservation"),
    path("client/verifier-voiture/", views.verifier_disponibilite_voiture, name="verifier_disponibilite_voiture"),
    path("client/voitures/", views.client_voitures, name="client_voitures"),
    path("client/voitures/<int:pk>/", views.client_detail_voiture, name="client_detail_voiture"),

    path("reservations/<int:pk>/client-annuler/", views.client_annuler_demande, name="client_annuler_demande"),

    # Gestion rôles (RBAC)
    path("roles/", views.gestion_roles, name="gestion_roles"),

    # Statistiques
    path("statistiques/", views.statistiques, name="statistiques"),

    # Historique
    path("historique/", views.historique, name="historique"),

    # Notifications
    path("notifications/", views.liste_notifications, name="liste_notifications"),
    path("notifications/<int:pk>/lire/", views.lire_notification, name="lire_notification"),
    path("notifications/tout-lire/", views.tout_marquer_lu, name="tout_marquer_lu"),

    # Rapport PDF
    path("rapport/pdf/", views.rapport_pdf, name="rapport_pdf"),
]
