import { test } from '@playwright/test';
import path from 'path';

const BASE = 'http://127.0.0.1:8000';
const SCREENSHOT_DIR = path.resolve('rapport_pfa/figures');

async function login(page, username, password) {
  await page.goto(`${BASE}/login/`);
  await page.fill('input[name="username"]', username);
  await page.fill('input[name="password"]', password);
  await page.click('button[type="submit"]');
}

async function screenshot(page, name) {
  await page.screenshot({ path: path.join(SCREENSHOT_DIR, name), fullPage: true });
}

test.describe('Captures écrans', () => {

  test('01 - Page accueil publique', async ({ page }) => {
    await page.goto(BASE);
    await page.waitForLoadState('networkidle');
    await screenshot(page, 'screen_accueil.png');
  });

  test('02 - Formulaire de connexion', async ({ page }) => {
    await page.goto(`${BASE}/login/`);
    await page.waitForLoadState('networkidle');
    await screenshot(page, 'screen_login.png');
  });

  test('03 - Réinitialisation mot de passe', async ({ page }) => {
    await page.goto(`${BASE}/password-reset/`);
    await page.waitForLoadState('networkidle');
    await screenshot(page, 'screen_password_reset.png');
  });

  test('04 - Dashboard admin', async ({ page }) => {
    await login(page, 'admin', 'admin1234');
    await page.waitForURL(`${BASE}/dashboard/`);
    await page.waitForLoadState('networkidle');
    await screenshot(page, 'screen_dashboard_admin.png');
  });

  test('05 - Liste voitures', async ({ page }) => {
    await login(page, 'admin', 'admin1234');
    await page.goto(`${BASE}/voitures/`);
    await page.waitForLoadState('networkidle');
    await screenshot(page, 'screen_voitures_liste.png');
  });

  test('06 - Formulaire ajout voiture', async ({ page }) => {
    await login(page, 'admin', 'admin1234');
    await page.goto(`${BASE}/voitures/ajouter/`);
    await page.waitForLoadState('networkidle');
    await screenshot(page, 'screen_voiture_form.png');
  });

  test('07 - Détail voiture', async ({ page }) => {
    await login(page, 'admin', 'admin1234');
    await page.goto(`${BASE}/voitures/`);
    await page.waitForLoadState('networkidle');
    const detailLink = page.locator('a:has-text("Détail")').first();
    if (await detailLink.isVisible()) {
      await detailLink.click();
      await page.waitForLoadState('networkidle');
    }
    await screenshot(page, 'screen_voiture_detail.png');
  });

  test('08 - Liste clients', async ({ page }) => {
    await login(page, 'admin', 'admin1234');
    await page.goto(`${BASE}/clients/`);
    await page.waitForLoadState('networkidle');
    await screenshot(page, 'screen_clients_liste.png');
  });

  test('09 - Détail client', async ({ page }) => {
    await login(page, 'admin', 'admin1234');
    await page.goto(`${BASE}/clients/`);
    await page.waitForLoadState('networkidle');
    const detailLink = page.locator('a:has-text("Détail")').first();
    if (await detailLink.isVisible()) {
      await detailLink.click();
      await page.waitForLoadState('networkidle');
    }
    await screenshot(page, 'screen_client_detail.png');
  });

  test('10 - Liste réservations', async ({ page }) => {
    await login(page, 'admin', 'admin1234');
    await page.goto(`${BASE}/reservations/`);
    await page.waitForLoadState('networkidle');
    await screenshot(page, 'screen_reservations_liste.png');
  });

  test('11 - Formulaire réservation staff', async ({ page }) => {
    await login(page, 'admin', 'admin1234');
    await page.goto(`${BASE}/reservations/ajouter/`);
    await page.waitForLoadState('networkidle');
    await screenshot(page, 'screen_reservation_form.png');
  });

  test('12 - Détail réservation', async ({ page }) => {
    await login(page, 'admin', 'admin1234');
    await page.goto(`${BASE}/reservations/`);
    await page.waitForLoadState('networkidle');
    const detailLink = page.locator('a:has-text("Détail")').first();
    if (await detailLink.isVisible()) {
      await detailLink.click();
      await page.waitForLoadState('networkidle');
    }
    await screenshot(page, 'screen_reservation_detail.png');
  });

  test('13 - Page statistiques', async ({ page }) => {
    await login(page, 'admin', 'admin1234');
    await page.goto(`${BASE}/statistiques/`);
    await page.waitForLoadState('networkidle');
    await screenshot(page, 'screen_statistiques.png');
  });

  test('14 - Gestion des rôles', async ({ page }) => {
    await login(page, 'admin', 'admin1234');
    await page.goto(`${BASE}/roles/`);
    await page.waitForLoadState('networkidle');
    await screenshot(page, 'screen_gestion_roles.png');
  });

  test('15 - Inscription client', async ({ page }) => {
    await page.goto(`${BASE}/client/register/`);
    await page.waitForLoadState('networkidle');
    await screenshot(page, 'screen_client_register.png');
  });

  test('16 - Dashboard client', async ({ page }) => {
    await login(page, 'ahmed', 'client1234');
    await page.waitForURL(`${BASE}/client/dashboard/`);
    await page.waitForLoadState('networkidle');
    await screenshot(page, 'screen_client_dashboard.png');
  });

  test('17 - Catalogue voitures client', async ({ page }) => {
    await login(page, 'ahmed', 'client1234');
    await page.goto(`${BASE}/client/voitures/`);
    await page.waitForLoadState('networkidle');
    await screenshot(page, 'screen_catalogue_client.png');
  });

  test('18 - Fiche voiture côté client', async ({ page }) => {
    await login(page, 'ahmed', 'client1234');
    await page.goto(`${BASE}/client/voitures/`);
    await page.waitForLoadState('networkidle');
    const cardLink = page.locator('a:has-text("Voir détails")').first();
    if (await cardLink.isVisible()) {
      await cardLink.click();
      await page.waitForLoadState('networkidle');
    }
    await screenshot(page, 'screen_client_detail_voiture.png');
  });

  test('19 - Formulaire réservation client', async ({ page }) => {
    await login(page, 'ahmed', 'client1234');
    await page.goto(`${BASE}/client/reserver/`);
    await page.waitForLoadState('networkidle');
    await screenshot(page, 'screen_client_reservation_form.png');
  });

  test('20 - Vérification AJAX disponibilité', async ({ page }) => {
    await login(page, 'ahmed', 'client1234');
    await page.goto(`${BASE}/client/voitures/`);
    await page.waitForLoadState('networkidle');
    const cardLink = page.locator('a:has-text("Voir détails")').first();
    if (await cardLink.isVisible()) {
      await cardLink.click();
      await page.waitForLoadState('networkidle');
    }
    // Remplir les dates pour déclencher la vérification AJAX
    const dateDebut = page.locator('input[name="date_debut"]');
    const dateFin = page.locator('input[name="date_fin"]');
    if (await dateDebut.isVisible()) {
      const tomorrow = new Date();
      tomorrow.setDate(tomorrow.getDate() + 1);
      const dayAfter = new Date(tomorrow);
      dayAfter.setDate(dayAfter.getDate() + 3);
      await dateDebut.fill(tomorrow.toISOString().split('T')[0]);
      await dateFin.fill(dayAfter.toISOString().split('T')[0]);
      await page.waitForTimeout(1000);
    }
    await screenshot(page, 'screen_client_availability_ajax.png');
  });

  test('21 - Facture PDF', async ({ page }) => {
    await login(page, 'admin', 'admin1234');
    await page.goto(`${BASE}/reservations/`);
    await page.waitForLoadState('networkidle');
    // Capturer la page liste réservations avec les boutons PDF visibles
    await screenshot(page, 'screen_facture_pdf.png');
  });

  test('22 - Rapport PDF global', async ({ page }) => {
    await login(page, 'admin', 'admin1234');
    await page.goto(`${BASE}/statistiques/`);
    await page.waitForLoadState('networkidle');
    await screenshot(page, 'screen_rapport_pdf.png');
  });

  test('23 - Page 404', async ({ page }) => {
    await page.goto(`${BASE}/page-inexistante/`);
    await page.waitForLoadState('networkidle');
    await screenshot(page, 'screen_404.png');
  });

});
