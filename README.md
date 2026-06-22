# Location de Voitures — Application de gestion

Application web de gestion de location de voitures pour une agence de taille moyenne. Développée avec Django 6, SQLite et Bootstrap 5.

## Stack technique

| Élément       | Technologie            |
|---------------|------------------------|
| Backend       | Django 6.0.5 (Python)  |
| Base de données | SQLite                |
| Frontend      | Django Templates + Bootstrap 5 |
| PDF           | ReportLab              |
| Auth          | Django auth (groupes Admin/Employé) |

## Schéma de la base de données

```
┌─────────────────┐     ┌─────────────────┐     ┌──────────────────────────┐
│     Voiture     │     │     Client      │     │       Reservation        │
├─────────────────┤     ├─────────────────┤     ├──────────────────────────┤
│ id (PK)         │     │ id (PK)         │     │ id (PK)                  │
│ marque          │     │ user (FK→User)  │     │ client (FK→Client)       │
│ modele          │     │ nom             │     │ voiture (FK→Voiture)     │
│ immatriculation │     │ prenom          │     │ date_debut               │
│ annee           │     │ cin (unique)    │     │ date_fin                 │
│ prix_jour       │     │ telephone       │     │ montant_total            │
│ statut          │     │ email           │     │ statut                   │
│ (disponible,    │     │ adresse         │     │ (en_attente, en_cours,   │
│  louee,         │     └─────────────────┘     │  terminee, annulee)      │
│  maintenance)   │                             │ date_creation            │
└─────────────────┘                             └──────────────────────────┘
```

## Fonctionnalités

### Espace personnel (Admin / Employé)
- **Dashboard** : statistiques en temps réel, demandes en attente, CA, meilleurs clients
- **Gestion des voitures** : CRUD, filtres par statut, recherche, export CSV
- **Gestion des clients** : CRUD, recherche, export CSV
- **Gestion des réservations** : cycle de vie complet (demande → acceptation → en cours → terminée)
- **Factures PDF** : génération pour les réservations terminées
- **Statistiques** : CA mensuel, taux d'occupation, répartition par statut
- **Rapport PDF** : rapport complet multi-pages
- **RBAC** : gestion des utilisateurs (Admin/Employé) avec interface dédiée
- **Exports CSV** : voitures, clients, réservations
- **Pagination** : 10 éléments par page sur toutes les listes

### Espace client
- **Inscription** avec création de compte
- **Demandes de réservation** : création, annulation avant validation
- **Historique** : toutes les réservations, statuts, montants
- **Factures PDF** : téléchargement des factures

### Rôles

| Rôle      | Permissions                                                    |
|-----------|----------------------------------------------------------------|
| Admin     | Tout (CRUD complet, gestion rôles, statistiques, suppression)  |
| Employé   | Dashboard, listes, réservations (accepter/refuser/terminer)    |
| Client    | Demandes de réservation, historique, factures                  |

## Prérequis

- Python 3.10 ou supérieur
- pip

## Installation

```bash
# 1. Cloner le dépôt
git clone <url-du-repo>
cd pfaKawtar

# 2. Créer un environnement virtuel
python -m venv venv
venv\Scripts\activate     # Windows
source venv/bin/activate   # Linux/Mac

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Appliquer les migrations
python manage.py migrate

# 5. Créer un superutilisateur
python manage.py createsuperuser

# 6. Charger les données de test (optionnel)
python manage.py seed_data

# 7. Lancer le serveur
python manage.py runserver
```

Accéder à http://127.0.0.1:8000/

## Identifiants de test

Après avoir exécuté `python manage.py seed_data` :

| Rôle    | Nom d'utilisateur | Mot de passe  |
|---------|-------------------|---------------|
| Admin   | `admin`           | `admin1234`   |
| Employé | `employe`         | `employe1234` |
| Client  | `ahmed`           | `client1234`  |
| Client  | `fatima`          | `client1234`  |
| Client  | `youssef`         | `client1234`  |
| Client  | `samira`          | `client1234`  |
| Client  | `karim`           | `client1234`  |

## Lancer les tests

```bash
python manage.py test core -v2
```

## Structure du projet

```
pfaKawtar/
├── core/                       # Application principale
│   ├── templates/core/         # Templates HTML
│   │   ├── base.html           # Layout principal
│   │   ├── dashboard.html      # Dashboard staff
│   │   ├── accueil.html        # Page d'accueil publique
│   │   ├── login.html          # Page de connexion
│   │   ├── voitures.html       # Liste des voitures
│   │   ├── clients.html        # Liste des clients
│   │   ├── reservations.html   # Liste des réservations
│   │   ├── client_dashboard.html # Espace client
│   │   ├── statistiques.html   # Statistiques
│   │   ├── gestion_roles.html  # Gestion des rôles
│   │   ├── pagination.html     # Include pagination
│   │   ├── 404.html / 500.html # Pages d'erreur
│   │   └── ...
│   ├── models.py               # Modèles Voiture, Client, Reservation
│   ├── views.py                # Vues (dashboard, CRUD, exports, PDF)
│   ├── urls.py                 # Routes de l'application
│   ├── forms.py                # Formulaires
│   ├── tests.py                # Tests unitaires
│   └── management/commands/    # Commandes custom
├── location_voiture/           # Projet Django
│   ├── settings.py
│   └── urls.py
├── docs/                       # Documentation
├── plans/                      # Plans d'exécution
├── requirements.txt            # Dépendances Python
├── IDENTIFIANTS.md             # Identifiants de test
└── README.md
```
