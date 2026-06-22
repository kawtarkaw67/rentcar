# Localisation des fonctions importantes

Cette fiche aide a retrouver rapidement les parties importantes du projet pendant la soutenance.

## Commandes utiles

| Besoin | Commande |
| --- | --- |
| Demarrer le projet | Double-cliquer sur `demarrer_projet.bat` |
| Demarrer manuellement | `python manage.py runserver 127.0.0.1:8000` |
| Verifier Django | `python manage.py check` |
| Appliquer les migrations | `python manage.py migrate` |
| Charger les donnees de test | `python manage.py seed_data` |
| Lancer les tests Django | `python manage.py test core -v2` |

## Structure generale

| Partie | Fichier | Role |
| --- | --- | --- |
| Configuration Django | `location_voiture/settings.py` | Base de donnees SQLite, langue, timezone, apps, fichiers media/static |
| Routes principales projet | `location_voiture/urls.py` | Inclut les routes de `core` et l'administration Django |
| Routes de l'application | `core/urls.py` | Liste toutes les URL: dashboard, voitures, clients, reservations, client, PDF, CSV |
| Modeles metier | `core/models.py` | Structure des donnees et relations |
| Formulaires | `core/forms.py` | Validation et champs des formulaires |
| Logique metier / vues | `core/views.py` | Traitement des pages, actions, PDF, CSV, roles |
| Templates HTML | `core/templates/core/` | Pages affichees dans le navigateur |
| Donnees de demonstration | `core/management/commands/seed_data.py` | Cree les utilisateurs et exemples de test |

## Modeles importants

| Fonctionnalite | Emplacement | Explication |
| --- | --- | --- |
| Categories de voitures | `core/models.py:12` | Modele `Categorie`, pour classer les voitures |
| Voitures | `core/models.py:29` | Modele `Voiture`, avec marque, modele, prix, statut, image et categorie |
| Clients | `core/models.py:73` | Modele `Client`, lie optionnellement au compte Django `User` |
| Reservations | `core/models.py:98` | Modele `Reservation`, relie un client a une voiture et gere les dates/statuts |
| Calcul du montant | `core/models.py:123` | Methode `calculer_montant`, calcule jours x prix journalier |
| Recalcul automatique | `core/models.py:130` | Methode `save`, met a jour `montant_total` avant sauvegarde |
| Paiements | `core/models.py:146` | Modele `Paiement`, montant, date, mode et statut |
| Historique | `core/models.py:173` | Journal des actions importantes |
| Notifications | `core/models.py:204` | Notifications persistantes pour les utilisateurs |

## Formulaires

| Formulaire | Emplacement | Utilisation |
| --- | --- | --- |
| `CategorieForm` | `core/forms.py:12` | Ajouter ou modifier une categorie |
| `VoitureForm` | `core/forms.py:21` | Ajouter ou modifier une voiture |
| `ClientForm` | `core/forms.py:31` | Ajouter ou modifier un client |
| `ReservationForm` | `core/forms.py:41` | Reservation cote admin/employe |
| `ClientReservationForm` | `core/forms.py:56` | Reservation cote client |
| `ClientRegistrationForm` | `core/forms.py:71` | Inscription client avec creation du compte `User` |
| `PaiementForm` | `core/forms.py:119` | Enregistrer ou modifier un paiement |
| `TerminerReservationForm` | `core/forms.py:132` | Cloturer une reservation avec date de retour |
| `ProfilForm` | `core/forms.py:148` | Modifier le profil utilisateur/client |

## Vues et logique metier

| Fonctionnalite | Emplacement | Explication |
| --- | --- | --- |
| Detection AJAX | `core/views.py:36` | Reconnait une requete AJAX |
| Historique | `core/views.py:47` | `enregistrer_historique`, garde une trace des actions |
| Notifications | `core/views.py:60` | `creer_notification`, cree une notification utilisateur |
| Reponse action | `core/views.py:73` | Retourne une reponse normale ou JSON selon le contexte |
| Creation reservation centralisee | `core/views.py:98` | Valide les dates, verifie la voiture et cree la reservation |
| Chiffre d'affaires mensuel | `core/views.py:166` | Calcule le CA par mois pour les statistiques |
| Droits d'annulation | `core/views.py:203` | Verifie si une reservation peut etre annulee |
| Droits de terminaison | `core/views.py:208` | Verifie si une reservation peut etre terminee |
| Droits acceptation/refus | `core/views.py:213` | Verifie si une reservation peut etre acceptee/refusee |
| Verification admin | `core/views.py:222` | Teste si l'utilisateur appartient au groupe Admin |
| Verification client | `core/views.py:232` | Teste si l'utilisateur est un client |

## Pages principales

| Page / Action | Emplacement | URL principale |
| --- | --- | --- |
| Accueil | `core/views.py:432` | `/` |
| Connexion | `core/views.py:457` | `/login/` |
| Deconnexion | `core/views.py:478` | `/logout/` |
| Profil | `core/views.py:485` | `/profil/` |
| Dashboard staff | `core/views.py:528` | `/dashboard/` |
| Statistiques | `core/views.py:1319` | `/statistiques/` |
| Gestion des roles | `core/views.py:1645` | `/roles/` |
| Rapport PDF | `core/views.py:1752` | `/rapport/pdf/` |

## Gestion des voitures

| Action | Emplacement | URL |
| --- | --- | --- |
| Liste voitures | `core/views.py:605` | `/voitures/` |
| Ajouter voiture | `core/views.py:648` | `/voitures/ajouter/` |
| Modifier voiture | `core/views.py:665` | `/voitures/<id>/modifier/` |
| Detail voiture | `core/views.py:683` | `/voitures/<id>/` |
| Supprimer voiture | `core/views.py:696` | `/voitures/<id>/supprimer/` |
| Export CSV voitures | `core/views.py:1216` | `/voitures/export/` |

## Gestion des clients

| Action | Emplacement | URL |
| --- | --- | --- |
| Liste clients | `core/views.py:714` | `/clients/` |
| Ajouter client | `core/views.py:741` | `/clients/ajouter/` |
| Modifier client | `core/views.py:758` | `/clients/<id>/modifier/` |
| Detail client | `core/views.py:776` | `/clients/<id>/` |
| Supprimer client | `core/views.py:789` | `/clients/<id>/supprimer/` |
| Export CSV clients | `core/views.py:1231` | `/clients/export/` |

## Cycle de reservation

| Action | Emplacement | URL |
| --- | --- | --- |
| Liste reservations | `core/views.py:807` | `/reservations/` |
| Ajouter reservation staff | `core/views.py:830` | `/reservations/ajouter/` |
| Detail reservation | `core/views.py:865` | `/reservations/<id>/` |
| Modifier reservation | `core/views.py:878` | `/reservations/<id>/modifier/` |
| Annuler reservation | `core/views.py:896` | `/reservations/<id>/annuler/` |
| Terminer reservation | `core/views.py:958` | `/reservations/<id>/terminer/` |
| Accepter reservation | `core/views.py:1026` | `/reservations/<id>/accepter/` |
| Refuser reservation | `core/views.py:1090` | `/reservations/<id>/refuser/` |
| Export CSV reservations | `core/views.py:1246` | `/reservations/export/` |
| Facture PDF | `core/views.py:1269` | `/reservations/<id>/facture/` |

## Paiements

| Action | Emplacement | URL |
| --- | --- | --- |
| Liste paiements | `core/views.py:319` | `/paiements/` |
| Detail paiement | `core/views.py:351` | `/paiements/<id>/` |
| Ajouter paiement | `core/views.py:360` | `/paiements/ajouter/` ou `/reservations/<id>/paiement/` |
| Modifier paiement | `core/views.py:409` | `/paiements/<id>/modifier/` |

## Espace client

| Action | Emplacement | URL |
| --- | --- | --- |
| Inscription client | `core/views.py:1357` | `/client/register/` |
| Catalogue client | `core/views.py:1378` | `/client/voitures/` |
| Detail voiture cote client | `core/views.py:1419` | `/client/voitures/<id>/` |
| Dashboard client | `core/views.py:1436` | `/client/dashboard/` |
| Creer demande de reservation | `core/views.py:1470` | `/client/reserver/` |
| Annuler demande client | `core/views.py:1531` | `/reservations/<id>/client-annuler/` |
| Verifier disponibilite | `core/views.py:1581` | `/client/verifier-voiture/` |

## Notifications, historique et erreurs

| Fonctionnalite | Emplacement | URL |
| --- | --- | --- |
| Liste notifications | `core/views.py:1144` | `/notifications/` |
| Lire une notification | `core/views.py:1162` | `/notifications/<id>/lire/` |
| Tout marquer comme lu | `core/views.py:1175` | `/notifications/tout-lire/` |
| Historique | `core/views.py:1189` | `/historique/` |
| Compteur notifications | `core/templatetags/notifications_tags.py:7` | Utilise dans les templates |
| Page 404 | `core/views.py:1737` | Handler erreur 404 |
| Page 500 | `core/views.py:1742` | Handler erreur 500 |

## Templates importants

| Template | Role |
| --- | --- |
| `core/templates/core/base.html` | Layout principal, navigation, messages |
| `core/templates/core/accueil.html` | Page d'accueil |
| `core/templates/core/login.html` | Connexion |
| `core/templates/core/dashboard.html` | Dashboard staff |
| `core/templates/core/voitures.html` | Liste des voitures |
| `core/templates/core/clients.html` | Liste des clients |
| `core/templates/core/reservations.html` | Liste des reservations |
| `core/templates/core/detail_reservation.html` | Detail d'une reservation |
| `core/templates/core/client_dashboard.html` | Espace client |
| `core/templates/core/client_voitures.html` | Catalogue client |
| `core/templates/core/statistiques.html` | Statistiques |
| `core/templates/core/gestion_roles.html` | Gestion des roles |
| `core/templates/core/notifications.html` | Notifications |
| `core/templates/core/historique.html` | Historique des actions |

## Donnees de test

| Element | Emplacement | Role |
| --- | --- | --- |
| Commande `seed_data` | `core/management/commands/seed_data.py:7` | Cree les comptes et donnees de demonstration |
| Identifiants | `IDENTIFIANTS.md` | Liste les comptes de test |
| README | `README.md` | Explication globale du projet et installation |

## Phrase utile en soutenance

Si le jury demande ou se trouve une fonctionnalite, il faut repondre avec la logique Django:

1. L'URL est definie dans `core/urls.py`.
2. La fonction qui traite la demande est dans `core/views.py`.
3. Les donnees sont structurees dans `core/models.py`.
4. Le formulaire est dans `core/forms.py` si l'utilisateur saisit des informations.
5. L'affichage final est dans `core/templates/core/`.
