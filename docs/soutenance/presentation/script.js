/* ============================================
   PFA Presentation — Script
   Animations + PPTX Export (PptxGenJS)
   ============================================ */

// ---------- Reveal.js Initialization ----------
document.addEventListener('DOMContentLoaded', () => {
  // Remove loading overlay
  setTimeout(() => {
    const overlay = document.querySelector('.loading-overlay');
    if (overlay) {
      overlay.style.opacity = '0';
      setTimeout(() => overlay.remove(), 500);
    }
  }, 800);

  Reveal.initialize({
    hash: true,
    slideNumber: false,
    controls: false,
    progress: false,
    center: false,
    transition: 'slide',
    transitionSpeed: 'default',
    backgroundTransition: 'fade',
    width: 1920,
    height: 1080,
    margin: 0.04,
    minScale: 0.2,
    maxScale: 2.0,
    keyboard: true,
    overview: true,
    touch: true,
  });

  // Slide counter
  const counter = document.getElementById('slideCounter');
  Reveal.on('slidechanged', (event) => {
    if (counter) {
      counter.textContent = `${event.indexh + 1} / ${Reveal.getTotalSlides()}`;
    }
  });

  // Animate elements on slide change
  Reveal.on('slidechanged', (event) => {
    const slide = event.currentSlide;
    if (!slide) return;

    // Reset and trigger animations
    const animated = slide.querySelectorAll('.fade-in, .slide-up, .zoom-in');
    animated.forEach((el, i) => {
      el.style.animation = 'none';
      el.offsetHeight; // trigger reflow
      el.style.animation = '';
      el.style.animationDelay = `${i * 0.1}s`;
    });

    // Animate progress bars
    const progressBars = slide.querySelectorAll('.progress-fill');
    progressBars.forEach(bar => {
      const width = bar.getAttribute('data-width');
      if (width) {
        bar.style.width = '0%';
        setTimeout(() => { bar.style.width = width; }, 300);
      }
    });

    // Animate stat numbers
    const statNumbers = slide.querySelectorAll('.stat-number[data-count]');
    statNumbers.forEach(el => {
      animateCounter(el, parseInt(el.getAttribute('data-count')));
    });
  });
});

// ---------- Counter Animation ----------
function animateCounter(element, target) {
  let current = 0;
  const duration = 1500;
  const increment = target / (duration / 16);

  element.textContent = '0';

  const timer = setInterval(() => {
    current += increment;
    if (current >= target) {
      current = target;
      clearInterval(timer);
    }
    element.textContent = Math.floor(current);
  }, 16);
}

// ---------- PPTX Export ----------
async function exportToPPTX() {
  const btn = document.querySelector('.export-pptx-btn');
  if (btn) {
    btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Export en cours...';
    btn.disabled = true;
  }

  try {
    const pptx = new PptxGenJS();
    pptx.layout = 'LAYOUT_WIDE';
    pptx.author = 'Kawtar Benyoussef';
    pptx.company = 'EMSI';
    pptx.subject = 'PFA - Gestion de Location de Voitures';
    pptx.title = 'Application Web de Gestion de Location de Voitures';

    const PRIMARY = '0F172A';
    const SECONDARY = '2563EB';
    const ACCENT = '3B82F6';
    const WHITE = 'FFFFFF';
    const GRAY = '94A3B8';
    const GRAY_LIGHT = 'F1F5F9';
    const SUCCESS = '10B981';
    const WARNING = 'F59E0B';
    const DANGER = 'EF4444';

    // ===== Slide 1: Cover =====
    let slide = pptx.addSlide();
    slide.background = { fill: PRIMARY };
    slide.addShape(pptx.ShapeType.rect, { x: 0, y: 0, w: '100%', h: 0.08, fill: { color: SECONDARY } });
    slide.addText('🚗', { x: 4.3, y: 1.2, w: 1.4, h: 1, fontSize: 54, align: 'center' });
    slide.addText('Application Web de\nGestion de Location de Voitures', {
      x: 1, y: 2.4, w: 8, h: 1.6, fontSize: 32, fontFace: 'Poppins',
      color: WHITE, bold: true, align: 'center', lineSpacingMultiple: 1.2
    });
    slide.addShape(pptx.ShapeType.rect, { x: 4.3, y: 4.1, w: 1.4, h: 0.05, fill: { color: SECONDARY } });
    slide.addText('PFA 2025-2026', {
      x: 1, y: 4.4, w: 8, h: 0.5, fontSize: 16, fontFace: 'Poppins',
      color: GRAY, align: 'center'
    });
    slide.addText([
      { text: 'Kawtar Benyoussef', options: { fontSize: 18, bold: true, color: WHITE } },
      { text: '\nEncadré par Pr. Houda Orchi', options: { fontSize: 14, color: GRAY } },
      { text: '\nEMSI - École Mohammadia d\'Ingénieurs', options: { fontSize: 13, color: GRAY } }
    ], { x: 1, y: 5.0, w: 8, h: 1.5, align: 'center', fontFace: 'Poppins', lineSpacingMultiple: 1.4 });

    // ===== Slide 2: Context =====
    slide = pptx.addSlide();
    slide.background = { fill: PRIMARY };
    slide.addShape(pptx.ShapeType.rect, { x: 0, y: 0, w: '100%', h: 0.06, fill: { color: SECONDARY } });
    slide.addText('01  Contexte du Projet', {
      x: 0.6, y: 0.3, w: 9, h: 0.6, fontSize: 26, fontFace: 'Poppins',
      color: WHITE, bold: true
    });
    slide.addShape(pptx.ShapeType.rect, { x: 0.6, y: 0.95, w: 1.5, h: 0.04, fill: { color: SECONDARY } });

    const contextItems = [
      { icon: '🏢', title: 'Secteur en croissance', desc: 'Le marché de la location de voitures au Maroc connaît une forte demande, notamment pour les déplacements professionnels et le tourisme.' },
      { icon: '📋', title: 'Gestion manuelle', desc: 'Les agences utilisent encore des registres papier ou des fichiers Excel, causant des pertes de données et des erreurs de suivi.' },
      { icon: '⏱️', title: 'Besoin de digitalisation', desc: 'Nécessité d\'une solution web centralisée pour gérer les véhicules, clients, réservations et paiements en temps réel.' },
      { icon: '🎯', title: 'Objectif du PFA', desc: 'Développer une application web complète avec Django pour automatiser et optimiser la gestion de location de voitures.' }
    ];

    contextItems.forEach((item, i) => {
      const y = 1.3 + i * 1.2;
      slide.addShape(pptx.ShapeType.roundRect, {
        x: 0.6, y: y, w: 9, h: 1.0, rectRadius: 0.1,
        fill: { color: '1E293B' }, line: { color: '334155', width: 1 }
      });
      slide.addText(item.icon, { x: 0.8, y: y + 0.15, w: 0.7, h: 0.7, fontSize: 28, align: 'center' });
      slide.addText(item.title, { x: 1.6, y: y + 0.1, w: 7.5, h: 0.4, fontSize: 16, fontFace: 'Poppins', color: WHITE, bold: true });
      slide.addText(item.desc, { x: 1.6, y: y + 0.5, w: 7.5, h: 0.45, fontSize: 11, fontFace: 'Poppins', color: GRAY });
    });

    // ===== Slide 3: Problématique =====
    slide = pptx.addSlide();
    slide.background = { fill: PRIMARY };
    slide.addShape(pptx.ShapeType.rect, { x: 0, y: 0, w: '100%', h: 0.06, fill: { color: SECONDARY } });
    slide.addText('02  Problématique', {
      x: 0.6, y: 0.3, w: 9, h: 0.6, fontSize: 26, fontFace: 'Poppins',
      color: WHITE, bold: true
    });
    slide.addShape(pptx.ShapeType.rect, { x: 0.6, y: 0.95, w: 1.5, h: 0.04, fill: { color: SECONDARY } });

    const problems = [
      { icon: '❌', text: 'Suivi manuel des véhicules → erreurs de disponibilité et doublons de réservation' },
      { icon: '❌', text: 'Absence de historique centralisé → difficultés d\'audit et de traçabilité' },
      { icon: '❌', text: 'Gestion des paiements non structurée → risques de pertes financières' },
      { icon: '❌', text: 'Pas de tableau de bord → absence d\'indicateurs de performance' },
      { icon: '❌', text: 'Communication client limitée → pas de notifications en temps réel' }
    ];

    problems.forEach((p, i) => {
      const y = 1.3 + i * 1.0;
      slide.addShape(pptx.ShapeType.roundRect, {
        x: 0.6, y: y, w: 9, h: 0.8, rectRadius: 0.08,
        fill: { color: '1E293B' }, line: { color: '334155', width: 1 }
      });
      slide.addText(p.icon, { x: 0.8, y: y + 0.1, w: 0.6, h: 0.6, fontSize: 22, align: 'center' });
      slide.addText(p.text, { x: 1.5, y: y + 0.15, w: 7.8, h: 0.5, fontSize: 13, fontFace: 'Poppins', color: WHITE });
    });

    slide.addShape(pptx.ShapeType.roundRect, {
      x: 0.6, y: 6.3, w: 9, h: 0.7, rectRadius: 0.08,
      fill: { color: SECONDARY }
    });
    slide.addText('→ Comment concevoir une application web fiable, sécurisée et performante pour la gestion de location de voitures ?', {
      x: 0.8, y: 6.35, w: 8.6, h: 0.6, fontSize: 13, fontFace: 'Poppins', color: WHITE, bold: true, align: 'center'
    });

    // ===== Slide 4: Objectifs =====
    slide = pptx.addSlide();
    slide.background = { fill: PRIMARY };
    slide.addShape(pptx.ShapeType.rect, { x: 0, y: 0, w: '100%', h: 0.06, fill: { color: SECONDARY } });
    slide.addText('03  Objectifs du Projet', {
      x: 0.6, y: 0.3, w: 9, h: 0.6, fontSize: 26, fontFace: 'Poppins',
      color: WHITE, bold: true
    });
    slide.addShape(pptx.ShapeType.rect, { x: 0.6, y: 0.95, w: 1.5, h: 0.04, fill: { color: SECONDARY } });

    // Functional objectives
    slide.addText('Objectifs Fonctionnels', {
      x: 0.6, y: 1.2, w: 4.5, h: 0.4, fontSize: 16, fontFace: 'Poppins',
      color: ACCENT, bold: true
    });

    const funcObj = [
      'Gestion complète des véhicules (CRUD)',
      'Gestion des clients et inscriptions',
      'Workflow de réservation complet',
      'Suivi des paiements',
      'Tableau de bord et statistiques',
      'Notifications et historique'
    ];

    funcObj.forEach((item, i) => {
      slide.addText(`✓  ${item}`, {
        x: 0.8, y: 1.7 + i * 0.45, w: 4.2, h: 0.4, fontSize: 12, fontFace: 'Poppins', color: WHITE
      });
    });

    // Technical objectives
    slide.addText('Objectifs Techniques', {
      x: 5.2, y: 1.2, w: 4.5, h: 0.4, fontSize: 16, fontFace: 'Poppins',
      color: ACCENT, bold: true
    });

    const techObj = [
      'Architecture MVT Django propre',
      'Système RBAC (3 rôles)',
      'Sécurité (CSRF, validation)',
      'Exports PDF (ReportLab) et CSV',
      'Tests unitaires + E2E (Playwright)',
      'Interface responsive et AJAX'
    ];

    techObj.forEach((item, i) => {
      slide.addText(`✓  ${item}`, {
        x: 5.4, y: 1.7 + i * 0.45, w: 4.2, h: 0.4, fontSize: 12, fontFace: 'Poppins', color: WHITE
      });
    });

    // Stats row
    const stats = [
      { num: '7', label: 'Modèles' },
      { num: '55+', label: 'Vues' },
      { num: '42', label: 'Routes URL' },
      { num: '39', label: 'Templates' },
      { num: '110+', label: 'Tests' }
    ];

    stats.forEach((s, i) => {
      const x = 0.6 + i * 1.9;
      slide.addShape(pptx.ShapeType.roundRect, {
        x: x, y: 5.2, w: 1.7, h: 1.2, rectRadius: 0.1,
        fill: { color: '1E293B' }, line: { color: SECONDARY, width: 1.5 }
      });
      slide.addText(s.num, { x: x, y: 5.3, w: 1.7, h: 0.65, fontSize: 28, fontFace: 'Poppins', color: ACCENT, bold: true, align: 'center' });
      slide.addText(s.label, { x: x, y: 5.9, w: 1.7, h: 0.4, fontSize: 11, fontFace: 'Poppins', color: GRAY, align: 'center' });
    });

    // ===== Slide 5: Technologies =====
    slide = pptx.addSlide();
    slide.background = { fill: PRIMARY };
    slide.addShape(pptx.ShapeType.rect, { x: 0, y: 0, w: '100%', h: 0.06, fill: { color: SECONDARY } });
    slide.addText('04  Technologies Utilisées', {
      x: 0.6, y: 0.3, w: 9, h: 0.6, fontSize: 26, fontFace: 'Poppins',
      color: WHITE, bold: true
    });
    slide.addShape(pptx.ShapeType.rect, { x: 0.6, y: 0.95, w: 1.5, h: 0.04, fill: { color: SECONDARY } });

    const techs = [
      { icon: '🐍', name: 'Python 3', desc: 'Langage principal du backend, puissant et polyvalent', color: '306998' },
      { icon: '🎸', name: 'Django 6.0', desc: 'Framework web MVC avec ORM, auth et admin intégrés', color: '092E20' },
      { icon: '🗄️', name: 'SQLite', desc: 'Base de données légère, idéale pour le développement', color: '003B57' },
      { icon: '🎨', name: 'Bootstrap 5', desc: 'Framework CSS pour une interface responsive', color: '7952B3' },
      { icon: '📄', name: 'ReportLab', desc: 'Génération de factures et rapports PDF', color: 'CC0000' },
      { icon: '🎭', name: 'Playwright', desc: 'Tests end-to-end automatisés du navigateur', color: '2EAD33' },
      { icon: '📊', name: 'Chart.js', desc: 'Graphiques pour le tableau de bord et statistiques', color: 'FF6384' },
      { icon: '🔒', name: 'Django Auth', desc: 'Authentification, autorisation et sécurité intégrées', color: 'EF4444' }
    ];

    techs.forEach((t, i) => {
      const col = i % 4;
      const row = Math.floor(i / 4);
      const x = 0.6 + col * 2.35;
      const y = 1.3 + row * 2.6;

      slide.addShape(pptx.ShapeType.roundRect, {
        x: x, y: y, w: 2.15, h: 2.3, rectRadius: 0.1,
        fill: { color: '1E293B' }, line: { color: '334155', width: 1 }
      });
      slide.addShape(pptx.ShapeType.roundRect, {
        x: x + 0.7, y: y + 0.2, w: 0.75, h: 0.75, rectRadius: 0.08,
        fill: { color: t.color }
      });
      slide.addText(t.icon, { x: x + 0.7, y: y + 0.25, w: 0.75, h: 0.65, fontSize: 26, align: 'center' });
      slide.addText(t.name, { x: x + 0.1, y: y + 1.05, w: 1.95, h: 0.35, fontSize: 13, fontFace: 'Poppins', color: WHITE, bold: true, align: 'center' });
      slide.addText(t.desc, { x: x + 0.1, y: y + 1.4, w: 1.95, h: 0.7, fontSize: 9.5, fontFace: 'Poppins', color: GRAY, align: 'center' });
    });

    // ===== Slide 6: Architecture MVT =====
    slide = pptx.addSlide();
    slide.background = { fill: PRIMARY };
    slide.addShape(pptx.ShapeType.rect, { x: 0, y: 0, w: '100%', h: 0.06, fill: { color: SECONDARY } });
    slide.addText('05  Architecture Django MVT', {
      x: 0.6, y: 0.3, w: 9, h: 0.6, fontSize: 26, fontFace: 'Poppins',
      color: WHITE, bold: true
    });
    slide.addShape(pptx.ShapeType.rect, { x: 0.6, y: 0.95, w: 1.5, h: 0.04, fill: { color: SECONDARY } });

    // Architecture boxes
    const archBoxes = [
      { x: 0.6, y: 1.3, w: 2.8, h: 2.2, title: '🌐 URLs', items: 'core/urls.py\n42 routes nommées\nREST-like patterns', color: SECONDARY },
      { x: 3.6, y: 1.3, w: 2.8, h: 2.2, title: '⚙️ Views', items: 'core/views.py\n55+ fonctions\n@login_required\n@admin_required', color: '7C3AED' },
      { x: 6.6, y: 1.3, w: 2.8, h: 2.2, title: '📋 Templates', items: '39 fichiers HTML\nBootstrap 5\nTemplate tags custom', color: '059669' },
    ];

    archBoxes.forEach(box => {
      slide.addShape(pptx.ShapeType.roundRect, {
        x: box.x, y: box.y, w: box.w, h: box.h, rectRadius: 0.1,
        fill: { color: '1E293B' }, line: { color: box.color, width: 2 }
      });
      slide.addText(box.title, { x: box.x, y: box.y + 0.15, w: box.w, h: 0.4, fontSize: 15, fontFace: 'Poppins', color: WHITE, bold: true, align: 'center' });
      slide.addText(box.items, { x: box.x + 0.15, y: box.y + 0.6, w: box.w - 0.3, h: 1.4, fontSize: 10.5, fontFace: 'Poppins', color: GRAY, align: 'center', lineSpacingMultiple: 1.4 });
    });

    // Arrows
    slide.addText('→', { x: 3.35, y: 1.9, w: 0.3, h: 0.5, fontSize: 28, color: ACCENT, align: 'center' });
    slide.addText('→', { x: 6.35, y: 1.9, w: 0.3, h: 0.5, fontSize: 28, color: ACCENT, align: 'center' });

    // Models and DB
    slide.addShape(pptx.ShapeType.roundRect, {
      x: 0.6, y: 3.9, w: 4.3, h: 2.8, rectRadius: 0.1,
      fill: { color: '1E293B' }, line: { color: 'F59E0B', width: 2 }
    });
    slide.addText('🗃️ Models (ORM Django)', { x: 0.6, y: 4.0, w: 4.3, h: 0.4, fontSize: 14, fontFace: 'Poppins', color: WHITE, bold: true, align: 'center' });

    const modelsList = ['User (auth)', 'Client', 'Voiture', 'Categorie', 'Reservation', 'Paiement', 'Historique', 'Notification'];
    modelsList.forEach((m, i) => {
      const col = i % 2;
      const row = Math.floor(i / 2);
      slide.addText(`• ${m}`, { x: 0.9 + col * 2, y: 4.5 + row * 0.45, w: 2, h: 0.4, fontSize: 10.5, fontFace: 'Poppins', color: GRAY });
    });

    // Database
    slide.addShape(pptx.ShapeType.roundRect, {
      x: 5.1, y: 3.9, w: 4.3, h: 2.8, rectRadius: 0.1,
      fill: { color: '1E293B' }, line: { color: SUCCESS, width: 2 }
    });
    slide.addText('🗄️ Base de Données', { x: 5.1, y: 4.0, w: 4.3, h: 0.4, fontSize: 14, fontFace: 'Poppins', color: WHITE, bold: true, align: 'center' });
    slide.addText('SQLite3\n\n• 10 migrations\n• Relations FK/1:1\n• Contraintes d\'intégrité\n• Index uniques\n• Validation côté modèle', {
      x: 5.3, y: 4.5, w: 3.9, h: 2.0, fontSize: 10.5, fontFace: 'Poppins', color: GRAY, lineSpacingMultiple: 1.4
    });

    // Arrow down
    slide.addText('↓', { x: 4.5, y: 3.5, w: 1, h: 0.4, fontSize: 28, color: ACCENT, align: 'center' });

    // ===== Slide 7: Actors =====
    slide = pptx.addSlide();
    slide.background = { fill: PRIMARY };
    slide.addShape(pptx.ShapeType.rect, { x: 0, y: 0, w: '100%', h: 0.06, fill: { color: SECONDARY } });
    slide.addText('06  Acteurs du Système', {
      x: 0.6, y: 0.3, w: 9, h: 0.6, fontSize: 26, fontFace: 'Poppins',
      color: WHITE, bold: true
    });
    slide.addShape(pptx.ShapeType.rect, { x: 0.6, y: 0.95, w: 1.5, h: 0.04, fill: { color: SECONDARY } });

    const actors = [
      {
        icon: '👨‍💼', title: 'Administrateur', color: DANGER,
        perms: ['Gestion complète CRUD', 'Gestion des rôles', 'Configuration du système', 'Suppression superuser bloquée', 'Accès aux statistiques']
      },
      {
        icon: '👨‍💻', title: 'Employé', color: WARNING,
        perms: ['Dashboard et KPIs', 'Créer/accepter/resuser réservations', 'Ajouter des clients', 'Consulter l\'historique', 'Gérer les retours']
      },
      {
        icon: '👤', title: 'Client', color: SUCCESS,
        perms: ['Inscription autonome', 'Catalogue voitures', 'Créer des réservations', 'Annuler ses demandes', 'Suivre ses réservations']
      }
    ];

    actors.forEach((a, i) => {
      const x = 0.6 + i * 3.2;
      slide.addShape(pptx.ShapeType.roundRect, {
        x: x, y: 1.3, w: 3.0, h: 5.0, rectRadius: 0.1,
        fill: { color: '1E293B' }, line: { color: a.color, width: 2 }
      });
      slide.addShape(pptx.ShapeType.rect, { x: x, y: 1.3, w: 3.0, h: 0.06, fill: { color: a.color } });
      slide.addText(a.icon, { x: x, y: 1.5, w: 3.0, h: 0.8, fontSize: 40, align: 'center' });
      slide.addText(a.title, { x: x, y: 2.3, w: 3.0, h: 0.4, fontSize: 16, fontFace: 'Poppins', color: WHITE, bold: true, align: 'center' });

      a.perms.forEach((p, j) => {
        slide.addText(`✓  ${p}`, { x: x + 0.2, y: 2.9 + j * 0.5, w: 2.6, h: 0.45, fontSize: 11, fontFace: 'Poppins', color: GRAY });
      });
    });

    // ===== Slide 8: Database =====
    slide = pptx.addSlide();
    slide.background = { fill: PRIMARY };
    slide.addShape(pptx.ShapeType.rect, { x: 0, y: 0, w: '100%', h: 0.06, fill: { color: SECONDARY } });
    slide.addText('07  Base de Données — Modèles', {
      x: 0.6, y: 0.3, w: 9, h: 0.6, fontSize: 26, fontFace: 'Poppins',
      color: WHITE, bold: true
    });
    slide.addShape(pptx.ShapeType.rect, { x: 0.6, y: 0.95, w: 1.5, h: 0.04, fill: { color: SECONDARY } });

    const dbTables = [
      { name: 'User', color: '6366F1', fields: ['id (PK)', 'username', 'email', 'is_staff', 'is_superuser'] },
      { name: 'Client', color: '8B5CF6', fields: ['id (PK)', 'user (1:1)', 'nom', 'prenom', 'cin (unique)', 'telephone'] },
      { name: 'Voiture', color: SECONDARY, fields: ['id (PK)', 'marque', 'modele', 'immat (unique)', 'prix_jour', 'statut'] },
      { name: 'Categorie', color: '0891B2', fields: ['id (PK)', 'nom (unique)', 'description'] },
      { name: 'Reservation', color: SUCCESS, fields: ['id (PK)', 'client (FK)', 'voiture (FK)', 'dates', 'montant', 'statut'] },
      { name: 'Paiement', color: WARNING, fields: ['id (PK)', 'reservation (FK)', 'montant', 'mode', 'statut'] },
      { name: 'Historique', color: 'EC4899', fields: ['id (PK)', 'action', 'utilisateur (FK)', 'reservation (FK)'] },
      { name: 'Notification', color: DANGER, fields: ['id (PK)', 'utilisateur (FK)', 'titre', 'message', 'lu'] }
    ];

    dbTables.forEach((t, i) => {
      const col = i % 4;
      const row = Math.floor(i / 4);
      const x = 0.6 + col * 2.35;
      const y = 1.2 + row * 2.8;

      slide.addShape(pptx.ShapeType.roundRect, {
        x: x, y: y, w: 2.15, h: 2.5, rectRadius: 0.08,
        fill: { color: '1E293B' }, line: { color: t.color, width: 1.5 }
      });
      slide.addShape(pptx.ShapeType.rect, { x: x, y: y, w: 2.15, h: 0.35, fill: { color: t.color } });
      slide.addText(t.name, { x: x, y: y + 0.02, w: 2.15, h: 0.32, fontSize: 11, fontFace: 'Poppins', color: WHITE, bold: true, align: 'center' });

      t.fields.forEach((f, j) => {
        const isPK = f.includes('PK');
        const isFK = f.includes('FK') || f.includes('1:1');
        let color = GRAY;
        if (isPK) color = WARNING;
        else if (isFK) color = SUCCESS;

        slide.addText(f, { x: x + 0.1, y: y + 0.4 + j * 0.32, w: 1.95, h: 0.3, fontSize: 9, fontFace: 'Consolas', color: color });
      });
    });

    // Relationships note
    slide.addText('Relations : User ←1:1→ Client ←1:N→ Reservation ←N:1→ Voiture ←N:1→ Categorie  |  Reservation ←1:N→ Paiement  |  User ←1:N→ Notification', {
      x: 0.6, y: 6.5, w: 9, h: 0.35, fontSize: 9.5, fontFace: 'Poppins', color: GRAY, align: 'center'
    });

    // ===== Slide 9: Fonctionnalités =====
    slide = pptx.addSlide();
    slide.background = { fill: PRIMARY };
    slide.addShape(pptx.ShapeType.rect, { x: 0, y: 0, w: '100%', h: 0.06, fill: { color: SECONDARY } });
    slide.addText('08  Fonctionnalités Principales', {
      x: 0.6, y: 0.3, w: 9, h: 0.6, fontSize: 26, fontFace: 'Poppins',
      color: WHITE, bold: true
    });
    slide.addShape(pptx.ShapeType.rect, { x: 0.6, y: 0.95, w: 1.5, h: 0.04, fill: { color: SECONDARY } });

    const features = [
      { icon: '🚗', title: 'Gestion Véhicules', desc: 'CRUD complet, images, catégories, filtres, recherche, statuts' },
      { icon: '👥', title: 'Gestion Clients', desc: 'Inscription, profils, historique, recherche, pagination' },
      { icon: '📅', title: 'Réservations', desc: 'Workflow complet : en_attente → en_cours → terminée, validation AJAX' },
      { icon: '💳', title: 'Paiements', desc: 'Especes, virement, carte. Suivi des statuts et historique' },
      { icon: '📊', title: 'Tableau de Bord', desc: '11 KPIs, top véhicules, top clients, retours récents' },
      { icon: '📈', title: 'Statistiques', desc: 'CA mensuel, taux d\'occupation, répartition par statut' },
      { icon: '🔔', title: 'Notifications', desc: 'Alertes temps réel, badge non-lus, marquer tout lu' },
      { icon: '📝', title: 'Historique Audit', desc: 'Traçabilité complète de toutes les actions avec filtres' },
      { icon: '📄', title: 'Exports', desc: 'PDF (factures, rapports) et CSV (voitures, clients, réservations)' },
      { icon: '🔐', title: 'Sécurité RBAC', desc: '3 rôles, permissions, CSRF, validation, protection superuser' },
      { icon: '🔍', title: 'Recherche & Filtres', desc: 'Recherche multi-champs, filtres par statut/catégorie, pagination' },
      { icon: '⚡', title: 'AJAX Temps Réel', desc: 'Vérification disponibilité, actions sans rechargement, toasts' }
    ];

    features.forEach((f, i) => {
      const col = i % 3;
      const row = Math.floor(i / 3);
      const x = 0.6 + col * 3.15;
      const y = 1.2 + row * 1.35;

      slide.addShape(pptx.ShapeType.roundRect, {
        x: x, y: y, w: 2.95, h: 1.15, rectRadius: 0.08,
        fill: { color: '1E293B' }, line: { color: '334155', width: 1 }
      });
      slide.addText(f.icon, { x: x + 0.1, y: y + 0.15, w: 0.6, h: 0.6, fontSize: 22, align: 'center' });
      slide.addText(f.title, { x: x + 0.7, y: y + 0.1, w: 2.1, h: 0.35, fontSize: 12, fontFace: 'Poppins', color: WHITE, bold: true });
      slide.addText(f.desc, { x: x + 0.7, y: y + 0.45, w: 2.1, h: 0.6, fontSize: 9, fontFace: 'Poppins', color: GRAY });
    });

    // ===== Slide 10: Réservations =====
    slide = pptx.addSlide();
    slide.background = { fill: PRIMARY };
    slide.addShape(pptx.ShapeType.rect, { x: 0, y: 0, w: '100%', h: 0.06, fill: { color: SECONDARY } });
    slide.addText('09  Gestion des Réservations', {
      x: 0.6, y: 0.3, w: 9, h: 0.6, fontSize: 26, fontFace: 'Poppins',
      color: WHITE, bold: true
    });
    slide.addShape(pptx.ShapeType.rect, { x: 0.6, y: 0.95, w: 1.5, h: 0.04, fill: { color: SECONDARY } });

    // Workflow
    const workflow = [
      { num: '1', title: 'Création', desc: 'Client ou employé crée une demande → statut "en_attente"', color: WARNING },
      { num: '2', title: 'Vérification', desc: 'Contrôle disponibilité véhicule, conflits de dates, statut maintenance', color: ACCENT },
      { num: '3', title: 'Validation', desc: 'Admin/employé accepte → "en_cours", voiture passe à "louee"', color: SUCCESS },
      { num: '4', title: 'Refus', desc: 'Si refusé → "annulee", historique + notification créés', color: DANGER },
      { num: '5', title: 'Retour', desc: 'Terminer → "terminee", voiture redevient "disponible"', color: '8B5CF6' }
    ];

    workflow.forEach((w, i) => {
      const y = 1.2 + i * 0.95;
      slide.addShape(pptx.ShapeType.roundRect, {
        x: 0.6, y: y, w: 5.5, h: 0.8, rectRadius: 0.08,
        fill: { color: '1E293B' }, line: { color: w.color, width: 1.5 }
      });
      slide.addShape(pptx.ShapeType.ellipse, {
        x: 0.8, y: y + 0.12, w: 0.55, h: 0.55, fill: { color: w.color }
      });
      slide.addText(w.num, { x: 0.8, y: y + 0.12, w: 0.55, h: 0.55, fontSize: 14, fontFace: 'Poppins', color: WHITE, bold: true, align: 'center', valign: 'middle' });
      slide.addText(w.title, { x: 1.5, y: y + 0.08, w: 4.3, h: 0.35, fontSize: 13, fontFace: 'Poppins', color: WHITE, bold: true });
      slide.addText(w.desc, { x: 1.5, y: y + 0.4, w: 4.3, h: 0.35, fontSize: 10, fontFace: 'Poppins', color: GRAY });

      if (i < workflow.length - 1) {
        slide.addText('↓', { x: 3.1, y: y + 0.75, w: 0.5, h: 0.25, fontSize: 14, color: ACCENT, align: 'center' });
      }
    });

    // Right side: Features
    slide.addShape(pptx.ShapeType.roundRect, {
      x: 6.3, y: 1.2, w: 3.3, h: 5.2, rectRadius: 0.1,
      fill: { color: '1E293B' }, line: { color: '334155', width: 1 }
    });
    slide.addText('Fonctionnalités Avancées', { x: 6.3, y: 1.3, w: 3.3, h: 0.4, fontSize: 14, fontFace: 'Poppins', color: ACCENT, bold: true, align: 'center' });

    const resFeatures = [
      'Vérification AJAX disponibilité',
      'Calcul automatique du montant',
      'Détection conflits de dates',
      'Blocage véhicules en maintenance',
      'Actions AJAX (accepter/refuser)',
      'Annulation par le client',
      'Historique complet des actions',
      'Notifications automatiques',
      'Export facture PDF',
      'Filtres et pagination'
    ];

    resFeatures.forEach((f, i) => {
      slide.addText(`• ${f}`, { x: 6.5, y: 1.8 + i * 0.43, w: 2.9, h: 0.4, fontSize: 10, fontFace: 'Poppins', color: GRAY });
    });

    // ===== Slide 11: Espace Client =====
    slide = pptx.addSlide();
    slide.background = { fill: PRIMARY };
    slide.addShape(pptx.ShapeType.rect, { x: 0, y: 0, w: '100%', h: 0.06, fill: { color: SECONDARY } });
    slide.addText('10  Espace Client', {
      x: 0.6, y: 0.3, w: 9, h: 0.6, fontSize: 26, fontFace: 'Poppins',
      color: WHITE, bold: true
    });
    slide.addShape(pptx.ShapeType.rect, { x: 0.6, y: 0.95, w: 1.5, h: 0.04, fill: { color: SECONDARY } });

    const clientFeatures = [
      { icon: '📝', title: 'Inscription Autonome', desc: 'Création de compte avec validation CIN unique, mot de passe sécurisé', x: 0.6, y: 1.3 },
      { icon: '🏠', title: 'Dashboard Personnel', desc: '4 compteurs (en attente, en cours, terminées, total dépensé)', x: 5, y: 1.3 },
      { icon: '🚗', title: 'Catalogue Voitures', desc: 'Grille de cartes avec images, marque, modèle, prix/jour, disponibilité', x: 0.6, y: 3.1 },
      { icon: '📅', title: 'Réservation en Ligne', desc: 'Formulaire avec vérification AJAX temps réel de la disponibilité', x: 5, y: 3.1 },
      { icon: '📊', title: 'Suivi des Réservations', desc: 'Historique paginé avec annulation possible pour les demandes en attente', x: 0.6, y: 4.9 },
      { icon: '🔔', title: 'Notifications', desc: 'Alertes pour changements de statut et paiements', x: 5, y: 4.9 }
    ];

    clientFeatures.forEach(f => {
      slide.addShape(pptx.ShapeType.roundRect, {
        x: f.x, y: f.y, w: 4.2, h: 1.5, rectRadius: 0.1,
        fill: { color: '1E293B' }, line: { color: '334155', width: 1 }
      });
      slide.addText(f.icon, { x: f.x + 0.15, y: f.y + 0.2, w: 0.7, h: 0.7, fontSize: 28, align: 'center' });
      slide.addText(f.title, { x: f.x + 0.9, y: f.y + 0.15, w: 3.1, h: 0.4, fontSize: 14, fontFace: 'Poppins', color: WHITE, bold: true });
      slide.addText(f.desc, { x: f.x + 0.9, y: f.y + 0.6, w: 3.1, h: 0.7, fontSize: 10.5, fontFace: 'Poppins', color: GRAY });
    });

    // ===== Slide 12: Sécurité =====
    slide = pptx.addSlide();
    slide.background = { fill: PRIMARY };
    slide.addShape(pptx.ShapeType.rect, { x: 0, y: 0, w: '100%', h: 0.06, fill: { color: SECONDARY } });
    slide.addText('11  Gestion des Rôles & Sécurité', {
      x: 0.6, y: 0.3, w: 9, h: 0.6, fontSize: 26, fontFace: 'Poppins',
      color: WHITE, bold: true
    });
    slide.addShape(pptx.ShapeType.rect, { x: 0.6, y: 0.95, w: 1.5, h: 0.04, fill: { color: SECONDARY } });

    // Security layers
    const secLayers = [
      { icon: '🔐', title: 'Authentification', items: 'Django Auth\nLogin/Logout\nPassword Reset\nSession Management', color: SECONDARY },
      { icon: '🛡️', title: 'Autorisation RBAC', items: 'Groupes: Admin, Employe\nClient (profil lié)\nDécorateur @admin_required\nVérifications inline', color: '7C3AED' },
      { icon: '🔒', title: 'Sécurité Web', items: 'Token CSRF\nValidation formulaires\nPassword Validators\nHeaders sécurité', color: SUCCESS },
      { icon: '📝', title: 'Audit & Traçabilité', items: 'Modèle Historique\n9 types d\'actions\nNotifications auto\nJournal d\'activité', color: WARNING }
    ];

    secLayers.forEach((s, i) => {
      const x = 0.6 + i * 2.35;
      slide.addShape(pptx.ShapeType.roundRect, {
        x: x, y: 1.2, w: 2.15, h: 3.5, rectRadius: 0.1,
        fill: { color: '1E293B' }, line: { color: s.color, width: 2 }
      });
      slide.addText(s.icon, { x: x, y: 1.35, w: 2.15, h: 0.6, fontSize: 30, align: 'center' });
      slide.addText(s.title, { x: x, y: 1.95, w: 2.15, h: 0.35, fontSize: 13, fontFace: 'Poppins', color: WHITE, bold: true, align: 'center' });
      slide.addText(s.items, { x: x + 0.15, y: 2.4, w: 1.85, h: 2.0, fontSize: 10, fontFace: 'Poppins', color: GRAY, align: 'center', lineSpacingMultiple: 1.5 });
    });

    // Protection superuser box
    slide.addShape(pptx.ShapeType.roundRect, {
      x: 0.6, y: 5.0, w: 9, h: 1.5, rectRadius: 0.1,
      fill: { color: '1E293B' }, line: { color: DANGER, width: 1.5 }
    });
    slide.addText('⚠️  Protection Superuser', { x: 0.8, y: 5.1, w: 4, h: 0.35, fontSize: 13, fontFace: 'Poppins', color: DANGER, bold: true });
    slide.addText('Le système empêche la suppression du compte superuser via la gestion des rôles.\nBlocage vérifié à la fois côté vue (gestion_roles) et dans les tests unitaires (5 tests dédiés).', {
      x: 0.8, y: 5.5, w: 8.5, h: 0.8, fontSize: 10.5, fontFace: 'Poppins', color: GRAY, lineSpacingMultiple: 1.4
    });

    // ===== Slide 13: Exports =====
    slide = pptx.addSlide();
    slide.background = { fill: PRIMARY };
    slide.addShape(pptx.ShapeType.rect, { x: 0, y: 0, w: '100%', h: 0.06, fill: { color: SECONDARY } });
    slide.addText('12  Exports PDF & CSV', {
      x: 0.6, y: 0.3, w: 9, h: 0.6, fontSize: 26, fontFace: 'Poppins',
      color: WHITE, bold: true
    });
    slide.addShape(pptx.ShapeType.rect, { x: 0.6, y: 0.95, w: 1.5, h: 0.04, fill: { color: SECONDARY } });

    // CSV Exports
    slide.addShape(pptx.ShapeType.roundRect, {
      x: 0.6, y: 1.2, w: 4.2, h: 3.5, rectRadius: 0.1,
      fill: { color: '1E293B' }, line: { color: SUCCESS, width: 2 }
    });
    slide.addText('📊  Exports CSV', { x: 0.6, y: 1.3, w: 4.2, h: 0.45, fontSize: 18, fontFace: 'Poppins', color: SUCCESS, bold: true, align: 'center' });

    const csvExports = [
      { name: 'Voitures', cols: 'Marque, Modèle, Immatriculation, Année, Prix/jour, Statut' },
      { name: 'Clients', cols: 'Nom, Prénom, CIN, Téléphone, Email, Adresse' },
      { name: 'Réservations', cols: 'Client, Voiture, Dates, Montant, Statut' }
    ];

    csvExports.forEach((e, i) => {
      slide.addText(e.name, { x: 0.9, y: 1.9 + i * 0.9, w: 3.6, h: 0.3, fontSize: 12, fontFace: 'Poppins', color: WHITE, bold: true });
      slide.addText(e.cols, { x: 0.9, y: 2.2 + i * 0.9, w: 3.6, h: 0.3, fontSize: 9.5, fontFace: 'Poppins', color: GRAY });
    });

    // PDF Exports
    slide.addShape(pptx.ShapeType.roundRect, {
      x: 5.0, y: 1.2, w: 4.6, h: 3.5, rectRadius: 0.1,
      fill: { color: '1E293B' }, line: { color: DANGER, width: 2 }
    });
    slide.addText('📄  Exports PDF (ReportLab)', { x: 5.0, y: 1.3, w: 4.6, h: 0.45, fontSize: 18, fontFace: 'Poppins', color: DANGER, bold: true, align: 'center' });

    slide.addText('Facture PDF', { x: 5.3, y: 1.9, w: 4, h: 0.3, fontSize: 13, fontFace: 'Poppins', color: WHITE, bold: true });
    slide.addText('• Numéro de facture\n• Informations client (nom, CIN, téléphone)\n• Détails véhicule et dates\n• Montant total en DH', {
      x: 5.3, y: 2.2, w: 4, h: 1.2, fontSize: 10, fontFace: 'Poppins', color: GRAY, lineSpacingMultiple: 1.4
    });

    slide.addText('Rapport PDF Global', { x: 5.3, y: 3.4, w: 4, h: 0.3, fontSize: 13, fontFace: 'Poppins', color: WHITE, bold: true });
    slide.addText('• Résumé (véhicules, clients, CA)\n• Top 5 véhicules les plus loués\n• Top 5 clients par CA généré\n• CA mensuel sur 6 mois', {
      x: 5.3, y: 3.7, w: 4, h: 1.0, fontSize: 10, fontFace: 'Poppins', color: GRAY, lineSpacingMultiple: 1.4
    });

    // Bottom note
    slide.addShape(pptx.ShapeType.roundRect, {
      x: 0.6, y: 5.0, w: 9, h: 1.3, rectRadius: 0.1,
      fill: { color: '1E293B' }, line: { color: '334155', width: 1 }
    });
    slide.addText('Technologie : ReportLab (reportlab.pdfgen.canvas)', { x: 0.8, y: 5.1, w: 8.5, h: 0.35, fontSize: 12, fontFace: 'Poppins', color: ACCENT, bold: true });
    slide.addText('Génération côté serveur avec reportlab.pdfgen.canvas et reportlab.lib.pagesizes.AA. Format A4, polices standard, en-têtes et pieds de page.', {
      x: 0.8, y: 5.5, w: 8.5, h: 0.6, fontSize: 10, fontFace: 'Poppins', color: GRAY
    });

    // ===== Slide 14: Statistiques =====
    slide = pptx.addSlide();
    slide.background = { fill: PRIMARY };
    slide.addShape(pptx.ShapeType.rect, { x: 0, y: 0, w: '100%', h: 0.06, fill: { color: SECONDARY } });
    slide.addText('13  Statistiques & Tableau de Bord', {
      x: 0.6, y: 0.3, w: 9, h: 0.6, fontSize: 26, fontFace: 'Poppins',
      color: WHITE, bold: true
    });
    slide.addShape(pptx.ShapeType.rect, { x: 0.6, y: 0.95, w: 1.5, h: 0.04, fill: { color: SECONDARY } });

    // KPI Dashboard
    slide.addText('Dashboard Admin — 11 Indicateurs', { x: 0.6, y: 1.2, w: 9, h: 0.35, fontSize: 15, fontFace: 'Poppins', color: ACCENT, bold: true });

    const kpis = [
      { icon: '🚗', label: 'Total Véhicules', color: SECONDARY },
      { icon: '✅', label: 'Disponibles', color: SUCCESS },
      { icon: '🔄', label: 'En Location', color: WARNING },
      { icon: '🔧', label: 'Maintenance', color: DANGER },
      { icon: '👥', label: 'Total Clients', color: '8B5CF6' },
    ];

    kpis.forEach((k, i) => {
      const x = 0.6 + i * 1.85;
      slide.addShape(pptx.ShapeType.roundRect, {
        x: x, y: 1.65, w: 1.65, h: 1.2, rectRadius: 0.08,
        fill: { color: '1E293B' }, line: { color: k.color, width: 1.5 }
      });
      slide.addText(k.icon, { x: x, y: 1.7, w: 1.65, h: 0.5, fontSize: 22, align: 'center' });
      slide.addText(k.label, { x: x, y: 2.2, w: 1.65, h: 0.4, fontSize: 9.5, fontFace: 'Poppins', color: GRAY, align: 'center' });
    });

    // Dashboard sections
    slide.addShape(pptx.ShapeType.roundRect, {
      x: 0.6, y: 3.1, w: 4.3, h: 3.2, rectRadius: 0.1,
      fill: { color: '1E293B' }, line: { color: '334155', width: 1 }
    });
    slide.addText('📊 Sections du Dashboard', { x: 0.8, y: 3.2, w: 3.9, h: 0.35, fontSize: 13, fontFace: 'Poppins', color: ACCENT, bold: true });

    const dashSections = [
      'Demandes en attente (top 10) + boutons AJAX',
      'Véhicule le plus loué (avec compteur)',
      'Top 5 clients par CA généré',
      '5 derniers retours enregistrés',
      'Statistiques paiements',
      'Boutons d\'actions rapides'
    ];

    dashSections.forEach((s, i) => {
      slide.addText(`• ${s}`, { x: 0.9, y: 3.6 + i * 0.42, w: 3.8, h: 0.4, fontSize: 10.5, fontFace: 'Poppins', color: GRAY });
    });

    // Statistics page
    slide.addShape(pptx.ShapeType.roundRect, {
      x: 5.1, y: 3.1, w: 4.5, h: 3.2, rectRadius: 0.1,
      fill: { color: '1E293B' }, line: { color: '334155', width: 1 }
    });
    slide.addText('📈 Page Statistiques', { x: 5.3, y: 3.2, w: 4.1, h: 0.35, fontSize: 13, fontFace: 'Poppins', color: ACCENT, bold: true });

    const statsItems = [
      'CA Total (réservations terminées)',
      'Taux d\'occupation = louées / (total - maintenance)',
      'Total des réservations',
      'Répartition par statut (tableau)',
      'CA mensuel sur 6 derniers mois',
      'Lien vers rapport PDF global'
    ];

    statsItems.forEach((s, i) => {
      slide.addText(`• ${s}`, { x: 5.4, y: 3.6 + i * 0.42, w: 4, h: 0.4, fontSize: 10.5, fontFace: 'Poppins', color: GRAY });
    });

    // ===== Slide 15: Tests =====
    slide = pptx.addSlide();
    slide.background = { fill: PRIMARY };
    slide.addShape(pptx.ShapeType.rect, { x: 0, y: 0, w: '100%', h: 0.06, fill: { color: SECONDARY } });
    slide.addText('14  Tests & Validation', {
      x: 0.6, y: 0.3, w: 9, h: 0.6, fontSize: 26, fontFace: 'Poppins',
      color: WHITE, bold: true
    });
    slide.addShape(pptx.ShapeType.rect, { x: 0.6, y: 0.95, w: 1.5, h: 0.04, fill: { color: SECONDARY } });

    // Django Tests
    slide.addShape(pptx.ShapeType.roundRect, {
      x: 0.6, y: 1.3, w: 4.3, h: 5.0, rectRadius: 0.1,
      fill: { color: '1E293B' }, line: { color: SUCCESS, width: 2 }
    });
    slide.addText('🧪 Tests Django Unitaires', { x: 0.6, y: 1.4, w: 4.3, h: 0.45, fontSize: 16, fontFace: 'Poppins', color: SUCCESS, bold: true, align: 'center' });
    slide.addText('110+ tests', { x: 0.6, y: 1.9, w: 4.3, h: 0.5, fontSize: 28, fontFace: 'Poppins', color: SUCCESS, bold: true, align: 'center' });
    slide.addText('core/tests.py + core/test_forms.py', { x: 0.6, y: 2.35, w: 4.3, h: 0.3, fontSize: 9, fontFace: 'Consolas', color: GRAY, align: 'center' });

    const djangoTests = [
      'Modèles : 24 tests (str, contraintes, calculs)',
      'Vues auth : 6 tests (login, redirect, accès)',
      'CRUD Voitures : 15 tests (opérations + edge cases)',
      'Réservations : 20 tests (workflow complet)',
      'Clients : 12 tests (inscription, RBAC)',
      'Paiements : 10 tests (CRUD, historique)',
      'Notifications : 8 tests (CRUD, template tag)',
      'Exports CSV/PDF : 6 tests',
      'RBAC : 11 tests (rôles, protection)',
      'AJAX : 11 tests (API disponibilité)',
      'Dashboard : 4 tests (contexte, KPIs)',
      'Forms : 31 tests (validation)'
    ];

    djangoTests.forEach((t, i) => {
      slide.addText(`• ${t}`, { x: 0.8, y: 2.7 + i * 0.32, w: 3.9, h: 0.3, fontSize: 9, fontFace: 'Poppins', color: GRAY });
    });

    // Playwright Tests
    slide.addShape(pptx.ShapeType.roundRect, {
      x: 5.1, y: 1.3, w: 4.5, h: 5.0, rectRadius: 0.1,
      fill: { color: '1E293B' }, line: { color: ACCENT, width: 2 }
    });
    slide.addText('🎭 Tests Playwright E2E', { x: 5.1, y: 1.4, w: 4.5, h: 0.45, fontSize: 16, fontFace: 'Poppins', color: ACCENT, bold: true, align: 'center' });
    slide.addText('35 tests', { x: 5.1, y: 1.9, w: 4.5, h: 0.5, fontSize: 28, fontFace: 'Poppins', color: ACCENT, bold: true, align: 'center' });
    slide.addText('tests_e2e/app.spec.js', { x: 5.1, y: 2.35, w: 4.5, h: 0.3, fontSize: 9, fontFace: 'Consolas', color: GRAY, align: 'center' });

    const playwrightTests = [
      'Authentification (6 tests)',
      'Navigation admin (1 test)',
      'Voitures : liste, filtres, CRUD (9 tests)',
      'Clients : liste, recherche (3 tests)',
      'Réservations : CRUD, filtres (5 tests)',
      'Actions AJAX (1 test)',
      'Exports CSV/PDF (3 tests)',
      'Espace client (5 tests)',
      'RBAC (2 tests)',
      'Dashboard (2 tests)',
      'Page 404 (1 test)'
    ];

    playwrightTests.forEach((t, i) => {
      slide.addText(`• ${t}`, { x: 5.3, y: 2.7 + i * 0.32, w: 4.1, h: 0.3, fontSize: 9.5, fontFace: 'Poppins', color: GRAY });
    });

    // ===== Slide 16: Limites =====
    slide = pptx.addSlide();
    slide.background = { fill: PRIMARY };
    slide.addShape(pptx.ShapeType.rect, { x: 0, y: 0, w: '100%', h: 0.06, fill: { color: SECONDARY } });
    slide.addText('15  Limites & Perspectives', {
      x: 0.6, y: 0.3, w: 9, h: 0.6, fontSize: 26, fontFace: 'Poppins',
      color: WHITE, bold: true
    });
    slide.addShape(pptx.ShapeType.rect, { x: 0.6, y: 0.95, w: 1.5, h: 0.04, fill: { color: SECONDARY } });

    // Limites
    slide.addShape(pptx.ShapeType.roundRect, {
      x: 0.6, y: 1.2, w: 4.3, h: 5.0, rectRadius: 0.1,
      fill: { color: '1E293B' }, line: { color: DANGER, width: 2 }
    });
    slide.addText('⚠️  Limites Actuelles', { x: 0.6, y: 1.3, w: 4.3, h: 0.45, fontSize: 16, fontFace: 'Poppins', color: DANGER, bold: true, align: 'center' });

    const limites = [
      'Base SQLite (pas de production)',
      'Pas de système de paiement en ligne',
      'Pas d\'application mobile',
      'Pas de géolocalisation véhicules',
      'Notifications uniquement in-app',
      'Pas d\'intégration calendar/Google',
      'Pas de multi-langue (fr uniquement)',
      'Pas de cache/optimisation Redis',
      'Pas de déploiement Docker/CI-CD'
    ];

    limites.forEach((l, i) => {
      slide.addText(`✗  ${l}`, { x: 0.9, y: 1.9 + i * 0.43, w: 3.8, h: 0.4, fontSize: 11, fontFace: 'Poppins', color: GRAY });
    });

    // Perspectives
    slide.addShape(pptx.ShapeType.roundRect, {
      x: 5.1, y: 1.2, w: 4.5, h: 5.0, rectRadius: 0.1,
      fill: { color: '1E293B' }, line: { color: SUCCESS, width: 2 }
    });
    slide.addText('🚀  Perspectives d\'Amélioration', { x: 5.1, y: 1.3, w: 4.5, h: 0.45, fontSize: 16, fontFace: 'Poppins', color: SUCCESS, bold: true, align: 'center' });

    const perspectives = [
      'Migration vers PostgreSQL',
      'Paiement en ligne (Stripe/CGP)',
      'Application mobile (Django REST)',
      'Géolocalisation GPS véhicules',
      'Notifications push/email (SendGrid)',
      'Intégration calendrier Google',
      'Multi-langues (AR/FR/EN)',
      'Cache Redis + CDN',
      'Docker + CI/CD (GitHub Actions)'
    ];

    perspectives.forEach((p, i) => {
      slide.addText(`✓  ${p}`, { x: 5.4, y: 1.9 + i * 0.43, w: 4, h: 0.4, fontSize: 11, fontFace: 'Poppins', color: GRAY });
    });

    // ===== Slide 17: Conclusion =====
    slide = pptx.addSlide();
    slide.background = { fill: PRIMARY };
    slide.addShape(pptx.ShapeType.rect, { x: 0, y: 0, w: '100%', h: 0.06, fill: { color: SECONDARY } });

    slide.addText('🎯', { x: 4.3, y: 0.8, w: 1.4, h: 0.8, fontSize: 42, align: 'center' });
    slide.addText('Conclusion', {
      x: 1, y: 1.6, w: 8, h: 0.6, fontSize: 30, fontFace: 'Poppins',
      color: WHITE, bold: true, align: 'center'
    });
    slide.addShape(pptx.ShapeType.rect, { x: 4.3, y: 2.25, w: 1.4, h: 0.04, fill: { color: SECONDARY } });

    // Summary
    slide.addShape(pptx.ShapeType.roundRect, {
      x: 1, y: 2.6, w: 8, h: 2.0, rectRadius: 0.1,
      fill: { color: '1E293B' }, line: { color: '334155', width: 1 }
    });
    slide.addText('Résumé du Projet', { x: 1.2, y: 2.7, w: 7.6, h: 0.35, fontSize: 14, fontFace: 'Poppins', color: ACCENT, bold: true });
    slide.addText(
      'Application web complète de gestion de location de voitures développée avec Django 6.0.\n' +
      '• 7 modèles de données, 55+ vues, 39 templates, 42 routes URL\n' +
      '• Système RBAC à 3 rôles (Admin, Employé, Client)\n' +
      '• Workflow complet de réservation avec notifications et historique\n' +
      '• Exports PDF (ReportLab) et CSV • Tests unitaires + E2E (Playwright)',
      { x: 1.2, y: 3.1, w: 7.6, h: 1.3, fontSize: 11, fontFace: 'Poppins', color: GRAY, lineSpacingMultiple: 1.5 }
    );

    // Thanks
    slide.addText('Merci de votre attention', {
      x: 1, y: 5.0, w: 8, h: 0.6, fontSize: 22, fontFace: 'Poppins',
      color: WHITE, bold: true, align: 'center'
    });

    slide.addText([
      { text: 'Kawtar Benyoussef', options: { fontSize: 16, bold: true, color: WHITE } },
      { text: '\nPr. Houda Orchi — Encadrante', options: { fontSize: 13, color: GRAY } },
      { text: '\nEMSI 2025-2026', options: { fontSize: 12, color: GRAY } }
    ], { x: 1, y: 5.6, w: 8, h: 1.2, align: 'center', fontFace: 'Poppins', lineSpacingMultiple: 1.4 });

    // Save
    const fileName = 'presentation_PFA_Location_Voitures.pptx';
    await pptx.writeFile({ fileName });
    console.log(`Fichier ${fileName} généré avec succès !`);

    if (btn) {
      btn.innerHTML = '<i class="fas fa-check"></i> Exporté !';
      setTimeout(() => {
        btn.innerHTML = '<i class="fas fa-file-export"></i> Exporter PPTX';
        btn.disabled = false;
      }, 2000);
    }

  } catch (error) {
    console.error('Erreur lors de l\'export PPTX:', error);
    if (btn) {
      btn.innerHTML = '<i class="fas fa-exclamation-triangle"></i> Erreur';
      setTimeout(() => {
        btn.innerHTML = '<i class="fas fa-file-export"></i> Exporter PPTX';
        btn.disabled = false;
      }, 2000);
    }
  }
}
