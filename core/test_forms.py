from django.test import TestCase
from django.contrib.auth.models import User
from .forms import (
    VoitureForm, ClientForm, ReservationForm, ClientReservationForm, ClientRegistrationForm,
    CategorieForm, PaiementForm, TerminerReservationForm, ProfilForm,
)
from .models import Voiture, Client, Reservation, Categorie, Paiement
from datetime import date, timedelta


class VoitureFormTests(TestCase):
    def test_voiture_form_valide(self):
        form = VoitureForm({
            "marque": "Renault",
            "modele": "Clio",
            "immatriculation": "XX-123-YY",
            "annee": 2022,
            "prix_jour": 300,
            "statut": "disponible",
        })
        self.assertTrue(form.is_valid())

    def test_voiture_form_champ_manquant(self):
        form = VoitureForm({
            "marque": "",
            "modele": "Clio",
            "immatriculation": "XX-123-YY",
            "annee": 2022,
            "prix_jour": 300,
        })
        self.assertFalse(form.is_valid())
        self.assertIn("marque", form.errors)

    def test_voiture_form_immatriculation_unique(self):
        Voiture.objects.create(
            marque="Test", modele="Test", immatriculation="XX-123-YY", annee=2022, prix_jour=300,
        )
        form = VoitureForm({
            "marque": "Renault",
            "modele": "Clio",
            "immatriculation": "XX-123-YY",
            "annee": 2022,
            "prix_jour": 300,
        })
        self.assertFalse(form.is_valid())
        self.assertIn("immatriculation", form.errors)

    def test_voiture_form_modification_immat_identique_ok(self):
        v = Voiture.objects.create(
            marque="Test", modele="Test", immatriculation="XX-123-YY", annee=2022, prix_jour=300,
        )
        form = VoitureForm({
            "marque": "Renault",
            "modele": "Clio",
            "immatriculation": "XX-123-YY",
            "annee": 2022,
            "prix_jour": 300,
            "statut": "disponible",
        }, instance=v)
        self.assertTrue(form.is_valid())


class ClientFormTests(TestCase):
    def test_client_form_valide(self):
        form = ClientForm({
            "nom": "El Amrani",
            "prenom": "Ahmed",
            "cin": "AB12345",
            "telephone": "0612345678",
        })
        self.assertTrue(form.is_valid())

    def test_client_form_champ_manquant(self):
        form = ClientForm({
            "nom": "",
            "prenom": "",
            "cin": "AB12345",
            "telephone": "0612345678",
        })
        self.assertFalse(form.is_valid())
        self.assertIn("nom", form.errors)

    def test_client_form_cin_unique(self):
        Client.objects.create(
            nom="Exist", prenom="Client", cin="AB12345", telephone="0600000000"
        )
        form = ClientForm({
            "nom": "New",
            "prenom": "Client",
            "cin": "AB12345",
            "telephone": "0600000000",
        })
        self.assertFalse(form.is_valid())
        self.assertIn("cin", form.errors)

    def test_client_form_sans_email(self):
        form = ClientForm({
            "nom": "Sans",
            "prenom": "Email",
            "cin": "NOEML01",
            "telephone": "0600000000",
        })
        self.assertTrue(form.is_valid())

    def test_client_form_avec_email(self):
        form = ClientForm({
            "nom": "Avec",
            "prenom": "Email",
            "cin": "WITHEML",
            "telephone": "0600000000",
            "email": "test@example.com",
        })
        self.assertTrue(form.is_valid())


class ReservationFormTests(TestCase):
    def setUp(self):
        self.client_obj = Client.objects.create(
            nom="Test", prenom="Client", cin="RF001", telephone="0600000000"
        )
        self.voiture = Voiture.objects.create(
            marque="Dacia", modele="Duster", immatriculation="RF-001-ZZ", annee=2023, prix_jour=500,
        )

    def test_reservation_form_valide(self):
        form = ReservationForm({
            "client": self.client_obj.pk,
            "voiture": self.voiture.pk,
            "date_debut": (date.today() + timedelta(days=1)).isoformat(),
            "date_fin": (date.today() + timedelta(days=4)).isoformat(),
        })
        self.assertTrue(form.is_valid())

    def test_reservation_form_client_manquant(self):
        form = ReservationForm({
            "voiture": self.voiture.pk,
            "date_debut": (date.today() + timedelta(days=1)).isoformat(),
            "date_fin": (date.today() + timedelta(days=4)).isoformat(),
        })
        self.assertFalse(form.is_valid())
        self.assertIn("client", form.errors)

    def test_reservation_form_voiture_manquante(self):
        form = ReservationForm({
            "client": self.client_obj.pk,
            "date_debut": (date.today() + timedelta(days=1)).isoformat(),
            "date_fin": (date.today() + timedelta(days=4)).isoformat(),
        })
        self.assertFalse(form.is_valid())
        self.assertIn("voiture", form.errors)


class ClientReservationFormTests(TestCase):
    def setUp(self):
        self.voiture = Voiture.objects.create(
            marque="Dacia", modele="Duster", immatriculation="CRF-001-ZZ", annee=2023, prix_jour=500,
        )

    def test_client_form_valide(self):
        form = ClientReservationForm({
            "voiture": self.voiture.pk,
            "date_debut": (date.today() + timedelta(days=1)).isoformat(),
            "date_fin": (date.today() + timedelta(days=4)).isoformat(),
        })
        self.assertTrue(form.is_valid())

    def test_client_form_pas_de_champ_client(self):
        form = ClientReservationForm({
            "voiture": self.voiture.pk,
            "date_debut": (date.today() + timedelta(days=1)).isoformat(),
            "date_fin": (date.today() + timedelta(days=4)),
        })
        self.assertNotIn("client", form.fields)

    def test_client_form_voiture_manquante(self):
        form = ClientReservationForm({
            "date_debut": (date.today() + timedelta(days=1)).isoformat(),
            "date_fin": (date.today() + timedelta(days=4)),
        })
        self.assertFalse(form.is_valid())


class ClientRegistrationFormTests(TestCase):
    def test_register_form_valide(self):
        form = ClientRegistrationForm({
            "username": "nouveau",
            "nom": "Test",
            "prenom": "User",
            "cin": "REG99999",
            "telephone": "0600000000",
            "password1": "ComplexPass123!",
            "password2": "ComplexPass123!",
        })
        self.assertTrue(form.is_valid())

    def test_register_cin_unique(self):
        User.objects.create_user(username="exist", password="test1234")
        Client.objects.create(
            nom="Exist", prenom="Client", cin="REG88888", telephone="0600000000"
        )
        form = ClientRegistrationForm({
            "username": "nouveau",
            "nom": "Test",
            "prenom": "User",
            "cin": "REG88888",
            "telephone": "0600000000",
            "password1": "ComplexPass123!",
            "password2": "ComplexPass123!",
        })
        self.assertFalse(form.is_valid())
        self.assertIn("cin", form.errors)

    def test_register_passwords_mismatch(self):
        form = ClientRegistrationForm({
            "username": "nouveau",
            "nom": "Test",
            "prenom": "User",
            "cin": "DIFF01",
            "telephone": "0600000000",
            "password1": "ComplexPass123!",
            "password2": "WrongPass456!",
        })
        self.assertFalse(form.is_valid())
        self.assertIn("password2", form.errors)

    def test_register_champs_obligatoires(self):
        form = ClientRegistrationForm({
            "username": "",
            "nom": "",
            "prenom": "",
            "cin": "",
            "telephone": "",
            "password1": "",
            "password2": "",
        })
        self.assertFalse(form.is_valid())
        self.assertIn("username", form.errors)
        self.assertIn("nom", form.errors)
        self.assertIn("cin", form.errors)

    def test_register_save_creer_user_et_client(self):
        form = ClientRegistrationForm({
            "username": "newuser",
            "nom": "Sauve",
            "prenom": "Garde",
            "cin": "SAVE01",
            "telephone": "0600000000",
            "email": "save@example.com",
            "password1": "ComplexPass123!",
            "password2": "ComplexPass123!",
        })
        self.assertTrue(form.is_valid())
        user = form.save()
        self.assertEqual(user.username, "newuser")
        self.assertTrue(hasattr(user, "client"))
        self.assertEqual(user.client.cin, "SAVE01")
        self.assertEqual(user.client.nom, "Sauve")


class CategorieFormTests(TestCase):
    def test_categorie_form_valide(self):
        form = CategorieForm({"nom": "SUV", "description": "Vehicules tout-terrain"})
        self.assertTrue(form.is_valid())

    def test_categorie_form_nom_manquant(self):
        form = CategorieForm({"nom": "", "description": "Test"})
        self.assertFalse(form.is_valid())
        self.assertIn("nom", form.errors)


class PaiementFormTests(TestCase):
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

    def test_paiement_form_valide(self):
        form = PaiementForm({
            "montant": "1500",
            "date_paiement": date.today().isoformat(),
            "mode_paiement": "especes",
            "statut": "paye",
        })
        self.assertTrue(form.is_valid())

    def test_paiement_form_montant_manquant(self):
        form = PaiementForm({
            "date_paiement": date.today().isoformat(),
            "mode_paiement": "especes",
            "statut": "paye",
        })
        self.assertFalse(form.is_valid())
        self.assertIn("montant", form.errors)

    def test_paiement_form_statut_defaut(self):
        form = PaiementForm({
            "montant": "500",
            "date_paiement": date.today().isoformat(),
            "mode_paiement": "especes",
            "statut": "en_attente",
        })
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["statut"], "en_attente")


class TerminerReservationFormTests(TestCase):
    def test_valide(self):
        form = TerminerReservationForm({
            "date_retour_reelle": date.today().isoformat(),
            "remarque": "Bon état",
        })
        self.assertTrue(form.is_valid())

    def test_date_manquante(self):
        form = TerminerReservationForm({"remarque": "Test"})
        self.assertFalse(form.is_valid())
        self.assertIn("date_retour_reelle", form.errors)

    def test_remarque_optionnelle(self):
        form = TerminerReservationForm({"date_retour_reelle": date.today().isoformat()})
        self.assertTrue(form.is_valid())


class ProfilFormTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="test1234", email="test@test.com")
        Client.objects.create(
            user=self.user, nom="Test", prenom="User", cin="PROF01", telephone="0600000000"
        )

    def test_profil_form_valide(self):
        form = ProfilForm({
            "username": "testuser",
            "email": "test@test.com",
            "first_name": "Test",
            "last_name": "User",
            "telephone": "0600000000",
            "adresse": "Rue Test",
        }, user=self.user)
        self.assertTrue(form.is_valid())

    def test_profil_form_username_pris(self):
        User.objects.create_user(username="autre", password="test1234")
        form = ProfilForm({
            "username": "autre",
            "email": "",
            "first_name": "",
            "last_name": "",
            "telephone": "0600000000",
            "adresse": "",
        }, user=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn("username", form.errors)

    def test_profil_form_sauvegarde(self):
        form = ProfilForm({
            "username": "newname",
            "email": "new@test.com",
            "first_name": "New",
            "last_name": "Name",
            "telephone": "0699999999",
            "adresse": "New Addr",
        }, user=self.user)
        self.assertTrue(form.is_valid())
        form.save()
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, "newname")
        self.user.client.refresh_from_db()
        self.assertEqual(self.user.client.telephone, "0699999999")
