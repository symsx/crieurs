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
globalTooltip.style.cssText = 'display: none; position: fixed; background: white; color: #333; padding: 20px; border-radius: 12px; font-size: 0.95em; line-height: 1.6; max-height: 400px; z-index: 10000; white-space: pre-wrap; word-wrap: break-word; box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1); border-left: 5px solid #6b7d1e; overflow-y: auto; box-sizing: border-box;';
document.body.appendChild(globalTooltip);

let currentCard = null;
let hideTimeout = null;

function hideTooltip() {
    globalTooltip.style.display = 'none';
    currentCard = null;
}

function cancelHideTimeout() {
    if (hideTimeout) {
        clearTimeout(hideTimeout);
        hideTimeout = null;
    }
}

function scheduleHideTooltip() {
    cancelHideTimeout();
    hideTimeout = setTimeout(hideTooltip, 200);
}

// Gère le positionnement des tooltips en fixed
document.querySelectorAll('.event-card').forEach(card => {
    const h3 = card.querySelector('h3');
    const tooltip = card.querySelector('.event-description-tooltip');
    
    if (h3 && tooltip) {
        function showTooltip() {
            cancelHideTimeout();
            const cardRect = card.getBoundingClientRect();
            const h3Rect = h3.getBoundingClientRect();
            
            // Copie le contenu de la description dans le tooltip global
            globalTooltip.innerHTML = tooltip.innerHTML;
            globalTooltip.style.display = 'block';
            globalTooltip.style.width = cardRect.width + 'px';
            
            // Positionne la popup sous le h3, alignée avec la carte
            let top = h3Rect.bottom + 8;  // 8px sous le titre
            let left = cardRect.left;
            
            // Applique le positionnement initial
            globalTooltip.style.top = top + 'px';
            globalTooltip.style.left = left + 'px';
            
            // Récupère la taille du tooltip pour ajustements
            const tooltipRect = globalTooltip.getBoundingClientRect();
            
            // Vérifie position verticale : si dépasse en bas, afficher au-dessus
            if (top + tooltipRect.height > window.innerHeight - 10) {
                top = h3Rect.top - tooltipRect.height - 8;  // 8px au-dessus du titre
            }
            
            // Applique les positions ajustées
            globalTooltip.style.top = top + 'px';
            globalTooltip.style.left = left + 'px';
        }
        
        // Ouverture au survol du h3
        h3.addEventListener('mouseenter', () => {
            currentCard = card;
            showTooltip();
        });
        
        // Début de la minuterie de fermeture quand on quitte la carte
        card.addEventListener('mouseleave', () => {
            if (currentCard === card) {
                scheduleHideTooltip();
            }
        });
        
        // Annule la minuterie si on rentre dans la carte
        card.addEventListener('mouseenter', () => {
            cancelHideTimeout();
        });
        
        // Repositionne la popup si on bouge la souris dans la carte
        card.addEventListener('mousemove', () => {
            if (globalTooltip.style.display === 'block' && currentCard === card) {
                showTooltip();
            }
        });
    }
});

// Événements pour la popup elle-même
globalTooltip.addEventListener('mouseenter', () => {
    cancelHideTimeout();
});

globalTooltip.addEventListener('mouseleave', () => {
    if (currentCard) {
        scheduleHideTooltip();
    }
});
