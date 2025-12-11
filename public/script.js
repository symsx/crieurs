// Gestion du menu burger
const burgerMenu = document.querySelector('.burger-menu');
const mobileMenu = document.querySelector('.mobile-menu');

if (burgerMenu && mobileMenu) {
    burgerMenu.addEventListener('click', function() {
        burgerMenu.classList.toggle('active');
        mobileMenu.classList.toggle('active');
    });
    
    // Ferme le menu quand on clique sur un lien
    const mobileMenuLinks = mobileMenu.querySelectorAll('a');
    mobileMenuLinks.forEach(link => {
        link.addEventListener('click', function() {
            burgerMenu.classList.remove('active');
            mobileMenu.classList.remove('active');
        });
    });
}

// Gestion des tooltips de description
const globalTooltip = document.createElement('div');
globalTooltip.id = 'global-tooltip';
globalTooltip.style.cssText = 'display: none; position: fixed; background: rgba(0, 0, 0, 0.95); color: white; padding: 15px; border-radius: 8px; font-size: 0.85em; line-height: 1.5; max-width: min(90vw, 700px); z-index: 10000; white-space: normal; word-wrap: break-word; box-shadow: 0 15px 40px rgba(0, 0, 0, 0.6); border: 2px solid rgba(102, 126, 234, 0.5); pointer-events: none;';
document.body.appendChild(globalTooltip);

// Gère le positionnement des tooltips en fixed
document.querySelectorAll('.event-card h3').forEach(h3 => {
    const tooltip = h3.querySelector('.event-description-tooltip');
    if (tooltip) {
        h3.addEventListener('mouseenter', () => {
            const rect = h3.getBoundingClientRect();
            
            // Copie le contenu de la description dans le tooltip global
            globalTooltip.innerHTML = tooltip.innerHTML;
            globalTooltip.style.display = 'block';
            
            // Pour position: fixed, utiliser les coordonnées du viewport SANS ajouter scrollY
            // car getBoundingClientRect() retourne déjà les coordonnées de l'écran
            let top = rect.bottom + 8;  // 8px sous le titre
            let left = rect.left;
            
            // Applique le positionnement initial
            globalTooltip.style.top = top + 'px';
            globalTooltip.style.left = left + 'px';
            
            // Récupère la taille du tooltip pour ajustements
            const tooltipRect = globalTooltip.getBoundingClientRect();
            
            // Vérifie position horizontale : si dépasse à droite, recentrer
            if (left + tooltipRect.width > window.innerWidth - 10) {
                left = window.innerWidth - tooltipRect.width - 10;
            }
            // Vérifie qu'on ne dépasse pas à gauche
            if (left < 10) {
                left = 10;
            }
            
            // Vérifie position verticale : si dépasse en bas, afficher au-dessus
            if (top + tooltipRect.height > window.innerHeight - 10) {
                top = rect.top - tooltipRect.height - 8;  // 8px au-dessus du titre
            }
            
            // Applique les positions ajustées
            globalTooltip.style.top = top + 'px';
            globalTooltip.style.left = left + 'px';
        });
        
        h3.addEventListener('mouseleave', () => {
            globalTooltip.style.display = 'none';
        });
    }
});
