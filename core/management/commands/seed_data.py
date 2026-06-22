from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group
from core.models import Voiture, Client, Reservation, Categorie
from datetime import date, timedelta


class Command(BaseCommand):
    help = "Ajoute des données de test pour la démonstration"

    def handle(self, *args, **options):
        # Créer les groupes
        admin_group, _ = Group.objects.get_or_create(name="Admin")
        employe_group, _ = Group.objects.get_or_create(name="Employé")
        self.stdout.write(f"  Groupes: Admin, Employé")

        # Ajouter l'admin existant au groupe Admin
        for username in ("admin", "employe"):
            user = User.objects.filter(username=username).first()
            if user:
                user.groups.add(admin_group if username == "admin" else employe_group)
                user.save()
        self.stdout.write("  Utilisateurs admin/employe mis à jour")

        # Créer un compte employé si pas encore là
        employe, created = User.objects.get_or_create(username="employe", is_staff=True)
        if created:
            employe.set_password("employe1234")
            employe.save()
            employe.groups.add(employe_group)
            self.stdout.write("  Compte employé créé (employe / employe1234)")

        # Catégories
        categories_data = [
            {"nom": "Berline", "description": "Voitures compactes et berlines familiales"},
            {"nom": "SUV", "description": "Véhicules tout-terrain et crossover"},
            {"nom": "Utilitaire", "description": "Véhicules de transport de marchandises"},
        ]
        categories = []
        for c in categories_data:
            obj, created = Categorie.objects.get_or_create(nom=c["nom"], defaults=c)
            categories.append(obj)
            if created:
                self.stdout.write(f"  Catégorie: {obj}")
        self.stdout.write(self.style.SUCCESS(f"{len(categories)} catégories prêtes"))

        # Voitures
        voitures_data = [
            {"marque": "Renault", "modele": "Clio", "immatriculation": "AB-123-CD", "annee": 2022, "prix_jour": 300, "statut": "disponible", "categorie": categories[0]},
            {"marque": "Dacia", "modele": "Duster", "immatriculation": "AB-456-EF", "annee": 2023, "prix_jour": 500, "statut": "disponible", "categorie": categories[1]},
            {"marque": "Peugeot", "modele": "208", "immatriculation": "AB-789-GH", "annee": 2021, "prix_jour": 350, "statut": "disponible", "categorie": categories[0]},
            {"marque": "Toyota", "modele": "Corolla", "immatriculation": "AB-012-IJ", "annee": 2024, "prix_jour": 600, "statut": "disponible", "categorie": categories[0]},
            {"marque": "Citroën", "modele": "C3", "immatriculation": "AB-345-KL", "annee": 2020, "prix_jour": 250, "statut": "maintenance", "categorie": categories[0]},
        ]

        voitures = []
        for v in voitures_data:
            obj, created = Voiture.objects.get_or_create(immatriculation=v["immatriculation"], defaults=v)
            voitures.append(obj)
            if created:
                self.stdout.write(f"  Voiture: {obj}")
        self.stdout.write(self.style.SUCCESS(f"{len(voitures)} voitures prêtes"))

        # Clients avec comptes utilisateurs
        clients_users = [
            {"username": "ahmed", "password": "client1234", "nom": "El Amrani", "prenom": "Ahmed", "cin": "AB12345", "telephone": "0612345678", "email": "ahmed@example.com"},
            {"username": "fatima", "password": "client1234", "nom": "Benali", "prenom": "Fatima", "cin": "CD67890", "telephone": "0623456789", "email": ""},
            {"username": "youssef", "password": "client1234", "nom": "Ouazzani", "prenom": "Youssef", "cin": "EF12345", "telephone": "0634567890", "email": ""},
            {"username": "samira", "password": "client1234", "nom": "Idrissi", "prenom": "Samira", "cin": "GH67890", "telephone": "0645678901", "email": ""},
            {"username": "karim", "password": "client1234", "nom": "Tazi", "prenom": "Karim", "cin": "IJ12345", "telephone": "0656789012", "email": ""},
        ]

        clients = []
        for c in clients_users:
            user, created = User.objects.get_or_create(username=c["username"])
            if created:
                user.set_password(c["password"])
                user.email = c["email"]
                user.save()
            client, created = Client.objects.get_or_create(
                cin=c["cin"],
                defaults={
                    "user": user,
                    "nom": c["nom"],
                    "prenom": c["prenom"],
                    "telephone": c["telephone"],
                    "email": c["email"],
                }
            )
            if not client.user:
                client.user = user
                client.save()
            clients.append(client)
            self.stdout.write(f"  Client: {client} (compte: {user.username})")
        self.stdout.write(self.style.SUCCESS(f"{len(clients)} clients prêts (avec comptes)"))

        # Réservations
        aujourdhui = date.today()

        reservations_data = [
            {"client": clients[0], "voiture": voitures[0], "date_debut": aujourdhui - timedelta(days=2), "date_fin": aujourdhui + timedelta(days=2)},
            {"client": clients[1], "voiture": voitures[1], "date_debut": aujourdhui, "date_fin": aujourdhui + timedelta(days=3)},
            {"client": clients[2], "voiture": voitures[2], "date_debut": aujourdhui - timedelta(days=5), "date_fin": aujourdhui - timedelta(days=1), "statut": "terminee"},
        ]

        for r in reservations_data:
            statut = r.pop("statut", "en_cours")
            res = Reservation.objects.create(**r)
            res.statut = statut
            res.save()
            if statut == "en_cours":
                res.voiture.statut = "louee"
                res.voiture.save()
            self.stdout.write(f"  Réservation: {res} ({res.montant_total} DH)")

        self.stdout.write(self.style.SUCCESS("\nDonnées de test ajoutées avec succès !"))
        self.stdout.write(f"\n  Voitures: {Voiture.objects.count()} | Clients: {Client.objects.count()} | Réservations: {Reservation.objects.count()}")
        self.stdout.write(f"\n  Comptes:")
        self.stdout.write(f"    Admin      : admin    / admin1234")
        self.stdout.write(f"    Employé    : employe  / employe1234")
        self.stdout.write(f"    Clients (tous) : client1234")
        for c in clients_users:
            self.stdout.write(f"      {c['username']}")
