# Questions possibles du jury - PFA Location de voitures

Cette fiche sert a reviser vite avant la soutenance. Les reponses sont formulees pour l'oral: courtes, claires et faciles a adapter.

## Presentation generale

### 1. Quel est l'objectif de votre projet ?

L'objectif est de developper une application web pour gerer une agence de location de voitures. Elle permet de gerer les voitures, les clients, les reservations, les paiements, les factures, les statistiques et un espace client.

### 2. Quel probleme le projet resout-il ?

Il remplace une gestion manuelle ou dispersee par une application centralisee. L'agence peut suivre les voitures disponibles, les demandes de reservation, les retours, les paiements et l'historique des actions.

### 3. Quels sont les principaux utilisateurs ?

Il y a trois types d'utilisateurs: l'administrateur, l'employe et le client. L'administrateur a tous les droits, l'employe gere surtout les operations quotidiennes, et le client peut consulter les voitures et faire des demandes de reservation.

## Choix techniques

### 4. Pourquoi avoir choisi Django ?

Django est adapte aux applications web de gestion. Il fournit deja l'authentification, l'administration, l'ORM, les formulaires, les vues, la securite de base et la gestion des templates. Cela permet de construire plus vite une application fiable.

### 5. Pourquoi utiliser SQLite ?

SQLite est simple a installer, ne demande pas de serveur separe et convient bien pour un projet academique ou une demonstration locale. Pour une version de production, on pourrait migrer vers PostgreSQL ou MySQL.

### 6. Quelle architecture utilisez-vous ?

Le projet suit l'architecture MVT de Django: Model, View, Template. Les modeles definissent les donnees, les vues contiennent la logique de traitement, et les templates affichent les pages HTML.

### 7. Pourquoi Bootstrap ?

Bootstrap permet d'avoir une interface propre et responsive rapidement. Il apporte des composants prets a l'emploi comme les tableaux, les formulaires, les boutons et les alertes.

## Base de donnees et modeles

### 8. Quels sont les modeles principaux ?

Les modeles principaux sont `Voiture`, `Client`, `Reservation`, `Paiement`, `Categorie`, `Historique` et `Notification`.

### 9. Comment calculez-vous le montant d'une reservation ?

Le montant est calcule automatiquement dans le modele `Reservation`: nombre de jours multiplie par le prix journalier de la voiture. Un minimum d'un jour est applique.

### 10. Pourquoi avoir separe Client et User ?

`User` sert a l'authentification Django: identifiant, mot de passe et groupes. `Client` contient les informations metier: CIN, telephone, adresse et lien avec les reservations.

### 11. Comment evitez-vous les doublons ?

Certains champs sont uniques, par exemple l'immatriculation d'une voiture et le CIN d'un client. Les formulaires valident aussi les donnees avant l'enregistrement.

## Authentification et roles

### 12. Comment fonctionne l'authentification ?

L'application utilise le systeme d'authentification de Django. Les utilisateurs se connectent avec un nom d'utilisateur et un mot de passe, puis Django gere la session.

### 13. Comment gerez-vous les roles ?

Les roles sont geres avec les groupes Django: Admin, Employe et Client. Certaines vues verifient le role avant d'autoriser une action.

### 14. Quelle est la difference entre Admin et Employe ?

L'administrateur a un acces complet, y compris la suppression et la gestion des roles. L'employe peut gerer les operations courantes comme les reservations, les voitures et les clients, mais avec moins de droits sensibles.

### 15. Que peut faire un client ?

Un client peut s'inscrire, se connecter, consulter les voitures disponibles, creer une demande de reservation, suivre son historique et telecharger une facture si la reservation est terminee.

## Cycle de reservation

### 16. Quel est le cycle de vie d'une reservation ?

Une reservation commence en general avec le statut `en_attente`. Elle peut ensuite etre acceptee et passer `en_cours`, puis etre terminee au retour du vehicule. Elle peut aussi etre annulee ou refusee.

### 17. Que se passe-t-il quand une reservation est acceptee ?

La reservation passe en cours et la voiture devient louee. L'action est enregistree dans l'historique et une notification peut etre creee.

### 18. Que se passe-t-il quand une reservation est terminee ?

On enregistre la date reelle de retour, la voiture redevient disponible, la reservation passe a l'etat terminee et la facture peut etre generee.

### 19. Comment le client sait-il si une voiture est disponible ?

Le client peut consulter le catalogue des voitures. Il existe aussi une verification de disponibilite cote client pour aider a choisir une voiture et des dates.

## Paiements, PDF et exports

### 20. Comment gerez-vous les paiements ?

Un paiement est associe a une reservation. Il contient le montant, la date, le mode de paiement et le statut du paiement.

### 21. Comment generez-vous les factures PDF ?

Les factures sont generees cote serveur avec ReportLab. La vue recupere les informations de la reservation, du client, de la voiture et du paiement, puis retourne un fichier PDF.

### 22. Pourquoi proposer des exports CSV ?

Les exports CSV permettent de recuperer les donnees dans Excel ou un autre outil. C'est utile pour l'administration, les rapports et l'archivage.

### 23. Que contient le rapport PDF ?

Le rapport PDF donne une vue globale de l'activite: statistiques, reservations, voitures, clients et indicateurs importants.

## Statistiques et tableau de bord

### 24. Quels indicateurs affiche le dashboard ?

Le dashboard affiche des informations utiles comme le nombre de voitures, les reservations, les demandes en attente, le chiffre d'affaires et des indicateurs d'activite.

### 25. Comment calculez-vous le chiffre d'affaires ?

Le chiffre d'affaires est calcule a partir des reservations et des montants associes, surtout les reservations terminees ou payees selon l'indicateur affiche.

### 26. Pourquoi avoir ajoute des statistiques ?

Les statistiques aident l'agence a prendre des decisions: savoir quelles voitures sont utilisees, suivre le revenu, identifier les demandes en attente et evaluer l'activite.

## Securite et qualite

### 27. Quelles mesures de securite sont presentes ?

Le projet utilise l'authentification Django, les protections CSRF, les sessions, les permissions par role, la validation des formulaires et l'ORM pour eviter les requetes SQL manuelles.

### 28. Est-ce que le projet est pret pour la production ?

Pour une production reelle, il faudrait renforcer la configuration: mettre `DEBUG=False`, utiliser une vraie base comme PostgreSQL, configurer un serveur web, securiser les variables d'environnement et mettre en place des sauvegardes.

### 29. Comment avez-vous teste l'application ?

Il y a des tests Django pour les modeles, les formulaires, les vues, les roles, les exports et plusieurs cas limites. Il existe aussi des tests end-to-end avec Playwright pour simuler des parcours utilisateur.

### 30. Que faites-vous si une erreur arrive pendant la demonstration ?

Le script de demarrage garde la fenetre ouverte en cas d'erreur. Cela permet de lire le message, corriger rapidement et relancer le projet.

## Questions pieges

### 31. Pourquoi ne pas avoir utilise une API REST ?

Pour ce projet, l'objectif principal etait une application web complete avec pages serveur. Django Templates etait suffisant. Une API REST pourrait etre ajoutee plus tard pour une application mobile ou un frontend separe.

### 32. Pourquoi ne pas avoir utilise React ?

React est utile pour des interfaces tres dynamiques. Ici, l'application est surtout une application de gestion avec formulaires, tableaux et actions serveur. Django Templates permet de livrer une solution plus simple et coherente.

### 33. Est-ce que SQLite peut gerer beaucoup d'utilisateurs ?

SQLite convient pour une demonstration, un prototype ou une petite utilisation locale. Pour beaucoup d'utilisateurs simultanes, il faut migrer vers PostgreSQL ou MySQL.

### 34. Que se passe-t-il si deux clients reservent la meme voiture ?

Le projet verifie la disponibilite et le statut de la voiture dans le flux de reservation. Pour une version production tres concurrente, on ajouterait des verrous transactionnels plus stricts cote base de donnees.

### 35. Quelle est la partie la plus importante du code ?

La partie la plus importante est le cycle de reservation dans `core/views.py`, car il relie les clients, les voitures, les statuts, l'historique, les notifications et les factures.

### 36. Quelle amelioration ajouteriez-vous en premier ?

J'ajouterais une base PostgreSQL, une meilleure verification de disponibilite sur les dates, un deploiement en ligne et des notifications par email reelles.

## Mini conclusion a dire a l'oral

Ce projet m'a permis de realiser une application web complete avec Django, depuis l'analyse du besoin jusqu'a la gestion des donnees, des roles, des reservations, des paiements et des documents PDF. Il peut servir de base pour une vraie agence apres quelques adaptations de production.
