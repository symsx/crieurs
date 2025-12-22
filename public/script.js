// Gestion du menu de navigation supérieur
console.log('[script.js] Loaded');

function initTopNavigation() {
    const currentPage = window.currentPage || 'sorties';
    const navLinks = document.querySelectorAll('.top-navigation .nav-link');
    
    navLinks.forEach(link => {
        link.classList.remove('active-if-sorties', 'active-if-libre', 'active-if-solidaire', 'active-if-commerciales');
        
        const href = link.getAttribute('href');
        if ((currentPage === 'sorties' && href.includes('annonces.html')) ||
            (currentPage === 'libre' && href.includes('expression_libre.html')) ||
            (currentPage === 'solidaire' && href.includes('solidaire.html')) ||
            (currentPage === 'commerciales' && href.includes('annonces_commerciales.html'))) {
            if (currentPage === 'sorties') {
                link.classList.add('active-if-sorties');
            } else if (currentPage === 'libre') {
                link.classList.add('active-if-libre');
            } else if (currentPage === 'solidaire') {
                link.classList.add('active-if-solidaire');
            } else if (currentPage === 'commerciales') {
                link.classList.add('active-if-commerciales');
            }
        }
    });
}

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

// Initialise la navigation au chargement
document.addEventListener('DOMContentLoaded', initTopNavigation);

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

// Filtre par commune et par date
document.addEventListener('DOMContentLoaded', function() {
    const communeFilter = document.getElementById('commune-filter');
    const dateFilter = document.getElementById('date-filter');
    const eventCards = document.querySelectorAll('.event-card');
    
    console.log('Initializing filters...');
    console.log('Commune filter element:', communeFilter);
    console.log('Date filter element:', dateFilter);
    console.log('Number of event cards:', eventCards.length);
    
    // Fonction pour parser une date au format "samedi 13 décembre 2025" ou "décembre 2025"
    function parseEventDate(dateStr) {
        if (!dateStr) return null;
        
        // Mapping des mois français
        const moisFr = {
            "janvier": 0, "février": 1, "mars": 2, "avril": 3, "mai": 4, "juin": 5,
            "juillet": 6, "août": 7, "septembre": 8, "octobre": 9, "novembre": 10, "décembre": 11
        };
        
        // Enlève le jour de la semaine (ex: "samedi" dans "samedi 13 décembre 2025")
        const withoutDay = dateStr.replace(/^(lundi|mardi|mercredi|jeudi|vendredi|samedi|dimanche)\s+/, '');
        
        // Enlève l'heure si elle est présente (ex: "22 décembre 2025 à 20:00" → "22 décembre 2025")
        const withoutTime = withoutDay.replace(/\s+à\s+\d{1,2}:\d{2}$/, '');
        
        // Regex compatible avec:
        // - "13 décembre 2025"
        // - "décembre 2025" (période complète du mois)
        // - "13 au 15 décembre 2025"
        // - Avec ou sans heure (la partie heure est enlevée avant)
        const periodMatch = withoutTime.match(/^(\d+)?\s*(?:au\s+\d+)?\s*(janvier|février|mars|avril|mai|juin|juillet|août|septembre|octobre|novembre|décembre)\s+(\d{4})$/i);
        
        if (!periodMatch) return null;
        
        const day = periodMatch[1] ? parseInt(periodMatch[1]) : 1;
        const month = moisFr[periodMatch[2].toLowerCase()];
        const year = parseInt(periodMatch[3]);
        
        if (month === undefined) return null;
        
        // Retourne le 1er jour si pas de jour spécifique (ex: "décembre 2025")
        return new Date(year, month, day);
    }
    
    // Fonction pour vérifier si une date est "à venir" (aujourd'hui ou après)
    function isUpcoming(dateStr) {
        if (!dateStr) {
            console.log('isUpcoming: dateStr is empty');
            return false;
        }
        
        const eventDate = parseEventDate(dateStr);
        if (!eventDate) {
            console.log(`isUpcoming: Failed to parse date: "${dateStr}"`);
            return false;
        }
        
        const today = new Date();
        today.setHours(0, 0, 0, 0);  // Réinitialise l'heure à 00:00:00
        
        const isUp = eventDate >= today;
        console.log(`isUpcoming: "${dateStr}" => ${eventDate.toLocaleDateString('fr-FR')} (today: ${today.toLocaleDateString('fr-FR')}) => ${isUp}`);
        
        return isUp;
    }
    
    // Fonction principale de filtrage
    function applyFilters() {
        const selectedCommune = communeFilter ? communeFilter.value : '';
        const selectedDateFilter = dateFilter ? dateFilter.value : 'all';
        
        console.log('Applying filters - Commune:', selectedCommune, 'Date filter:', selectedDateFilter);
        
        eventCards.forEach(card => {
            const cardCommune = card.getAttribute('data-commune');
            const cardEventDate = card.getAttribute('data-event-date');
            
            // Filtre commune
            const communeMatch = !selectedCommune || cardCommune === selectedCommune;
            
            // Filtre date
            let dateMatch = true;
            if (selectedDateFilter === 'upcoming') {
                dateMatch = isUpcoming(cardEventDate);
            }
            
            // Affiche la carte si elle passe tous les filtres
            if (communeMatch && dateMatch) {
                card.style.display = '';
            } else {
                card.style.display = 'none';
            }
        });
    }
    
    // Ajoute les event listeners
    if (communeFilter && eventCards.length > 0) {
        communeFilter.addEventListener('change', applyFilters);
    } else {
        console.warn('Commune filter element or event cards not found');
    }
    
    if (dateFilter && eventCards.length > 0) {
        dateFilter.addEventListener('change', applyFilters);
    } else {
        console.warn('Date filter element or event cards not found');
    }
    
    // Applique les filtres au chargement initial (important pour la valeur par défaut "À venir")
    applyFilters();
});