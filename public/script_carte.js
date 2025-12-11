// Données des marqueurs
const markers = window.markersData || [];

// Initialise la carte
function initializeMap(lat, lng) {
    const map = L.map('map').setView([lat, lng], 10);

    // Ajoute la couche de tuiles OpenStreetMap
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors',
        maxZoom: 19
    }).addTo(map);

    // Groupe de marqueurs en cluster
    const markerClusterGroup = L.markerClusterGroup({
        maxClusterRadius: 80,
        disableClusteringAtZoom: 15
    });

    // Ajoute les marqueurs
    markers.forEach((marker, index) => {
        const popup = `
            <div class="popup-content">
                <h4>${marker.title}</h4>
                <p><span class="popup-label">Lieu:</span> ${marker.location}</p>
                <p><span class="popup-label">Date:</span> ${marker.date}</p>
                ${marker.description ? `<p><span class="popup-label">Description:</span><br>${marker.description}</p>` : ''}
                ${marker.links && marker.links.length > 0 ? `<p><span class="popup-label">Liens:</span><br>${marker.links.map(l => `<a href="${l}" target="_blank" rel="noopener" class="popup-link">🔗 Lien</a>`).join('<br>')}</p>` : ''}
            </div>
        `;

        const customIcon = L.divIcon({
            className: 'custom-marker',
            html: `<div style="background-color: #667eea; color: white; width: 40px; height: 40px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold; border: 3px solid white; box-shadow: 0 2px 8px rgba(0,0,0,0.3);">📍</div>`,
            iconSize: [40, 40],
            iconAnchor: [20, 20],
            popupAnchor: [0, -20]
        });

        const markerObj = L.marker([marker.lat, marker.lng], { icon: customIcon })
            .bindPopup(popup)
            .on('click', function() {
                // Highlight dans la sidebar
                document.querySelectorAll('.event-list-item').forEach(el => el.classList.remove('active'));
                const items = document.querySelectorAll('.event-list-item');
                if (items[index]) {
                    items[index].classList.add('active');
                }
            });

        markerClusterGroup.addLayer(markerObj);
    });

    map.addLayer(markerClusterGroup);

    // Fonction pour centrer la carte sur un événement
    window.focusEvent = function(lat, lng) {
        map.setView([lat, lng], 13);
        // Ouvre le popup du marqueur si possible
        markerClusterGroup.eachLayer(layer => {
            if (Math.abs(layer.getLatLng().lat - lat) < 0.0001 && Math.abs(layer.getLatLng().lng - lng) < 0.0001) {
                layer.openPopup();
            }
        });
    };
}

// Gère le menu burger sur mobile
document.addEventListener('DOMContentLoaded', function() {
    const burgerMenu = document.querySelector('.burger-menu');
    const mobileMenu = document.querySelector('.mobile-menu');

    if (burgerMenu && mobileMenu) {
        burgerMenu.addEventListener('click', function() {
            burgerMenu.classList.toggle('active');
            mobileMenu.classList.toggle('active');
        });

        // Ferme le menu quand on clique sur un lien
        const menuLinks = mobileMenu.querySelectorAll('a');
        menuLinks.forEach(link => {
            link.addEventListener('click', function() {
                burgerMenu.classList.remove('active');
                mobileMenu.classList.remove('active');
            });
        });
    }
});
