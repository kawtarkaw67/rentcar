from django.test import TestCase, Client as TestClient
from django.contrib.auth.models import User, Group
from django.urls import reverse
from datetime import date, timedelta
from .models import Voiture, Client, Reservation, Categorie, Paiement, Historique, Notification
from .views import enregistrer_historique, creer_notification


class VoitureModelTests(TestCase):
    def setUp(self):
        self.voiture = Voiture.objects.create(
            marque="Renault",
            modele="Clio",
            immatriculation="XX-123-YY",
            annee=2022,
            prix_jour=300,
            statut="disponible",
        )

    def test_str_voiture(self):
        self.assertEqual(str(self.voiture), "Renault Clio - XX-123-YY")

    def test_statut_defaut(self):
        v = Voiture.objects.create(
            marque="Peugeot", modele="208", immatriculation="ZZ-999-AA", annee=2020, prix_jour=250
        )
        self.assertEqual(v.statut, "disponible")

    def test_immatriculation_unique(self):
        with self.assertRaises(Exception):
            Voiture.objects.create(
                marque="Double", modele="Copie", immatriculation="XX-123-YY", annee=2021, prix_jour=200
            )

    def test_prix_jour_negatif_accepte_car_pas_de_validateur(self):
        v = Voiture.objects.create(
            marque="Test", modele="Test", immatriculation="NEG-001-XX", annee=2022, prix_jour=-100
        )
        self.assertEqual(v.prix_jour, -100)

    def test_annee_future_acceptee(self):
        v = Voiture.objects.create(
            marque="Future", modele="Next", immatriculation="FUT-999-ZZ", annee=2030, prix_jour=500
        )
        self.assertEqual(v.annee, 2030)


class ClientModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testclient", password="test1234")
        self.client_obj = Client.objects.create(
            user=self.user,
            nom="El Amrani",
            prenom="Ahmed",
            cin="AB12345",
            telephone="0612345678",
        )

    def test_str_client(self):
        self.assertEqual(str(self.client_obj), "El Amrani Ahmed")

    def test_cin_unique(self):
        with self.assertRaises(Exception):
            Client.objects.create(
                nom="Autre", prenom="Personne", cin="AB12345", telephone="0600000000"
            )

    def test_liaison_user(self):
        self.assertEqual(self.client_obj.user.username, "testclient")

    def test_client_sans_user(self):
        c = Client.objects.create(
            nom="Sans", prenom="Compte", cin="NUSER01", telephone="0600000000"
        )
        self.assertIsNone(c.user)

    def test_client_email_optionnel(self):
        c = Client.objects.create(
            nom="No", prenom="Email", cin="NOEML01", telephone="0600000000"
        )
        self.assertIsNone(c.email)


class ReservationModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="cliresa", password="test1234")
        self.client = Client.objects.create(
            user=self.user, nom="Benali", prenom="Fatima", cin="CD67890", telephone="0623456789"
        )
        self.voiture = Voiture.objects.create(
            marque="Dacia", modele="Duster", immatriculation="AB-456-EF", annee=2023, prix_jour=500,
        )

    def test_calcul_montant(self):
        r = Reservation.objects.create(
            client=self.client,
            voiture=self.voiture,
            date_debut=date.today(),
            date_fin=date.today() + timedelta(days=3),
        )
        self.assertEqual(r.montant_total, 1500)

    def test_montant_minimum_1_jour(self):
        r = Reservation.objects.create(
            client=self.client,
            voiture=self.voiture,
            date_debut=date.today(),
            date_fin=date.today(),
        )
        self.assertEqual(r.montant_total, 500)

    def test_statut_defaut_en_attente(self):
        r = Reservation.objects.create(
            client=self.client,
            voiture=self.voiture,
            date_debut=date.today(),
            date_fin=date.today() + timedelta(days=2),
        )
        self.assertEqual(r.statut, "en_attente")

    def test_date_creation_auto(self):
        r = Reservation.objects.create(
            client=self.client,
            voiture=self.voiture,
            date_debut=date.today(),
            date_fin=date.today() + timedelta(days=1),
        )
        self.assertIsNotNone(r.date_creation)


# ---------- VIEWS ----------

class BaseAuthMixin:
    def _login_as(self, username, password):
        self.client.login(username=username, password=password)


class AuthViewTests(TestCase, BaseAuthMixin):
    def setUp(self):
        Group.objects.get_or_create(name="Admin")
        Group.objects.get_or_create(name="Employé")
        self.admin_user = User.objects.create_user(username="admin", password="admin1234", is_staff=True)
        admin_g = Group.objects.get(name="Admin")
        self.admin_user.groups.add(admin_g)

        self.client_user = User.objects.create_user(username="ahmed", password="client1234")
        Client.objects.create(
            user=self.client_user, nom="El Amrani", prenom="Ahmed", cin="AB12345", telephone="0612345678"
        )

    def test_login_redirect_admin(self):
        response = self.client.post(reverse("login"), {"username": "admin", "password": "admin1234"})
        self.assertRedirects(response, reverse("dashboard"))

    def test_login_redirect_client(self):
        response = self.client.post(reverse("login"), {"username": "ahmed", "password": "client1234"})
        self.assertRedirects(response, reverse("client_dashboard"))

    def test_login_mauvais_identifiants(self):
        response = self.client.post(reverse("login"), {"username": "admin", "password": "faux"})
        self.assertEqual(response.status_code, 200)

    def test_acces_dashboard_sans_login(self):
        response = self.client.get(reverse("dashboard"))
        self.assertEqual(response.status_code, 302)


class VoitureViewTests(TestCase, BaseAuthMixin):
    def setUp(self):
        admin_g, _ = Group.objects.get_or_create(name="Admin")
        self.user = User.objects.create_user(username="staff", password="staff1234", is_staff=True)
        self.user.groups.add(admin_g)
        self.voiture = Voiture.objects.create(
            marque="Renault", modele="Clio", immatriculation="XX-123-YY", annee=2022, prix_jour=300,
        )

    def test_liste_voitures_auth(self):
        self._login_as("staff", "staff1234")
        response = self.client.get(reverse("liste_voitures"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Clio")

    def test_ajouter_voiture(self):
        self._login_as("staff", "staff1234")
        response = self.client.post(reverse("ajouter_voiture"), {
            "marque": "Peugeot", "modele": "208", "immatriculation": "ZZ-999-AA",
            "annee": 2021, "prix_jour": 350, "statut": "disponible",
        })
        self.assertRedirects(response, reverse("liste_voitures"))
        self.assertEqual(Voiture.objects.count(), 2)

    def test_modifier_voiture(self):
        self._login_as("staff", "staff1234")
        response = self.client.post(reverse("modifier_voiture", args=[self.voiture.pk]), {
            "marque": "Renault", "modele": "Clio GT", "immatriculation": "XX-123-YY",
            "annee": 2022, "prix_jour": 350, "statut": "disponible",
        })
        self.assertRedirects(response, reverse("liste_voitures"))
        self.voiture.refresh_from_db()
        self.assertEqual(self.voiture.modele, "Clio GT")

    def test_supprimer_voiture(self):
        self._login_as("staff", "staff1234")
        response = self.client.post(reverse("supprimer_voiture", args=[self.voiture.pk]))
        self.assertRedirects(response, reverse("liste_voitures"))
        self.assertEqual(Voiture.objects.count(), 0)

    def test_detail_voiture(self):
        self._login_as("staff", "staff1234")
        response = self.client.get(reverse("detail_voiture", args=[self.voiture.pk]))
        self.assertEqual(response.status_code, 200)


class ReservationViewTests(TestCase, BaseAuthMixin):
    def setUp(self):
        Group.objects.get_or_create(name="Admin")
        self.user = User.objects.create_user(username="staff", password="staff1234", is_staff=True)
        admin_g = Group.objects.get(name="Admin")
        self.user.groups.add(admin_g)

        self.client_user = User.objects.create_user(username="ahmed", password="client1234")
        self.client_obj = Client.objects.create(
            user=self.client_user, nom="El Amrani", prenom="Ahmed", cin="AB12345", telephone="0612345678"
        )
        self.voiture = Voiture.objects.create(
            marque="Dacia", modele="Duster", immatriculation="AB-456-EF", annee=2023, prix_jour=500,
        )

    def test_creer_demande_en_attente(self):
        self._login_as("staff", "staff1234")
        response = self.client.post(reverse("ajouter_reservation"), {
            "client": self.client_obj.pk,
            "voiture": self.voiture.pk,
            "date_debut": (date.today() + timedelta(days=1)).isoformat(),
            "date_fin": (date.today() + timedelta(days=4)).isoformat(),
        })
        self.assertRedirects(response, reverse("liste_reservations"))
        r = Reservation.objects.first()
        self.assertEqual(r.statut, "en_attente")
        self.voiture.refresh_from_db()
        self.assertEqual(self.voiture.statut, "disponible")

    def test_accepter_reservation(self):
        r = Reservation.objects.create(
            client=self.client_obj, voiture=self.voiture,
            date_debut=date.today() + timedelta(days=1),
            date_fin=date.today() + timedelta(days=4),
            statut="en_attente",
        )
        self._login_as("staff", "staff1234")
        response = self.client.get(reverse("accepter_reservation", args=[r.pk]))
        r.refresh_from_db()
        self.voiture.refresh_from_db()
        self.assertEqual(r.statut, "en_cours")
        self.assertEqual(self.voiture.statut, "louee")
        self.assertRedirects(response, reverse("liste_reservations"))

    def test_refuser_reservation(self):
        r = Reservation.objects.create(
            client=self.client_obj, voiture=self.voiture,
            date_debut=date.today() + timedelta(days=1),
            date_fin=date.today() + timedelta(days=4),
            statut="en_attente",
        )
        self._login_as("staff", "staff1234")
        response = self.client.post(reverse("refuser_reservation", args=[r.pk]))
        r.refresh_from_db()
        self.assertEqual(r.statut, "annulee")
        self.assertRedirects(response, reverse("liste_reservations"))

    def test_conflit_double_reservation_rejeté(self):
        Reservation.objects.create(
            client=self.client_obj, voiture=self.voiture,
            date_debut=date.today() + timedelta(days=2),
            date_fin=date.today() + timedelta(days=5),
            statut="en_attente",
        )
        self._login_as("staff", "staff1234")
        response = self.client.post(reverse("ajouter_reservation"), {
            "client": self.client_obj.pk,
            "voiture": self.voiture.pk,
            "date_debut": (date.today() + timedelta(days=3)).isoformat(),
            "date_fin": (date.today() + timedelta(days=6)).isoformat(),
        })
        self.assertEqual(Reservation.objects.count(), 1)

    def test_terminer_reservation(self):
        r = Reservation.objects.create(
            client=self.client_obj, voiture=self.voiture,
            date_debut=date.today(), date_fin=date.today() + timedelta(days=2),
            statut="en_cours",
        )
        self.voiture.statut = "louee"
        self.voiture.save()
        self._login_as("staff", "staff1234")
        response = self.client.post(reverse("terminer_reservation", args=[r.pk]), {
            "date_retour_reelle": date.today().isoformat(),
            "remarque": "",
        })
        r.refresh_from_db()
        self.voiture.refresh_from_db()
        self.assertEqual(r.statut, "terminee")
        self.assertEqual(self.voiture.statut, "disponible")


class ClientRegistrationTests(TestCase):
    def test_inscription_creer_client_et_user(self):
        response = self.client.post(reverse("client_register"), {
            "username": "nouveau",
            "nom": "Test",
            "prenom": "User",
            "cin": "XX99999",
            "telephone": "0600000000",
            "email": "test@example.com",
            "password1": "ComplexPass123!",
            "password2": "ComplexPass123!",
        })
        self.assertRedirects(response, reverse("client_dashboard"))
        user = User.objects.get(username="nouveau")
        self.assertTrue(hasattr(user, "client"))
        self.assertEqual(user.client.cin, "XX99999")


class ClientDashboardTests(TestCase, BaseAuthMixin):
    def setUp(self):
        self.user = User.objects.create_user(username="ahmed", password="client1234")
        self.client_obj = Client.objects.create(
            user=self.user, nom="El Amrani", prenom="Ahmed", cin="AB12345", telephone="0612345678"
        )
        self.voiture = Voiture.objects.create(
            marque="Dacia", modele="Duster", immatriculation="AB-456-EF", annee=2023, prix_jour=500,
        )

    def test_dashboard_client_affiche_reservations(self):
        Reservation.objects.create(
            client=self.client_obj, voiture=self.voiture,
            date_debut=date.today(), date_fin=date.today() + timedelta(days=2),
            statut="en_cours",
        )
        self._login_as("ahmed", "client1234")
        response = self.client.get(reverse("client_dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Duster")


class ClientReservationViewTests(TestCase, BaseAuthMixin):
    def setUp(self):
        self.user = User.objects.create_user(username="ahmed", password="client1234")
        self.client_obj = Client.objects.create(
            user=self.user, nom="El Amrani", prenom="Ahmed", cin="AB12345", telephone="0612345678"
        )
        self.voiture = Voiture.objects.create(
            marque="Dacia", modele="Duster", immatriculation="AB-456-EF", annee=2023, prix_jour=500,
        )

    def test_client_creer_reservation_form_render(self):
        self._login_as("ahmed", "client1234")
        response = self.client.get(reverse("client_creer_reservation"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Duster")

    def test_client_creer_reservation_success(self):
        self._login_as("ahmed", "client1234")
        response = self.client.post(reverse("client_creer_reservation"), {
            "voiture": self.voiture.pk,
            "date_debut": (date.today() + timedelta(days=1)).isoformat(),
            "date_fin": (date.today() + timedelta(days=4)).isoformat(),
        })
        self.assertRedirects(response, reverse("client_dashboard"))
        r = Reservation.objects.first()
        self.assertIsNotNone(r)
        self.assertEqual(r.client, self.client_obj)
        self.assertEqual(r.voiture, self.voiture)
        self.assertEqual(r.statut, "en_attente")

    def test_client_creer_reservation_date_invalide(self):
        self._login_as("ahmed", "client1234")
        response = self.client.post(reverse("client_creer_reservation"), {
            "voiture": self.voiture.pk,
            "date_debut": (date.today() + timedelta(days=4)).isoformat(),
            "date_fin": (date.today() + timedelta(days=1)).isoformat(),
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Reservation.objects.count(), 0)

    def test_client_creer_reservation_maintenance(self):
        self.voiture.statut = "maintenance"
        self.voiture.save()
        self._login_as("ahmed", "client1234")
        response = self.client.post(reverse("client_creer_reservation"), {
            "voiture": self.voiture.pk,
            "date_debut": (date.today() + timedelta(days=1)).isoformat(),
            "date_fin": (date.today() + timedelta(days=4)).isoformat(),
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Reservation.objects.count(), 0)

    def test_client_creer_reservation_conflit(self):
        Reservation.objects.create(
            client=self.client_obj, voiture=self.voiture,
            date_debut=date.today() + timedelta(days=2),
            date_fin=date.today() + timedelta(days=5),
            statut="en_cours",
        )
        self._login_as("ahmed", "client1234")
        response = self.client.post(reverse("client_creer_reservation"), {
            "voiture": self.voiture.pk,
            "date_debut": (date.today() + timedelta(days=3)).isoformat(),
            "date_fin": (date.today() + timedelta(days=6)).isoformat(),
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Reservation.objects.count(), 1)


class CSVExportTests(TestCase, BaseAuthMixin):
    def setUp(self):
        self.user = User.objects.create_user(username="staff", password="staff1234", is_staff=True)
        self.voiture = Voiture.objects.create(
            marque="Renault", modele="Clio", immatriculation="XX-123-YY", annee=2022, prix_jour=300,
        )
        self._login_as("staff", "staff1234")

    def test_export_voitures_csv(self):
        response = self.client.get(reverse("export_voitures_csv"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "text/csv")
        content = response.content.decode()
        self.assertIn("Renault", content)
        self.assertIn("Clio", content)

    def test_export_reservations_csv(self):
        response = self.client.get(reverse("export_reservations_csv"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "text/csv")


class RBACTests(TestCase, BaseAuthMixin):
    def setUp(self):
        Group.objects.get_or_create(name="Admin")
        Group.objects.get_or_create(name="Employé")
        self.admin = User.objects.create_user(username="boss", password="boss1234", is_staff=True, is_superuser=True)
        admin_g = Group.objects.get(name="Admin")
        self.admin.groups.add(admin_g)

        self.employe = User.objects.create_user(username="emp1", password="emp1234", is_staff=True)
        emp_g = Group.objects.get(name="Employé")
        self.employe.groups.add(emp_g)

        self.client_user = User.objects.create_user(username="ahmed", password="client1234")
        Client.objects.create(
            user=self.client_user, nom="El Amrani", prenom="Ahmed", cin="AB12345", telephone="0612345678"
        )

    def test_admin_acces_roles(self):
        self._login_as("boss", "boss1234")
        response = self.client.get(reverse("gestion_roles"))
        self.assertEqual(response.status_code, 200)

    def test_employe_bloque_roles(self):
        self._login_as("emp1", "emp1234")
        response = self.client.get(reverse("gestion_roles"))
        self.assertEqual(response.status_code, 302)

    def test_ajouter_utilisateur(self):
        self._login_as("boss", "boss1234")
        response = self.client.post(reverse("gestion_roles"), {
            "action": "add_user",
            "new_username": "nouveau",
            "new_password": "pass1234",
            "new_groupe": "Employé",
        })
        self.assertRedirects(response, reverse("gestion_roles"))
        user = User.objects.get(username="nouveau")
        self.assertTrue(user.is_staff)
        self.assertEqual(user.groups.first().name, "Employé")

    def test_changer_role(self):
        self._login_as("boss", "boss1234")
        response = self.client.post(reverse("gestion_roles"), {
            "action": "change_role",
            "user_id": self.employe.pk,
            "groupe": "Admin",
        })
        self.assertRedirects(response, reverse("gestion_roles"))
        self.employe.refresh_from_db()
        self.assertEqual(self.employe.groups.first().name, "Admin")

    def test_supprimer_utilisateur(self):
        new_user = User.objects.create_user(username="todelete", password="pass1234", is_staff=True)
        self._login_as("boss", "boss1234")
        response = self.client.post(reverse("gestion_roles"), {
            "action": "delete_user",
            "user_id": new_user.pk,
        })
        self.assertRedirects(response, reverse("gestion_roles"))
        self.assertFalse(User.objects.filter(username="todelete").exists())

    def test_bloque_supprimer_superuser(self):
        self._login_as("boss", "boss1234")
        response = self.client.post(reverse("gestion_roles"), {
            "action": "delete_user",
            "user_id": self.admin.pk,
        })
        self.assertRedirects(response, reverse("gestion_roles"))
        self.assertTrue(User.objects.filter(username="boss").exists())


class AccueilTests(TestCase):
    def test_page_accueil_publique(self):
        response = self.client.get(reverse("accueil"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Location Auto")

    def test_redirection_si_connecte(self):
        user = User.objects.create_user(username="staff", password="staff1234", is_staff=True)
        self.client.login(username="staff", password="staff1234")
        response = self.client.get(reverse("accueil"))
        self.assertRedirects(response, reverse("dashboard"))


class ClientAnnulationTests(TestCase, BaseAuthMixin):
    def setUp(self):
        self.user = User.objects.create_user(username="ahmed", password="client1234")
        self.client_obj = Client.objects.create(
            user=self.user, nom="El Amrani", prenom="Ahmed", cin="AB12345", telephone="0612345678"
        )
        self.autre_user = User.objects.create_user(username="fatima", password="client1234")
        self.autre_client = Client.objects.create(
            user=self.autre_user, nom="Benali", prenom="Fatima", cin="CD67890", telephone="0623456789"
        )
        self.voiture = Voiture.objects.create(
            marque="Dacia", modele="Duster", immatriculation="AB-456-EF", annee=2023, prix_jour=500,
        )

    def test_client_annule_sa_demande(self):
        r = Reservation.objects.create(
            client=self.client_obj, voiture=self.voiture,
            date_debut=date.today() + timedelta(days=1),
            date_fin=date.today() + timedelta(days=4),
            statut="en_attente",
        )
        self._login_as("ahmed", "client1234")
        response = self.client.get(reverse("client_annuler_demande", args=[r.pk]))
        r.refresh_from_db()
        self.assertEqual(r.statut, "annulee")
        self.assertRedirects(response, reverse("client_dashboard"))

    def test_client_ne_peut_pas_annuler_demande_autre(self):
        r = Reservation.objects.create(
            client=self.autre_client, voiture=self.voiture,
            date_debut=date.today() + timedelta(days=1),
            date_fin=date.today() + timedelta(days=4),
            statut="en_attente",
        )
        self._login_as("ahmed", "client1234")
        response = self.client.get(reverse("client_annuler_demande", args=[r.pk]))
        r.refresh_from_db()
        self.assertEqual(r.statut, "en_attente")
        self.assertRedirects(response, reverse("client_dashboard"))


class PaginationTests(TestCase, BaseAuthMixin):
    def setUp(self):
        admin_g, _ = Group.objects.get_or_create(name="Admin")
        self.user = User.objects.create_user(username="staff", password="staff1234", is_staff=True)
        self.user.groups.add(admin_g)
        for i in range(15):
            Voiture.objects.create(
                marque=f"Marque{i}", modele=f"Modele{i}",
                immatriculation=f"XX-{i:03d}-YY", annee=2020, prix_jour=300,
            )

    def test_pagination_voitures(self):
        self._login_as("staff", "staff1234")
        response = self.client.get(reverse("liste_voitures"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Page 1")


class StatistiquesTests(TestCase, BaseAuthMixin):
    def setUp(self):
        admin_g, _ = Group.objects.get_or_create(name="Admin")
        employe_g, _ = Group.objects.get_or_create(name="Employé")
        self.admin = User.objects.create_user(username="boss", password="boss1234", is_staff=True)
        self.admin.groups.add(admin_g)
        self.employe = User.objects.create_user(username="emp1", password="emp1234", is_staff=True)
        self.employe.groups.add(employe_g)

    def test_statistiques_admin(self):
        self._login_as("boss", "boss1234")
        response = self.client.get(reverse("statistiques"))
        self.assertEqual(response.status_code, 200)

    def test_statistiques_employe(self):
        self._login_as("emp1", "emp1234")
        response = self.client.get(reverse("statistiques"))
        self.assertEqual(response.status_code, 200)


class RapportPDFTests(TestCase, BaseAuthMixin):
    def setUp(self):
        self.user = User.objects.create_user(username="staff", password="staff1234", is_staff=True)

    def test_rapport_pdf(self):
        self._login_as("staff", "staff1234")
        response = self.client.get(reverse("rapport_pdf"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/pdf")


class HandlerTests(TestCase):
    def test_404_page(self):
        response = self.client.get("/page-inexistante/")
        self.assertEqual(response.status_code, 404)
        self.assertContains(response, "404", status_code=404)


class AJAXReservationTests(TestCase, BaseAuthMixin):
    def setUp(self):
        admin_g, _ = Group.objects.get_or_create(name="Admin")
        self.staff_user = User.objects.create_user(username="staff", password="staff1234", is_staff=True)
        self.staff_user.groups.add(admin_g)
        
        self.user = User.objects.create_user(username="ahmed", password="client1234")
        self.client_obj = Client.objects.create(
            user=self.user, nom="El Amrani", prenom="Ahmed", cin="AB12345", telephone="0612345678"
        )
        self.voiture = Voiture.objects.create(
            marque="Dacia", modele="Duster", immatriculation="AB-456-EF", annee=2023, prix_jour=500,
        )
        self.reservation = Reservation.objects.create(
            client=self.client_obj, voiture=self.voiture,
            date_debut=date.today() + timedelta(days=1),
            date_fin=date.today() + timedelta(days=4),
            statut="en_attente"
        )

    def test_verifier_disponibilite_voiture_api(self):
        self._login_as("ahmed", "client1234")
        url = reverse("verifier_disponibilite_voiture")
        response = self.client.get(url, {
            "voiture": self.voiture.pk,
            "date_debut": (date.today() + timedelta(days=5)).isoformat(),
            "date_fin": (date.today() + timedelta(days=8)).isoformat(),
        }, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["available"])
        self.assertIn("Véhicule disponible", data["message"])

    def test_verifier_disponibilite_voiture_conflit(self):
        self._login_as("ahmed", "client1234")
        url = reverse("verifier_disponibilite_voiture")
        response = self.client.get(url, {
            "voiture": self.voiture.pk,
            "date_debut": (date.today() + timedelta(days=2)).isoformat(),
            "date_fin": (date.today() + timedelta(days=3)).isoformat(),
        }, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertFalse(data["available"])
        self.assertIn("pas disponible", data["message"])

    def test_accepter_reservation_ajax(self):
        self._login_as("staff", "staff1234")
        url = reverse("accepter_reservation", args=[self.reservation.pk])
        response = self.client.post(url, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "success")
        self.assertEqual(data["new_statut"], "en_cours")
        
        self.reservation.refresh_from_db()
        self.assertEqual(self.reservation.statut, "en_cours")

    def test_refuser_reservation_ajax(self):
        self._login_as("staff", "staff1234")
        url = reverse("refuser_reservation", args=[self.reservation.pk])
        response = self.client.post(url, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "success")
        self.assertEqual(data["new_statut"], "annulee")
        
        self.reservation.refresh_from_db()
        self.assertEqual(self.reservation.statut, "annulee")

    def test_verifier_disponibilite_sans_params(self):
        self._login_as("ahmed", "client1234")
        url = reverse("verifier_disponibilite_voiture")
        response = self.client.get(url, {}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertFalse(data["available"])

    def test_verifier_disponibilite_date_fin_avant_debut(self):
        self._login_as("ahmed", "client1234")
        url = reverse("verifier_disponibilite_voiture")
        response = self.client.get(url, {
            "voiture": self.voiture.pk,
            "date_debut": (date.today() + timedelta(days=5)).isoformat(),
            "date_fin": (date.today() + timedelta(days=3)).isoformat(),
        }, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        data = response.json()
        self.assertFalse(data["available"])

    def test_verifier_disponibilite_voiture_inexistante(self):
        self._login_as("ahmed", "client1234")
        url = reverse("verifier_disponibilite_voiture")
        response = self.client.get(url, {
            "voiture": 9999,
            "date_debut": (date.today() + timedelta(days=5)).isoformat(),
            "date_fin": (date.today() + timedelta(days=8)).isoformat(),
        }, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        data = response.json()
        self.assertFalse(data["available"])

    def test_annuler_reservation_ajax(self):
        self._login_as("staff", "staff1234")
        url = reverse("annuler_reservation", args=[self.reservation.pk])
        response = self.client.post(url, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "success")
        self.assertEqual(data["new_statut"], "annulee")
        self.reservation.refresh_from_db()
        self.assertEqual(self.reservation.statut, "annulee")

    def test_terminer_reservation_ajax(self):
        r = Reservation.objects.create(
            client=self.client_obj, voiture=self.voiture,
            date_debut=date.today(), date_fin=date.today() + timedelta(days=1),
            statut="en_cours",
        )
        self.voiture.statut = "louee"
        self.voiture.save()
        self._login_as("staff", "staff1234")
        url = reverse("terminer_reservation", args=[r.pk])
        response = self.client.post(url, {
            "date_retour_reelle": date.today().isoformat(),
            "remarque": "",
        }, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "success")
        self.assertEqual(data["new_statut"], "terminee")
        r.refresh_from_db()
        self.assertEqual(r.statut, "terminee")

    def test_client_creer_reservation_ajax_success(self):
        self._login_as("ahmed", "client1234")
        response = self.client.post(
            reverse("client_creer_reservation"),
            {
                "voiture": self.voiture.pk,
                "date_debut": (date.today() + timedelta(days=10)).isoformat(),
                "date_fin": (date.today() + timedelta(days=12)).isoformat(),
            },
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "success")

    def test_client_creer_reservation_ajax_date_invalide(self):
        self._login_as("ahmed", "client1234")
        response = self.client.post(
            reverse("client_creer_reservation"),
            {
                "voiture": self.voiture.pk,
                "date_debut": (date.today() + timedelta(days=12)).isoformat(),
                "date_fin": (date.today() + timedelta(days=10)).isoformat(),
            },
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        )
        data = response.json()
        self.assertEqual(data["status"], "error")


# ---------- NOUVEAUX TESTS ----------


class LogoutTests(TestCase, BaseAuthMixin):
    def setUp(self):
        self.user = User.objects.create_user(username="staff", password="staff1234", is_staff=True)

    def test_logout(self):
        self._login_as("staff", "staff1234")
        response = self.client.get(reverse("logout"))
        self.assertRedirects(response, reverse("login"))

    def test_logout_sans_login(self):
        response = self.client.get(reverse("logout"))
        self.assertRedirects(response, reverse("login"))


class DashboardContextTests(TestCase, BaseAuthMixin):
    def setUp(self):
        Group.objects.get_or_create(name="Admin")
        self.user = User.objects.create_user(username="staff", password="staff1234", is_staff=True)
        self.user.groups.add(Group.objects.get(name="Admin"))
        self.client_obj = Client.objects.create(
            nom="Test", prenom="Client", cin="DASH001", telephone="0600000000"
        )
        self.voiture = Voiture.objects.create(
            marque="BMW", modele="X1", immatriculation="BM-001-WW", annee=2023, prix_jour=600,
        )

    def test_dashboard_contexte_complet(self):
        Reservation.objects.create(
            client=self.client_obj, voiture=self.voiture,
            date_debut=date.today(), date_fin=date.today() + timedelta(days=2),
            statut="en_cours",
        )
        Reservation.objects.create(
            client=self.client_obj, voiture=self.voiture,
            date_debut=date.today() - timedelta(days=5),
            date_fin=date.today() - timedelta(days=3),
            statut="terminee",
        )
        self._login_as("staff", "staff1234")
        response = self.client.get(reverse("dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Dashboard")
        self.assertEqual(response.context["total_voitures"], 1)
        self.assertEqual(response.context["total_clients"], 1)
        self.assertEqual(response.context["reservations_en_cours"], 1)
        self.assertEqual(response.context["reservations_terminees"], 1)
        self.assertEqual(response.context["ca_total"], 1200)

    def test_dashboard_demandes_en_attente(self):
        Reservation.objects.create(
            client=self.client_obj, voiture=self.voiture,
            date_debut=date.today() + timedelta(days=1),
            date_fin=date.today() + timedelta(days=3),
            statut="en_attente",
        )
        self._login_as("staff", "staff1234")
        response = self.client.get(reverse("dashboard"))
        self.assertEqual(response.context["nb_demandes_attente"], 1)
        self.assertEqual(len(response.context["demandes_en_attente"]), 1)

    def test_dashboard_sans_reservations(self):
        self._login_as("staff", "staff1234")
        response = self.client.get(reverse("dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["ca_total"], 0)
        self.assertEqual(response.context["reservations_en_cours"], 0)

    def test_dashboard_acces_employe(self):
        Group.objects.get_or_create(name="Employé")
        emp = User.objects.create_user(username="emp1", password="emp1234", is_staff=True)
        emp.groups.add(Group.objects.get(name="Employé"))
        self._login_as("emp1", "emp1234")
        response = self.client.get(reverse("dashboard"))
        self.assertEqual(response.status_code, 200)


class VoitureViewEdgeCaseTests(TestCase, BaseAuthMixin):
    def setUp(self):
        Group.objects.get_or_create(name="Admin")
        self.user = User.objects.create_user(username="staff", password="staff1234", is_staff=True)
        self.user.groups.add(Group.objects.get(name="Admin"))
        self.voiture = Voiture.objects.create(
            marque="Renault", modele="Clio", immatriculation="XX-123-YY", annee=2022, prix_jour=300,
        )

    def test_suppression_voiture_GET(self):
        self._login_as("staff", "staff1234")
        response = self.client.get(reverse("supprimer_voiture", args=[self.voiture.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Confirmation")

    def test_detail_voiture_avec_reservations(self):
        c = Client.objects.create(nom="X", prenom="Y", cin="DETV01", telephone="0600000000")
        Reservation.objects.create(
            client=c, voiture=self.voiture,
            date_debut=date.today(), date_fin=date.today() + timedelta(days=1),
        )
        self._login_as("staff", "staff1234")
        response = self.client.get(reverse("detail_voiture", args=[self.voiture.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Clio")
        self.assertEqual(len(response.context["reservations"]), 1)

    def test_liste_voitures_filtre_statut(self):
        Voiture.objects.create(
            marque="Peugeot", modele="208", immatriculation="PE-001-ZZ", annee=2021, prix_jour=250,
            statut="maintenance",
        )
        self._login_as("staff", "staff1234")
        response = self.client.get(reverse("liste_voitures") + "?statut=maintenance")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Peugeot")
        self.assertNotContains(response, "Renault")

    def test_liste_voitures_recherche(self):
        self._login_as("staff", "staff1234")
        response = self.client.get(reverse("liste_voitures") + "?q=Clio")
        self.assertContains(response, "Clio")
        response = self.client.get(reverse("liste_voitures") + "?q=inexistant")
        self.assertNotContains(response, "Clio")

    def test_ajouter_voiture_formulaire_invalide(self):
        self._login_as("staff", "staff1234")
        response = self.client.post(reverse("ajouter_voiture"), {})
        self.assertEqual(response.status_code, 200)

    def test_modifier_voiture_GET(self):
        self._login_as("staff", "staff1234")
        response = self.client.get(reverse("modifier_voiture", args=[self.voiture.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Clio")

    def test_voiture_inexistante_404(self):
        self._login_as("staff", "staff1234")
        response = self.client.get(reverse("detail_voiture", args=[9999]))
        self.assertEqual(response.status_code, 404)


class VoitureAccesNonAdminTests(TestCase, BaseAuthMixin):
    def setUp(self):
        Group.objects.get_or_create(name="Employé")
        self.emp = User.objects.create_user(username="emp1", password="emp1234", is_staff=True)
        self.emp.groups.add(Group.objects.get(name="Employé"))
        self.voiture = Voiture.objects.create(
            marque="Renault", modele="Clio", immatriculation="XX-123-YY", annee=2022, prix_jour=300,
        )

    def test_employe_peut_voir_liste_voitures(self):
        self._login_as("emp1", "emp1234")
        response = self.client.get(reverse("liste_voitures"))
        self.assertEqual(response.status_code, 200)

    def test_employe_bloque_ajout_voiture(self):
        self._login_as("emp1", "emp1234")
        response = self.client.get(reverse("ajouter_voiture"))
        self.assertEqual(response.status_code, 302)

    def test_employe_bloque_suppression_voiture(self):
        self._login_as("emp1", "emp1234")
        response = self.client.post(reverse("supprimer_voiture", args=[self.voiture.pk]))
        self.assertEqual(response.status_code, 302)


class ClientViewEdgeCaseTests(TestCase, BaseAuthMixin):
    def setUp(self):
        Group.objects.get_or_create(name="Admin")
        self.user = User.objects.create_user(username="staff", password="staff1234", is_staff=True)
        self.user.groups.add(Group.objects.get(name="Admin"))
        self.client_obj = Client.objects.create(
            nom="El Amrani", prenom="Ahmed", cin="AB12345", telephone="0612345678"
        )

    def test_liste_clients(self):
        self._login_as("staff", "staff1234")
        response = self.client.get(reverse("liste_clients"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "El Amrani")

    def test_ajouter_client(self):
        self._login_as("staff", "staff1234")
        response = self.client.post(reverse("ajouter_client"), {
            "nom": "Nouveau", "prenom": "Client", "cin": "NEWCL01",
            "telephone": "0611111111",
        })
        self.assertRedirects(response, reverse("liste_clients"))
        self.assertEqual(Client.objects.count(), 2)

    def test_modifier_client(self):
        self._login_as("staff", "staff1234")
        response = self.client.post(reverse("modifier_client", args=[self.client_obj.pk]), {
            "nom": "El Amrani", "prenom": "Ahmed Modifié", "cin": "AB12345",
            "telephone": "0612345678",
        })
        self.assertRedirects(response, reverse("liste_clients"))
        self.client_obj.refresh_from_db()
        self.assertEqual(self.client_obj.prenom, "Ahmed Modifié")

    def test_supprimer_client(self):
        self._login_as("staff", "staff1234")
        response = self.client.post(reverse("supprimer_client", args=[self.client_obj.pk]))
        self.assertRedirects(response, reverse("liste_clients"))
        self.assertEqual(Client.objects.count(), 0)

    def test_detail_client(self):
        self._login_as("staff", "staff1234")
        response = self.client.get(reverse("detail_client", args=[self.client_obj.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Ahmed")

    def test_liste_clients_recherche(self):
        self._login_as("staff", "staff1234")
        response = self.client.get(reverse("liste_clients") + "?q=Amrani")
        self.assertContains(response, "El Amrani")
        response = self.client.get(reverse("liste_clients") + "?q=inexistant")
        self.assertNotContains(response, "El Amrani")

    def test_supprimer_client_GET(self):
        self._login_as("staff", "staff1234")
        response = self.client.get(reverse("supprimer_client", args=[self.client_obj.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Confirmation")

    def test_client_inexistant_404(self):
        self._login_as("staff", "staff1234")
        response = self.client.get(reverse("detail_client", args=[9999]))
        self.assertEqual(response.status_code, 404)


class ClientAccesNonAdminTests(TestCase, BaseAuthMixin):
    def setUp(self):
        Group.objects.get_or_create(name="Employé")
        self.emp = User.objects.create_user(username="emp1", password="emp1234", is_staff=True)
        self.emp.groups.add(Group.objects.get(name="Employé"))
        self.client_obj = Client.objects.create(
            nom="Test", prenom="Client", cin="TSTCL01", telephone="0600000000"
        )

    def test_employe_peut_voir_liste_clients(self):
        self._login_as("emp1", "emp1234")
        response = self.client.get(reverse("liste_clients"))
        self.assertEqual(response.status_code, 200)

    def test_employe_peut_ajouter_client(self):
        self._login_as("emp1", "emp1234")
        response = self.client.get(reverse("ajouter_client"))
        self.assertEqual(response.status_code, 200)

    def test_employe_bloque_suppression_client(self):
        self._login_as("emp1", "emp1234")
        response = self.client.post(reverse("supprimer_client", args=[self.client_obj.pk]))
        self.assertEqual(response.status_code, 302)

    def test_employe_bloque_modification_client(self):
        self._login_as("emp1", "emp1234")
        response = self.client.get(reverse("modifier_client", args=[self.client_obj.pk]))
        self.assertEqual(response.status_code, 302)


class ReservationViewEdgeCaseTests(TestCase, BaseAuthMixin):
    def setUp(self):
        Group.objects.get_or_create(name="Admin")
        self.user = User.objects.create_user(username="staff", password="staff1234", is_staff=True)
        self.user.groups.add(Group.objects.get(name="Admin"))
        self.client_ahmed = Client.objects.create(
            nom="El Amrani", prenom="Ahmed", cin="AB12345", telephone="0612345678"
        )
        self.client_fatima = Client.objects.create(
            nom="Benali", prenom="Fatima", cin="CD67890", telephone="0623456789"
        )
        self.voiture = Voiture.objects.create(
            marque="Dacia", modele="Duster", immatriculation="AB-456-EF", annee=2023, prix_jour=500,
        )

    def test_liste_reservations(self):
        Reservation.objects.create(
            client=self.client_ahmed, voiture=self.voiture,
            date_debut=date.today(), date_fin=date.today() + timedelta(days=2),
        )
        self._login_as("staff", "staff1234")
        response = self.client.get(reverse("liste_reservations"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Duster")

    def test_liste_reservations_filtre_statut(self):
        Reservation.objects.create(
            client=self.client_ahmed, voiture=self.voiture,
            date_debut=date.today(), date_fin=date.today() + timedelta(days=2),
            statut="terminee",
        )
        Reservation.objects.create(
            client=self.client_fatima, voiture=self.voiture,
            date_debut=date.today() + timedelta(days=3),
            date_fin=date.today() + timedelta(days=5),
            statut="en_attente",
        )
        self._login_as("staff", "staff1234")
        response = self.client.get(reverse("liste_reservations") + "?statut=terminee")
        self.assertContains(response, "El Amrani")
        self.assertNotContains(response, "Fatima")

    def test_detail_reservation(self):
        r = Reservation.objects.create(
            client=self.client_ahmed, voiture=self.voiture,
            date_debut=date.today(), date_fin=date.today() + timedelta(days=2),
        )
        self._login_as("staff", "staff1234")
        response = self.client.get(reverse("detail_reservation", args=[r.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Ahmed")

    def test_modifier_reservation(self):
        r = Reservation.objects.create(
            client=self.client_ahmed, voiture=self.voiture,
            date_debut=date.today(), date_fin=date.today() + timedelta(days=2),
        )
        self._login_as("staff", "staff1234")
        response = self.client.post(reverse("modifier_reservation", args=[r.pk]), {
            "client": self.client_fatima.pk,
            "voiture": self.voiture.pk,
            "date_debut": (date.today() + timedelta(days=5)).isoformat(),
            "date_fin": (date.today() + timedelta(days=8)).isoformat(),
        })
        self.assertRedirects(response, reverse("liste_reservations"))
        r.refresh_from_db()
        self.assertEqual(r.client, self.client_fatima)

    def test_annuler_reservation_GET(self):
        r = Reservation.objects.create(
            client=self.client_ahmed, voiture=self.voiture,
            date_debut=date.today(), date_fin=date.today() + timedelta(days=2),
            statut="en_cours",
        )
        self._login_as("staff", "staff1234")
        response = self.client.get(reverse("annuler_reservation", args=[r.pk]))
        self.assertEqual(response.status_code, 200)

    def test_terminer_reservation_GET(self):
        r = Reservation.objects.create(
            client=self.client_ahmed, voiture=self.voiture,
            date_debut=date.today(), date_fin=date.today() + timedelta(days=2),
            statut="en_cours",
        )
        self._login_as("staff", "staff1234")
        response = self.client.get(reverse("terminer_reservation", args=[r.pk]))
        self.assertEqual(response.status_code, 200)

    def test_terminer_reservation_pas_en_cours_bloque(self):
        r = Reservation.objects.create(
            client=self.client_ahmed, voiture=self.voiture,
            date_debut=date.today(), date_fin=date.today() + timedelta(days=2),
            statut="en_attente",
        )
        self._login_as("staff", "staff1234")
        response = self.client.post(reverse("terminer_reservation", args=[r.pk]))
        r.refresh_from_db()
        self.assertEqual(r.statut, "en_attente")

    def test_accepter_reservation_deja_traitee(self):
        r = Reservation.objects.create(
            client=self.client_ahmed, voiture=self.voiture,
            date_debut=date.today(), date_fin=date.today() + timedelta(days=2),
            statut="en_cours",
        )
        self._login_as("staff", "staff1234")
        response = self.client.get(reverse("accepter_reservation", args=[r.pk]))
        r.refresh_from_db()
        self.assertEqual(r.statut, "en_cours")

    def test_refuser_reservation_deja_traitee(self):
        r = Reservation.objects.create(
            client=self.client_ahmed, voiture=self.voiture,
            date_debut=date.today(), date_fin=date.today() + timedelta(days=2),
            statut="annulee",
        )
        self._login_as("staff", "staff1234")
        response = self.client.post(reverse("refuser_reservation", args=[r.pk]))
        r.refresh_from_db()
        self.assertEqual(r.statut, "annulee")

    def test_accepter_conflit_sur_periode(self):
        Reservation.objects.create(
            client=self.client_ahmed, voiture=self.voiture,
            date_debut=date.today(), date_fin=date.today() + timedelta(days=5),
            statut="en_cours",
        )
        r2 = Reservation.objects.create(
            client=self.client_fatima, voiture=self.voiture,
            date_debut=date.today() + timedelta(days=2),
            date_fin=date.today() + timedelta(days=7),
            statut="en_attente",
        )
        self._login_as("staff", "staff1234")
        response = self.client.get(reverse("accepter_reservation", args=[r2.pk]))
        r2.refresh_from_db()
        self.assertEqual(r2.statut, "en_attente")

    def test_annuler_reservation_liberer_voiture(self):
        self.voiture.statut = "louee"
        self.voiture.save()
        r = Reservation.objects.create(
            client=self.client_ahmed, voiture=self.voiture,
            date_debut=date.today(), date_fin=date.today() + timedelta(days=2),
            statut="en_cours",
        )
        self._login_as("staff", "staff1234")
        self.client.post(reverse("annuler_reservation", args=[r.pk]))
        self.voiture.refresh_from_db()
        self.assertEqual(self.voiture.statut, "disponible")

    def test_annuler_reservation_ne_libere_pas_si_autre_en_cours(self):
        v2 = Voiture.objects.create(
            marque="Peugeot", modele="208", immatriculation="PE-002-ZZ", annee=2022, prix_jour=300,
            statut="louee",
        )
        Reservation.objects.create(
            client=self.client_ahmed, voiture=v2,
            date_debut=date.today(), date_fin=date.today() + timedelta(days=2),
            statut="en_cours",
        )
        r2 = Reservation.objects.create(
            client=self.client_fatima, voiture=v2,
            date_debut=date.today(), date_fin=date.today() + timedelta(days=2),
            statut="en_cours",
        )
        self._login_as("staff", "staff1234")
        self.client.post(reverse("annuler_reservation", args=[r2.pk]))
        v2.refresh_from_db()
        self.assertEqual(v2.statut, "louee")


class FacturePDFTests(TestCase, BaseAuthMixin):
    def setUp(self):
        self.user = User.objects.create_user(username="staff", password="staff1234", is_staff=True)
        self.client_obj = Client.objects.create(
            nom="El Amrani", prenom="Ahmed", cin="AB12345", telephone="0612345678"
        )
        self.voiture = Voiture.objects.create(
            marque="Dacia", modele="Duster", immatriculation="AB-456-EF", annee=2023, prix_jour=500,
        )

    def test_facture_pdf(self):
        r = Reservation.objects.create(
            client=self.client_obj, voiture=self.voiture,
            date_debut=date.today(), date_fin=date.today() + timedelta(days=3),
        )
        self._login_as("staff", "staff1234")
        response = self.client.get(reverse("facture_pdf", args=[r.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/pdf")

    def test_facture_404_reservation_inexistante(self):
        self._login_as("staff", "staff1234")
        response = self.client.get(reverse("facture_pdf", args=[9999]))
        self.assertEqual(response.status_code, 404)


class ExportClientsCSVTests(TestCase, BaseAuthMixin):
    def setUp(self):
        self.user = User.objects.create_user(username="staff", password="staff1234", is_staff=True)
        Client.objects.create(
            nom="Test", prenom="Client", cin="EXPCL01", telephone="0600000000"
        )

    def test_export_clients_csv(self):
        self._login_as("staff", "staff1234")
        response = self.client.get(reverse("export_clients_csv"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "text/csv")
        content = response.content.decode()
        self.assertIn("Test", content)
        self.assertIn("Client", content)


class ClientAnnulationEdgeCasesTests(TestCase, BaseAuthMixin):
    def setUp(self):
        self.user = User.objects.create_user(username="ahmed", password="client1234")
        self.client_obj = Client.objects.create(
            user=self.user, nom="El Amrani", prenom="Ahmed", cin="AB12345", telephone="0612345678"
        )
        self.voiture = Voiture.objects.create(
            marque="Dacia", modele="Duster", immatriculation="AB-456-EF", annee=2023, prix_jour=500,
        )

    def test_client_annule_demande_deja_en_cours_bloque(self):
        r = Reservation.objects.create(
            client=self.client_obj, voiture=self.voiture,
            date_debut=date.today(), date_fin=date.today() + timedelta(days=2),
            statut="en_cours",
        )
        self._login_as("ahmed", "client1234")
        self.client.get(reverse("client_annuler_demande", args=[r.pk]))
        r.refresh_from_db()
        self.assertEqual(r.statut, "en_cours")

    def test_client_annule_demande_terminee_bloque(self):
        r = Reservation.objects.create(
            client=self.client_obj, voiture=self.voiture,
            date_debut=date.today(), date_fin=date.today() + timedelta(days=2),
            statut="terminee",
        )
        self._login_as("ahmed", "client1234")
        self.client.get(reverse("client_annuler_demande", args=[r.pk]))
        r.refresh_from_db()
        self.assertEqual(r.statut, "terminee")


class ClientDashboardEdgeCasesTests(TestCase, BaseAuthMixin):
    def setUp(self):
        self.user = User.objects.create_user(username="ahmed", password="client1234")
        self.client_obj = Client.objects.create(
            user=self.user, nom="El Amrani", prenom="Ahmed", cin="AB12345", telephone="0612345678"
        )
        self.voiture = Voiture.objects.create(
            marque="Dacia", modele="Duster", immatriculation="AB-456-EF", annee=2023, prix_jour=500,
        )

    def test_client_dashboard_sans_reservations(self):
        self._login_as("ahmed", "client1234")
        response = self.client.get(reverse("client_dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["en_cours_count"], 0)

    def test_client_dashboard_compteurs(self):
        Reservation.objects.create(
            client=self.client_obj, voiture=self.voiture,
            date_debut=date.today(), date_fin=date.today() + timedelta(days=2),
            statut="en_cours",
        )
        Reservation.objects.create(
            client=self.client_obj, voiture=self.voiture,
            date_debut=date.today() + timedelta(days=3),
            date_fin=date.today() + timedelta(days=5),
            statut="en_attente",
        )
        Reservation.objects.create(
            client=self.client_obj, voiture=self.voiture,
            date_debut=date.today() - timedelta(days=10),
            date_fin=date.today() - timedelta(days=8),
            statut="terminee",
        )
        self._login_as("ahmed", "client1234")
        response = self.client.get(reverse("client_dashboard"))
        self.assertEqual(response.context["en_cours_count"], 1)
        self.assertEqual(response.context["en_attente_count"], 1)
        self.assertEqual(response.context["terminees_count"], 1)
        self.assertEqual(response.context["total_depense"], 1000)

    def test_client_dashboard_pas_de_profil(self):
        u = User.objects.create_user(username="orphan", password="test1234")
        self.client.login(username="orphan", password="test1234")
        response = self.client.get(reverse("client_dashboard"))
        self.assertRedirects(response, reverse("login"))


class ClientRegistrationEdgeCasesTests(TestCase):
    def test_inscription_cin_duplique(self):
        User.objects.create_user(username="exist", password="test1234")
        Client.objects.create(
            nom="Exist", prenom="Client", cin="DUP001", telephone="0600000000"
        )
        response = self.client.post(reverse("client_register"), {
            "username": "nouveau",
            "nom": "Test",
            "prenom": "User",
            "cin": "DUP001",
            "telephone": "0600000000",
            "password1": "ComplexPass123!",
            "password2": "ComplexPass123!",
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username="nouveau").exists())

    def test_inscription_passwords_mismatch(self):
        response = self.client.post(reverse("client_register"), {
            "username": "nouveau",
            "nom": "Test",
            "prenom": "User",
            "cin": "PASS01",
            "telephone": "0600000000",
            "password1": "ComplexPass123!",
            "password2": "DifferentPass123!",
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username="nouveau").exists())

    def test_inscription_champs_obligatoires(self):
        response = self.client.post(reverse("client_register"), {
            "username": "",
            "nom": "",
            "prenom": "",
            "cin": "",
            "telephone": "",
        })
        self.assertEqual(response.status_code, 200)

    def test_register_GET(self):
        response = self.client.get(reverse("client_register"))
        self.assertEqual(response.status_code, 200)


class RBACEdgeCaseTests(TestCase, BaseAuthMixin):
    def setUp(self):
        Group.objects.get_or_create(name="Admin")
        Group.objects.get_or_create(name="Employé")
        self.admin = User.objects.create_user(username="boss", password="boss1234", is_staff=True, is_superuser=True)
        self.admin.groups.add(Group.objects.get(name="Admin"))

    def test_gestion_roles_GET(self):
        self._login_as("boss", "boss1234")
        response = self.client.get(reverse("gestion_roles"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("users_data", response.context)

    def test_add_user_username_existant(self):
        self._login_as("boss", "boss1234")
        response = self.client.post(reverse("gestion_roles"), {
            "action": "add_user",
            "new_username": "boss",
            "new_password": "pass1234",
            "new_groupe": "Employé",
        })
        self.assertRedirects(response, reverse("gestion_roles"))

    def test_add_user_sans_mdp(self):
        self._login_as("boss", "boss1234")
        response = self.client.post(reverse("gestion_roles"), {
            "action": "add_user",
            "new_username": "nouveau",
            "new_password": "",
            "new_groupe": "Employé",
        })
        self.assertRedirects(response, reverse("gestion_roles"))
        self.assertFalse(User.objects.filter(username="nouveau").exists())

    def test_add_user_sans_groupe(self):
        self._login_as("boss", "boss1234")
        response = self.client.post(reverse("gestion_roles"), {
            "action": "add_user",
            "new_username": "sansgroupe",
            "new_password": "pass1234",
            "new_groupe": "",
        })
        self.assertRedirects(response, reverse("gestion_roles"))
        u = User.objects.get(username="sansgroupe")
        self.assertEqual(u.groups.count(), 0)

    def test_change_role_none(self):
        emp = User.objects.create_user(username="emp1", password="emp1234", is_staff=True)
        emp.groups.add(Group.objects.get(name="Employé"))
        self._login_as("boss", "boss1234")
        response = self.client.post(reverse("gestion_roles"), {
            "action": "change_role",
            "user_id": emp.pk,
            "groupe": "",
        })
        self.assertRedirects(response, reverse("gestion_roles"))
        emp.refresh_from_db()
        self.assertEqual(emp.groups.count(), 0)


class RapportPDFEdgeCaseTests(TestCase, BaseAuthMixin):
    def setUp(self):
        self.user = User.objects.create_user(username="staff", password="staff1234", is_staff=True)

    def test_rapport_pdf_sans_donnees(self):
        self._login_as("staff", "staff1234")
        response = self.client.get(reverse("rapport_pdf"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/pdf")


class AccueilEdgeCaseTests(TestCase):
    def test_page_accueil_context(self):
        Voiture.objects.create(
            marque="Renault", modele="Clio", immatriculation="XX-123-YY", annee=2022, prix_jour=300,
        )
        Voiture.objects.create(
            marque="Peugeot", modele="208", immatriculation="PE-001-ZZ", annee=2021, prix_jour=250,
            statut="maintenance",
        )
        response = self.client.get(reverse("accueil"))
        self.assertEqual(response.context["total_voitures"], 2)
        self.assertEqual(response.context["voitures_dispo"], 1)


class PaginationEdgeCaseTests(TestCase, BaseAuthMixin):
    def setUp(self):
        Group.objects.get_or_create(name="Admin")
        self.user = User.objects.create_user(username="staff", password="staff1234", is_staff=True)
        self.user.groups.add(Group.objects.get(name="Admin"))

    def test_pagination_clients(self):
        for i in range(15):
            Client.objects.create(
                nom=f"Nom{i}", prenom=f"Prenom{i}", cin=f"CIN{i:05d}", telephone=f"06000000{i:02d}"
            )
        self._login_as("staff", "staff1234")
        response = self.client.get(reverse("liste_clients"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["page_obj"]), 10)

    def test_pagination_reservations(self):
        c = Client.objects.create(nom="X", prenom="Y", cin="PAGRS01", telephone="0600000000")
        v = Voiture.objects.create(
            marque="Dacia", modele="Duster", immatriculation="PA-001-GG", annee=2023, prix_jour=500,
        )
        for i in range(15):
            Reservation.objects.create(
                client=c, voiture=v,
                date_debut=date.today() + timedelta(days=i * 10),
                date_fin=date.today() + timedelta(days=i * 10 + 1),
            )
        self._login_as("staff", "staff1234")
        response = self.client.get(reverse("liste_reservations"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["page_obj"]), 10)


class AccueilRedirectionClientTests(TestCase):
    def test_redirection_si_client_connecte(self):
        u = User.objects.create_user(username="ahmed", password="client1234")
        Client.objects.create(user=u, nom="Test", prenom="Client", cin="REDIR01", telephone="0600000000")
        self.client.login(username="ahmed", password="client1234")
        response = self.client.get(reverse("accueil"))
        self.assertRedirects(response, reverse("client_dashboard"))


# ═══════════════════════════════════════════════════════════
# TESTS CATEGORIES (model + CRUD vues)
# ═══════════════════════════════════════════════════════════

class CategorieModelTests(TestCase):
    def test_str_categorie(self):
        cat = Categorie.objects.create(nom="SUV", description="Vehicules tout-terrain")
        self.assertEqual(str(cat), "SUV")

    def test_nom_unique(self):
        Categorie.objects.create(nom="Berline")
        with self.assertRaises(Exception):
            Categorie.objects.create(nom="Berline")


class CategorieViewTests(TestCase, BaseAuthMixin):
    def setUp(self):
        Group.objects.get_or_create(name="Admin")
        self.user = User.objects.create_user(username="staff", password="staff1234", is_staff=True)
        self.user.groups.add(Group.objects.get(name="Admin"))
        self.categorie = Categorie.objects.create(nom="SUV", description="Vehicules tout-terrain")

    def test_liste_categories_affiche(self):
        self._login_as("staff", "staff1234")
        response = self.client.get(reverse("liste_categories"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "SUV")

    def test_liste_categories_recherche(self):
        Categorie.objects.create(nom="Berline")
        self._login_as("staff", "staff1234")
        response = self.client.get(reverse("liste_categories") + "?q=SUV")
        self.assertEqual(len(response.context["page_obj"]), 1)

    def test_ajouter_categorie_get(self):
        self._login_as("staff", "staff1234")
        response = self.client.get(reverse("ajouter_categorie"))
        self.assertEqual(response.status_code, 200)

    def test_ajouter_categorie_post(self):
        self._login_as("staff", "staff1234")
        response = self.client.post(reverse("ajouter_categorie"), {
            "nom": "Citadine",
            "description": "Petites voitures",
        })
        self.assertRedirects(response, reverse("liste_categories"))
        self.assertEqual(Categorie.objects.count(), 2)

    def test_modifier_categorie_get(self):
        self._login_as("staff", "staff1234")
        response = self.client.get(reverse("modifier_categorie", args=[self.categorie.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "SUV")

    def test_modifier_categorie_post(self):
        self._login_as("staff", "staff1234")
        response = self.client.post(reverse("modifier_categorie", args=[self.categorie.pk]), {
            "nom": "SUV Premium",
            "description": "Vehicules haut de gamme",
        })
        self.assertRedirects(response, reverse("liste_categories"))
        self.categorie.refresh_from_db()
        self.assertEqual(self.categorie.nom, "SUV Premium")

    def test_supprimer_categorie_get_confirmation(self):
        self._login_as("staff", "staff1234")
        response = self.client.get(reverse("supprimer_categorie", args=[self.categorie.pk]))
        self.assertEqual(response.status_code, 200)

    def test_supprimer_categorie_post(self):
        self._login_as("staff", "staff1234")
        response = self.client.post(reverse("supprimer_categorie", args=[self.categorie.pk]))
        self.assertRedirects(response, reverse("liste_categories"))
        self.assertEqual(Categorie.objects.count(), 0)

    def test_employe_interdit_categories(self):
        Group.objects.get_or_create(name="Employé")
        emp = User.objects.create_user(username="emp", password="emp1234", is_staff=True)
        emp.groups.add(Group.objects.get(name="Employé"))
        self._login_as("emp", "emp1234")
        for url_name in ["ajouter_categorie", "modifier_categorie", "supprimer_categorie"]:
            if url_name == "ajouter_categorie":
                response = self.client.get(reverse(url_name))
            else:
                response = self.client.get(reverse(url_name, args=[self.categorie.pk]))
            self.assertEqual(response.status_code, 302)


# ═══════════════════════════════════════════════════════════
# TESTS PAIEMENTS (model + CRUD vues)
# ═══════════════════════════════════════════════════════════

class PaiementModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="cliresa", password="test1234")
        self.client_obj = Client.objects.create(
            user=self.user, nom="Benali", prenom="Fatima", cin="CD67890", telephone="0623456789"
        )
        self.voiture = Voiture.objects.create(
            marque="Dacia", modele="Duster", immatriculation="AB-456-EF", annee=2023, prix_jour=500,
        )
        self.reservation = Reservation.objects.create(
            client=self.client_obj, voiture=self.voiture,
            date_debut=date.today(), date_fin=date.today() + timedelta(days=3),
        )

    def test_str_paiement(self):
        p = Paiement.objects.create(
            reservation=self.reservation, montant=1500,
            date_paiement=date.today(), mode_paiement="especes", statut="paye"
        )
        self.assertIn("1500", str(p))
        self.assertIn("Paye", str(p))

    def test_paiement_defaut_en_attente(self):
        p = Paiement.objects.create(
            reservation=self.reservation, montant=500,
            date_paiement=date.today(),
        )
        self.assertEqual(p.statut, "en_attente")

    def test_mode_paiement_defaut_especes(self):
        p = Paiement.objects.create(
            reservation=self.reservation, montant=500,
            date_paiement=date.today(),
        )
        self.assertEqual(p.mode_paiement, "especes")


class PaiementViewTests(TestCase, BaseAuthMixin):
    def setUp(self):
        Group.objects.get_or_create(name="Admin")
        self.user = User.objects.create_user(username="staff", password="staff1234", is_staff=True)
        self.user.groups.add(Group.objects.get(name="Admin"))
        self.client_user = User.objects.create_user(username="ahmed", password="client1234")
        self.client_obj = Client.objects.create(
            user=self.client_user, nom="El Amrani", prenom="Ahmed", cin="AB12345", telephone="0612345678"
        )
        self.voiture = Voiture.objects.create(
            marque="Dacia", modele="Duster", immatriculation="AB-456-EF", annee=2023, prix_jour=500,
        )
        self.reservation = Reservation.objects.create(
            client=self.client_obj, voiture=self.voiture,
            date_debut=date.today(), date_fin=date.today() + timedelta(days=3),
            statut="en_cours",
        )

    def test_liste_paiements(self):
        self._login_as("staff", "staff1234")
        response = self.client.get(reverse("liste_paiements"))
        self.assertEqual(response.status_code, 200)

    def test_liste_paiements_filtrer_statut(self):
        Paiement.objects.create(
            reservation=self.reservation, montant=1500,
            date_paiement=date.today(), statut="paye"
        )
        self._login_as("staff", "staff1234")
        response = self.client.get(reverse("liste_paiements") + "?statut=paye")
        self.assertEqual(len(response.context["page_obj"]), 1)

    def test_detail_paiement(self):
        p = Paiement.objects.create(
            reservation=self.reservation, montant=1500,
            date_paiement=date.today(), statut="paye"
        )
        self._login_as("staff", "staff1234")
        response = self.client.get(reverse("detail_paiement", args=[p.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "1500")

    def test_ajouter_paiement_get(self):
        self._login_as("staff", "staff1234")
        response = self.client.get(reverse("ajouter_paiement"))
        self.assertEqual(response.status_code, 200)

    def test_ajouter_paiement_post(self):
        self._login_as("staff", "staff1234")
        response = self.client.post(reverse("ajouter_paiement"), {
            "reservation": self.reservation.pk,
            "montant": "1500",
            "date_paiement": date.today().isoformat(),
            "mode_paiement": "especes",
            "statut": "paye",
        })
        self.assertRedirects(response, reverse("detail_reservation", args=[self.reservation.pk]))
        self.assertEqual(Paiement.objects.count(), 1)

    def test_ajouter_paiement_depuis_reservation(self):
        self._login_as("staff", "staff1234")
        response = self.client.get(reverse("ajouter_paiement_reservation", args=[self.reservation.pk]))
        self.assertEqual(response.status_code, 200)

    def test_ajouter_paiement_cree_historique(self):
        self._login_as("staff", "staff1234")
        self.client.post(reverse("ajouter_paiement"), {
            "reservation": self.reservation.pk,
            "montant": "1500",
            "date_paiement": date.today().isoformat(),
            "mode_paiement": "especes",
            "statut": "paye",
        })
        self.assertTrue(Historique.objects.filter(action="paiement").exists())

    def test_ajouter_paiement_notifie_client(self):
        self._login_as("staff", "staff1234")
        self.client.post(reverse("ajouter_paiement"), {
            "reservation": self.reservation.pk,
            "montant": "1500",
            "date_paiement": date.today().isoformat(),
            "mode_paiement": "especes",
            "statut": "paye",
        })
        self.assertTrue(Notification.objects.filter(utilisateur=self.client_user).exists())

    def test_modifier_paiement_get(self):
        p = Paiement.objects.create(
            reservation=self.reservation, montant=1500,
            date_paiement=date.today(), statut="paye"
        )
        self._login_as("staff", "staff1234")
        response = self.client.get(reverse("modifier_paiement", args=[p.pk]))
        self.assertEqual(response.status_code, 200)

    def test_modifier_paiement_post(self):
        p = Paiement.objects.create(
            reservation=self.reservation, montant=1500,
            date_paiement=date.today(), statut="paye"
        )
        self._login_as("staff", "staff1234")
        response = self.client.post(reverse("modifier_paiement", args=[p.pk]), {
            "montant": "2000",
            "date_paiement": date.today().isoformat(),
            "mode_paiement": "carte",
            "statut": "paye",
        })
        self.assertRedirects(response, reverse("detail_paiement", args=[p.pk]))
        p.refresh_from_db()
        self.assertEqual(p.montant, 2000)


# ═══════════════════════════════════════════════════════════
# TESTS HISTORIQUE (model + helper + integration)
# ═══════════════════════════════════════════════════════════

class HistoriqueModelTests(TestCase):
    def test_str_historique(self):
        h = Historique.objects.create(action="creation", description="Reservation #1 creee")
        self.assertIn("Création", str(h))
        self.assertIn("Reservation #1 creee", str(h))

    def test_date_action_auto(self):
        h = Historique.objects.create(action="validation", description="Test")
        self.assertIsNotNone(h.date_action)


class HistoriqueHelperTests(TestCase):
    def test_enregistrer_historique(self):
        enregistrer_historique("creation", "Test action")
        self.assertEqual(Historique.objects.count(), 1)
        h = Historique.objects.first()
        self.assertEqual(h.action, "creation")
        self.assertEqual(h.description, "Test action")

    def test_enregistrer_historique_avec_utilisateur(self):
        user = User.objects.create_user(username="staff", password="test1234")
        enregistrer_historique("validation", "Validation #1", utilisateur=user)
        h = Historique.objects.first()
        self.assertEqual(h.utilisateur, user)

    def test_enregistrer_historique_avec_reservation(self):
        user = User.objects.create_user(username="cliresa", password="test1234")
        client_obj = Client.objects.create(user=user, nom="Test", prenom="Client", cin="HIST01", telephone="0600000000")
        voiture = Voiture.objects.create(marque="Dacia", modele="Duster", immatriculation="HI-001-ZZ", annee=2023, prix_jour=500)
        reservation = Reservation.objects.create(client=client_obj, voiture=voiture, date_debut=date.today(), date_fin=date.today() + timedelta(days=2))
        enregistrer_historique("retour", "Retour enregistre", reservation=reservation)
        h = Historique.objects.first()
        self.assertEqual(h.reservation, reservation)


class HistoriqueViewTests(TestCase, BaseAuthMixin):
    def setUp(self):
        Group.objects.get_or_create(name="Admin")
        self.user = User.objects.create_user(username="staff", password="staff1234", is_staff=True)
        self.user.groups.add(Group.objects.get(name="Admin"))

    def test_historique_page(self):
        enregistrer_historique("creation", "Action test")
        self._login_as("staff", "staff1234")
        response = self.client.get(reverse("historique"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Action test")

    def test_historique_filtre_action(self):
        enregistrer_historique("creation", "Creation test")
        enregistrer_historique("retour", "Retour test")
        self._login_as("staff", "staff1234")
        response = self.client.get(reverse("historique") + "?action=retour")
        self.assertEqual(len(response.context["page_obj"]), 1)

    def test_historique_integration_accepter_reservation(self):
        client_user = User.objects.create_user(username="ahmed", password="client1234")
        client_obj = Client.objects.create(user=client_user, nom="El Amrani", prenom="Ahmed", cin="AB12345", telephone="0612345678")
        voiture = Voiture.objects.create(marque="Dacia", modele="Duster", immatriculation="AB-456-EF", annee=2023, prix_jour=500)
        reservation = Reservation.objects.create(client=client_obj, voiture=voiture, date_debut=date.today() + timedelta(days=1), date_fin=date.today() + timedelta(days=4), statut="en_attente")
        self._login_as("staff", "staff1234")
        self.client.get(reverse("accepter_reservation", args=[reservation.pk]))
        self.assertTrue(Historique.objects.filter(action="validation", reservation=reservation).exists())

    def test_historique_integration_refuser_reservation(self):
        client_user = User.objects.create_user(username="ahmed", password="client1234")
        client_obj = Client.objects.create(user=client_user, nom="El Amrani", prenom="Ahmed", cin="AB12345", telephone="0612345678")
        voiture = Voiture.objects.create(marque="Dacia", modele="Duster", immatriculation="AB-456-EF", annee=2023, prix_jour=500)
        reservation = Reservation.objects.create(client=client_obj, voiture=voiture, date_debut=date.today() + timedelta(days=1), date_fin=date.today() + timedelta(days=4), statut="en_attente")
        self._login_as("staff", "staff1234")
        self.client.post(reverse("refuser_reservation", args=[reservation.pk]))
        self.assertTrue(Historique.objects.filter(action="refus", reservation=reservation).exists())


# ═══════════════════════════════════════════════════════════
# TESTS RESERVATION (date_retour_reelle + remarque)
# ═══════════════════════════════════════════════════════════

class ReservationRetourTests(TestCase, BaseAuthMixin):
    def setUp(self):
        Group.objects.get_or_create(name="Admin")
        self.user = User.objects.create_user(username="staff", password="staff1234", is_staff=True)
        self.user.groups.add(Group.objects.get(name="Admin"))
        self.client_user = User.objects.create_user(username="ahmed", password="client1234")
        self.client_obj = Client.objects.create(
            user=self.client_user, nom="El Amrani", prenom="Ahmed", cin="AB12345", telephone="0612345678"
        )
        self.voiture = Voiture.objects.create(
            marque="Dacia", modele="Duster", immatriculation="AB-456-EF", annee=2023, prix_jour=500,
            statut="louee",
        )
        self.reservation = Reservation.objects.create(
            client=self.client_obj, voiture=self.voiture,
            date_debut=date.today(), date_fin=date.today() + timedelta(days=2),
            statut="en_cours",
        )

    def test_terminer_avec_remarque(self):
        self._login_as("staff", "staff1234")
        response = self.client.post(reverse("terminer_reservation", args=[self.reservation.pk]), {
            "date_retour_reelle": date.today().isoformat(),
            "remarque": "Véhicule en bon état",
        })
        self.assertRedirects(response, reverse("liste_reservations"))
        self.reservation.refresh_from_db()
        self.assertEqual(self.reservation.statut, "terminee")
        self.assertEqual(self.reservation.date_retour_reelle, date.today())
        self.assertEqual(self.reservation.remarque, "Véhicule en bon état")

    def test_terminer_get_affiche_formulaire(self):
        self._login_as("staff", "staff1234")
        response = self.client.get(reverse("terminer_reservation", args=[self.reservation.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Terminer")

    def test_terminer_sans_remarque(self):
        self._login_as("staff", "staff1234")
        response = self.client.post(reverse("terminer_reservation", args=[self.reservation.pk]), {
            "date_retour_reelle": date.today().isoformat(),
            "remarque": "",
        })
        self.reservation.refresh_from_db()
        self.assertEqual(self.reservation.remarque, "")

    def test_terminer_voiture_redevient_disponible(self):
        self._login_as("staff", "staff1234")
        self.client.post(reverse("terminer_reservation", args=[self.reservation.pk]), {
            "date_retour_reelle": date.today().isoformat(),
            "remarque": "",
        })
        self.voiture.refresh_from_db()
        self.assertEqual(self.voiture.statut, "disponible")

    def test_terminer_historique_enregistre(self):
        self._login_as("staff", "staff1234")
        self.client.post(reverse("terminer_reservation", args=[self.reservation.pk]), {
            "date_retour_reelle": date.today().isoformat(),
            "remarque": "OK",
        })
        self.assertTrue(Historique.objects.filter(action="retour", reservation=self.reservation).exists())

    def test_terminer_client_notifie(self):
        self._login_as("staff", "staff1234")
        self.client.post(reverse("terminer_reservation", args=[self.reservation.pk]), {
            "date_retour_reelle": date.today().isoformat(),
            "remarque": "",
        })
        self.assertTrue(Notification.objects.filter(utilisateur=self.client_user, titre="Réservation terminée").exists())

    def test_terminer_reservation_non_en_cours_echoue(self):
        self.reservation.statut = "en_attente"
        self.reservation.save()
        self._login_as("staff", "staff1234")
        response = self.client.post(reverse("terminer_reservation", args=[self.reservation.pk]), {
            "date_retour_reelle": date.today().isoformat(),
            "remarque": "",
        })
        self.reservation.refresh_from_db()
        self.assertEqual(self.reservation.statut, "en_attente")

    def test_detail_reservation_affiche_retour(self):
        self.reservation.statut = "terminee"
        self.reservation.date_retour_reelle = date.today()
        self.reservation.remarque = "Retour OK"
        self.reservation.save()
        self._login_as("staff", "staff1234")
        response = self.client.get(reverse("detail_reservation", args=[self.reservation.pk]))
        self.assertContains(response, "Retour OK")


# ═══════════════════════════════════════════════════════════
# TESTS NOTIFICATIONS (model + vues + badge)
# ═══════════════════════════════════════════════════════════

class NotificationModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="test1234")

    def test_str_non_lue(self):
        n = Notification.objects.create(utilisateur=self.user, titre="Test", message="Message test")
        self.assertIn("Non lu", str(n))

    def test_str_lue(self):
        n = Notification.objects.create(utilisateur=self.user, titre="Test", message="Message test", lu=True)
        self.assertIn("Lu", str(n))

    def test_ordre_date_creation(self):
        n1 = Notification.objects.create(utilisateur=self.user, titre="Premier", message="1")
        n2 = Notification.objects.create(utilisateur=self.user, titre="Deuxieme", message="2")
        notifs = list(Notification.objects.all())
        self.assertEqual(notifs[0], n2)

    def test_lien_optionnel(self):
        n = Notification.objects.create(utilisateur=self.user, titre="Test", message="Msg")
        self.assertIsNone(n.lien)


class CreerNotificationHelperTests(TestCase):
    def test_creer_notification(self):
        user = User.objects.create_user(username="testuser", password="test1234")
        creer_notification(user, "Titre", "Message", lien="/test/")
        self.assertEqual(Notification.objects.count(), 1)
        n = Notification.objects.first()
        self.assertEqual(n.titre, "Titre")
        self.assertEqual(n.lien, "/test/")

    def test_creer_notification_sans_utilisateur(self):
        creer_notification(None, "Titre", "Message")
        self.assertEqual(Notification.objects.count(), 0)

    def test_creer_notification_sans_lien(self):
        user = User.objects.create_user(username="testuser", password="test1234")
        creer_notification(user, "Titre", "Message")
        n = Notification.objects.first()
        self.assertIsNone(n.lien)


class NotificationViewTests(TestCase, BaseAuthMixin):
    def setUp(self):
        self.user = User.objects.create_user(username="ahmed", password="client1234")
        self.client_obj = Client.objects.create(
            user=self.user, nom="El Amrani", prenom="Ahmed", cin="AB12345", telephone="0612345678"
        )

    def test_liste_notifications(self):
        Notification.objects.create(utilisateur=self.user, titre="Test", message="Msg")
        self._login_as("ahmed", "client1234")
        response = self.client.get(reverse("liste_notifications"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test")

    def test_lire_notification(self):
        n = Notification.objects.create(utilisateur=self.user, titre="Test", message="Msg", lien="/client/dashboard/")
        self._login_as("ahmed", "client1234")
        response = self.client.get(reverse("lire_notification", args=[n.pk]))
        n.refresh_from_db()
        self.assertTrue(n.lu)

    def test_lire_notification_sans_lien_redirige_liste(self):
        n = Notification.objects.create(utilisateur=self.user, titre="Test", message="Msg")
        self._login_as("ahmed", "client1234")
        response = self.client.get(reverse("lire_notification", args=[n.pk]))
        self.assertRedirects(response, reverse("liste_notifications"))

    def test_tout_marquer_lu(self):
        Notification.objects.create(utilisateur=self.user, titre="N1", message="M1")
        Notification.objects.create(utilisateur=self.user, titre="N2", message="M2")
        self._login_as("ahmed", "client1234")
        self.client.post(reverse("tout_marquer_lu"))
        self.assertFalse(self.user.notifications.filter(lu=False).exists())

    def test_notification_autre_utilisateur_inaccessible(self):
        autre = User.objects.create_user(username="autre", password="test1234")
        n = Notification.objects.create(utilisateur=autre, titre="Privé", message="Secret")
        self._login_as("ahmed", "client1234")
        response = self.client.get(reverse("lire_notification", args=[n.pk]))
        self.assertEqual(response.status_code, 404)


# ═══════════════════════════════════════════════════════════
# TESTS PROFIL (modification)
# ═══════════════════════════════════════════════════════════

class ProfilViewTests(TestCase, BaseAuthMixin):
    def setUp(self):
        self.user = User.objects.create_user(username="ahmed", password="client1234", email="ahmed@test.com")
        self.client_obj = Client.objects.create(
            user=self.user, nom="El Amrani", prenom="Ahmed", cin="AB12345", telephone="0612345678"
        )

    def test_profil_get(self):
        self._login_as("ahmed", "client1234")
        response = self.client.get(reverse("modifier_profil"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "ahmed")

    def test_profil_post_modification(self):
        self._login_as("ahmed", "client1234")
        response = self.client.post(reverse("modifier_profil"), {
            "username": "ahmed_updated",
            "email": "new@test.com",
            "first_name": "Ahmed",
            "last_name": "El Amrani",
            "telephone": "0699999999",
            "adresse": "Rue Test, Casablanca",
        })
        self.assertRedirects(response, reverse("modifier_profil"))
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, "ahmed_updated")
        self.assertEqual(self.user.email, "new@test.com")
        self.client_obj.refresh_from_db()
        self.assertEqual(self.client_obj.telephone, "0699999999")
        self.assertEqual(self.client_obj.adresse, "Rue Test, Casablanca")

    def test_profil_username_pris(self):
        User.objects.create_user(username="autre_user", password="test1234")
        self._login_as("ahmed", "client1234")
        response = self.client.post(reverse("modifier_profil"), {
            "username": "autre_user",
            "email": "",
            "first_name": "Ahmed",
            "last_name": "",
            "telephone": "0612345678",
            "adresse": "",
        })
        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, "ahmed")

    def test_profil_sans_client(self):
        user = User.objects.create_user(username="sansclient", password="test1234")
        self.client.login(username="sansclient", password="test1234")
        response = self.client.get(reverse("modifier_profil"))
        self.assertEqual(response.status_code, 200)


# ═══════════════════════════════════════════════════════════
# TESTS DASHBOARD (nouveaux indicateurs)
# ═══════════════════════════════════════════════════════════

class DashboardIndicateurTests(TestCase, BaseAuthMixin):
    def setUp(self):
        Group.objects.get_or_create(name="Admin")
        self.user = User.objects.create_user(username="staff", password="staff1234", is_staff=True)
        self.user.groups.add(Group.objects.get(name="Admin"))
        self.client_user = User.objects.create_user(username="ahmed", password="client1234")
        self.client_obj = Client.objects.create(
            user=self.client_user, nom="El Amrani", prenom="Ahmed", cin="AB12345", telephone="0612345678"
        )
        self.voiture = Voiture.objects.create(
            marque="Dacia", modele="Duster", immatriculation="AB-456-EF", annee=2023, prix_jour=500,
        )

    def test_dashboard_paiements_en_attente(self):
        r = Reservation.objects.create(
            client=self.client_obj, voiture=self.voiture,
            date_debut=date.today(), date_fin=date.today() + timedelta(days=2),
            statut="en_cours",
        )
        Paiement.objects.create(reservation=r, montant=1000, date_paiement=date.today(), statut="en_attente")
        self._login_as("staff", "staff1234")
        response = self.client.get(reverse("dashboard"))
        self.assertEqual(response.context["paiements_en_attente"], 1)

    def test_dashboard_total_recu(self):
        r = Reservation.objects.create(
            client=self.client_obj, voiture=self.voiture,
            date_debut=date.today(), date_fin=date.today() + timedelta(days=2),
            statut="en_cours",
        )
        Paiement.objects.create(reservation=r, montant=1000, date_paiement=date.today(), statut="paye")
        Paiement.objects.create(reservation=r, montant=500, date_paiement=date.today(), statut="paye")
        self._login_as("staff", "staff1234")
        response = self.client.get(reverse("dashboard"))
        self.assertEqual(response.context["total_recu"], 1500)

    def test_dashboard_derniers_retours(self):
        r = Reservation.objects.create(
            client=self.client_obj, voiture=self.voiture,
            date_debut=date.today(), date_fin=date.today() + timedelta(days=2),
            statut="terminee", date_retour_reelle=date.today(),
        )
        self._login_as("staff", "staff1234")
        response = self.client.get(reverse("dashboard"))
        self.assertEqual(len(response.context["derniers_retours"]), 1)

    def test_dashboard_retours_sans_date_reelle_non_affiches(self):
        Reservation.objects.create(
            client=self.client_obj, voiture=self.voiture,
            date_debut=date.today(), date_fin=date.today() + timedelta(days=2),
            statut="terminee",
        )
        self._login_as("staff", "staff1234")
        response = self.client.get(reverse("dashboard"))
        self.assertEqual(len(response.context["derniers_retours"]), 0)


# ═══════════════════════════════════════════════════════════
# TESTS NOTIFICATION NAVBAR (template tag)
# ═══════════════════════════════════════════════════════════

from .templatetags.notifications_tags import nb_notifications_non_lues


class NotificationTemplateTagTests(TestCase):
    def test_aucune_notification(self):
        user = User.objects.create_user(username="testuser", password="test1234")
        self.assertEqual(nb_notifications_non_lues(user), 0)

    def test_notifications_non_lues(self):
        user = User.objects.create_user(username="testuser", password="test1234")
        Notification.objects.create(utilisateur=user, titre="N1", message="M1")
        Notification.objects.create(utilisateur=user, titre="N2", message="M2", lu=True)
        self.assertEqual(nb_notifications_non_lues(user), 1)

    def test_toutes_lues(self):
        user = User.objects.create_user(username="testuser", password="test1234")
        Notification.objects.create(utilisateur=user, titre="N1", message="M1", lu=True)
        self.assertEqual(nb_notifications_non_lues(user), 0)


# ═══════════════════════════════════════════════════════════
# TESTS HISTORIQUE PAGE - FILTRES ET PAGINATION
# ═══════════════════════════════════════════════════════════

class HistoriquePaginationTests(TestCase, BaseAuthMixin):
    def setUp(self):
        Group.objects.get_or_create(name="Admin")
        self.user = User.objects.create_user(username="staff", password="staff1234", is_staff=True)
        self.user.groups.add(Group.objects.get(name="Admin"))

    def test_pagination_historique(self):
        for i in range(25):
            enregistrer_historique("creation", f"Action {i}")
        self._login_as("staff", "staff1234")
        response = self.client.get(reverse("historique"))
        self.assertEqual(len(response.context["page_obj"]), 20)

    def test_historique_filtre_creation(self):
        enregistrer_historique("creation", "Creation test")
        enregistrer_historique("retour", "Retour test")
        enregistrer_historique("paiement", "Paiement test")
        self._login_as("staff", "staff1234")
        response = self.client.get(reverse("historique") + "?action=creation")
        self.assertEqual(len(response.context["page_obj"]), 1)
