import { test, expect } from '@playwright/test';

const BASE = 'http://127.0.0.1:8000';

async function login(page, username, password) {
  await page.goto(`${BASE}/login/`);
  await page.fill('input[name="username"]', username);
  await page.fill('input[name="password"]', password);
  await page.click('button[type="submit"]');
}

// ========== AUTH ==========

test('page accueil publique', async ({ page }) => {
  await page.goto(BASE);
  await expect(page.locator('h1')).toContainText('Location');
});

test('login admin redirige vers dashboard', async ({ page }) => {
  await login(page, 'admin', 'admin1234');
  await expect(page).toHaveURL(`${BASE}/dashboard/`);
  await expect(page.locator('h1')).toContainText('Tableau de bord');
});

test('login client redirige vers espace client', async ({ page }) => {
  await login(page, 'ahmed', 'client1234');
  await expect(page).toHaveURL(`${BASE}/client/dashboard/`);
});

test('mauvais identifiants affiche erreur', async ({ page }) => {
  await page.goto(`${BASE}/login/`);
  await page.fill('input[name="username"]', 'admin');
  await page.fill('input[name="password"]', 'faux');
  await page.click('button[type="submit"]');
  await expect(page.locator('.alert, .alert-danger').first()).toBeVisible();
});

test('acces dashboard sans login redirige', async ({ page }) => {
  await page.goto(`${BASE}/dashboard/`);
  await expect(page).toHaveURL(/login/);
});

test('logout fonctionne', async ({ page }) => {
  await login(page, 'admin', 'admin1234');
  await expect(page).toHaveURL(`${BASE}/dashboard/`);
  await page.click('a:has-text("Déconnexion")');
  await expect(page).toHaveURL(/login/);
});

// ========== NAVIGATION ==========

test('navigation admin complete', async ({ page }) => {
  await login(page, 'admin', 'admin1234');

  await page.click('a:has-text("Voitures")');
  await expect(page).toHaveURL(`${BASE}/voitures/`);
  await expect(page.locator('h1')).toContainText('voitures');

  await page.click('a:has-text("Clients")');
  await expect(page).toHaveURL(`${BASE}/clients/`);

  await page.click('a:has-text("Réservations")');
  await expect(page).toHaveURL(`${BASE}/reservations/`);

  await page.click('a:has-text("Dashboard")');
  await expect(page).toHaveURL(`${BASE}/dashboard/`);
});

// ========== VOITURES (display, search, detail) ==========

test('liste voitures accessible', async ({ page }) => {
  await login(page, 'admin', 'admin1234');
  await page.goto(`${BASE}/voitures/`);
  const rows = page.locator('tbody tr');
  expect(await rows.count()).toBeGreaterThan(0);
});

test('filtre voitures par statut', async ({ page }) => {
  await login(page, 'admin', 'admin1234');
  await page.goto(`${BASE}/voitures/`);
  await page.selectOption('select[name="statut"]', 'disponible');
  await page.click('button:has-text("Filtrer")');
  const rows = page.locator('tbody tr');
  expect(await rows.count()).toBeGreaterThan(0);
});

test('recherche voiture par mot-cle', async ({ page }) => {
  await login(page, 'admin', 'admin1234');
  await page.goto(`${BASE}/voitures/`);
  await page.fill('input[name="q"]', 'Renault');
  await page.press('input[name="q"]', 'Enter');
  await page.waitForTimeout(500);
  const rows = page.locator('tbody tr');
  expect(await rows.count()).toBeGreaterThan(0);
});

test('detail voiture', async ({ page }) => {
  await login(page, 'admin', 'admin1234');
  await page.goto(`${BASE}/voitures/`);
  const detailLink = page.locator('a:has-text("Détail")').first();
  if (await detailLink.isVisible()) {
    await detailLink.click();
    await expect(page.locator('body')).toContainText('Immatriculation');
  }
});

// ========== FORMULAIRES VOITURE (via API POST validant) ==========

test('formulaire ajout voiture affiche la page', async ({ page }) => {
  await login(page, 'admin', 'admin1234');
  await page.goto(`${BASE}/voitures/ajouter/`);
  await expect(page.locator('h1')).toContainText('Ajouter');
});

test('formulaire modification voiture affiche la page', async ({ page }) => {
  await login(page, 'admin', 'admin1234');
  await page.goto(`${BASE}/voitures/`);
  const editLink = page.locator('a.btn-warning').first();
  if (await editLink.isVisible()) {
    await editLink.click();
    await expect(page.locator('h1')).toContainText('Modifier');
  }
});

test('formulaire suppression voiture affiche confirmation', async ({ page }) => {
  await login(page, 'admin', 'admin1234');
  await page.goto(`${BASE}/voitures/`);
  const deleteLink = page.locator('a.btn-danger').first();
  if (await deleteLink.isVisible()) {
    await deleteLink.click();
    await expect(page.locator('h1')).toContainText('Confirmation');
  }
});

// ========== CLIENTS ==========

test('liste clients accessible', async ({ page }) => {
  await login(page, 'admin', 'admin1234');
  await page.goto(`${BASE}/clients/`);
  await expect(page.locator('tbody')).toContainText('El Amrani');
});

test('recherche client', async ({ page }) => {
  await login(page, 'admin', 'admin1234');
  await page.goto(`${BASE}/clients/`);
  await page.fill('input[name="q"]', 'El Amrani');
  await page.click('button:has-text("Rechercher")');
  await expect(page.locator('tbody')).toContainText('El Amrani');
});

test('formulaire ajout client affiche la page', async ({ page }) => {
  await login(page, 'admin', 'admin1234');
  await page.goto(`${BASE}/clients/ajouter/`);
  await expect(page.locator('h1')).toContainText('Ajouter');
});

// ========== RESERVATIONS ==========

test('liste reservations accessible', async ({ page }) => {
  await login(page, 'admin', 'admin1234');
  await page.goto(`${BASE}/reservations/`);
  const rows = page.locator('tbody tr');
  expect(await rows.count()).toBeGreaterThan(0);
});

test('filtrer reservations par statut', async ({ page }) => {
  await login(page, 'admin', 'admin1234');
  await page.goto(`${BASE}/reservations/`);
  await page.selectOption('select[name="statut"]', 'en_cours');
  await page.click('button:has-text("Filtrer")');
  const pageLoaded = await page.locator('tbody').isVisible();
  expect(pageLoaded).toBe(true);
});

test('detail reservation', async ({ page }) => {
  await login(page, 'admin', 'admin1234');
  await page.goto(`${BASE}/reservations/`);
  const detailLink = page.locator('a:has-text("Détail")').first();
  if (await detailLink.isVisible()) {
    await detailLink.click();
    await expect(page.locator('body')).toContainText('Client');
  }
});

test('formulaire reservation affiche la page', async ({ page }) => {
  await login(page, 'admin', 'admin1234');
  await page.goto(`${BASE}/reservations/ajouter/`);
  await expect(page.locator('h1')).toContainText('Nouvelle');
});

// ========== AJAX ACTION (accepter via API) ==========

test('accepter reservation via bouton admin', async ({ page }) => {
  await login(page, 'admin', 'admin1234');
  await page.goto(`${BASE}/reservations/`);
  await page.selectOption('select[name="statut"]', 'en_attente');
  const acceptBtn = page.locator('button:has-text("Accepter")').first();
  if (await acceptBtn.isVisible()) {
    page.on('dialog', dialog => dialog.accept());
    await acceptBtn.click();
    await page.waitForTimeout(1000);
  }
});

// ========== EXPORTS CSV ==========

test('export CSV voitures telechargeable', async ({ page }) => {
  await login(page, 'admin', 'admin1234');
  await page.goto(`${BASE}/voitures/`);
  const [download] = await Promise.all([
    page.waitForEvent('download'),
    page.click('a:has-text("Exporter CSV")'),
  ]);
  expect(download.suggestedFilename()).toContain('.csv');
});

test('export CSV clients telechargeable', async ({ page }) => {
  await login(page, 'admin', 'admin1234');
  await page.goto(`${BASE}/clients/`);
  const [download] = await Promise.all([
    page.waitForEvent('download'),
    page.click('a:has-text("Exporter CSV")'),
  ]);
  expect(download.suggestedFilename()).toContain('.csv');
});

// ========== PDF ==========

test('facture PDF telechargeable', async ({ page }) => {
  await login(page, 'admin', 'admin1234');
  await page.goto(`${BASE}/reservations/`);
  const pdfLink = page.locator('a:has-text("PDF")').first();
  if (await pdfLink.isVisible()) {
    const [download] = await Promise.all([
      page.waitForEvent('download'),
      pdfLink.click(),
    ]);
    expect(download.suggestedFilename()).toContain('.pdf');
  }
});

// ========== STATISTIQUES ==========

test('page statistiques accessible', async ({ page }) => {
  await login(page, 'admin', 'admin1234');
  await page.goto(`${BASE}/statistiques/`);
  await expect(page.locator('h1')).toContainText('Statistiques');
});

// ========== ESPACE CLIENT ==========

test('inscription nouveau client', async ({ page }) => {
  const uniqueId = Date.now();
  await page.goto(`${BASE}/client/register/`);
  await page.fill('input[name="username"]', `e2eclient${uniqueId}`);
  await page.fill('input[name="nom"]', 'E2E');
  await page.fill('input[name="prenom"]', 'Inscrit');
  await page.fill('input[name="cin"]', `E2E-CIN-${uniqueId}`);
  await page.fill('input[name="telephone"]', '0600000000');
  await page.fill('input[name="password1"]', 'ComplexePass123!');
  await page.fill('input[name="password2"]', 'ComplexePass123!');
  await page.click('button[type="submit"]');
  await expect(page).toHaveURL(`${BASE}/client/dashboard/`);
});

test('page inscription affiche le formulaire', async ({ page }) => {
  await page.goto(`${BASE}/client/register/`);
  await expect(page.locator('body')).toContainText('Créer un compte');
});

test('client dashboard affiche les compteurs', async ({ page }) => {
  await login(page, 'ahmed', 'client1234');
  await expect(page).toHaveURL(`${BASE}/client/dashboard/`);
  await expect(page.locator('h1')).toContainText('Mon espace');
});

test('page demande reservation client accessible', async ({ page }) => {
  await login(page, 'ahmed', 'client1234');
  await page.goto(`${BASE}/client/reserver/`);
  await expect(page.locator('h1')).toContainText('Nouvelle');
});

// ========== RBAC ==========

test('admin accede a gestion roles', async ({ page }) => {
  await login(page, 'admin', 'admin1234');
  await page.goto(`${BASE}/roles/`);
  await expect(page.locator('h1')).toContainText('Gestion des utilisateurs');
});

test('employe bloque gestion roles', async ({ page }) => {
  await login(page, 'employe', 'employe1234');
  await page.goto(`${BASE}/roles/`);
  await expect(page).toHaveURL(/dashboard/);
});

// ========== HANDLERS ==========

test('page 404 fonctionnelle', async ({ page }) => {
  await page.goto(`${BASE}/page-inexistante/`);
  await expect(page.locator('body')).toContainText('404');
});

// ========== DASHBOARD ==========

test('dashboard affiche stats', async ({ page }) => {
  await login(page, 'admin', 'admin1234');
  await expect(page.locator('body')).toContainText('Dashboard');
  await expect(page.locator('body')).toContainText('Voitures');
});

test('employe accede au dashboard', async ({ page }) => {
  await login(page, 'employe', 'employe1234');
  await expect(page).toHaveURL(`${BASE}/dashboard/`);
});
