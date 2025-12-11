# 📊 Structure des données

## Format d'une annonce extraite

Chaque événement extrait a la structure suivante :

```python
{
    'title': str,                  # Titre de l'événement
    'date': str,                   # Date de l'événement
    'location': str,               # Lieu de l'événement
    'summary': str,                # Description/sommaire
    'contact_name': str,           # Nom du contact
    'phone': str,                  # Numéro de téléphone
    'email': str,                  # Email du contact
    'mailcontact': str,            # Email alternatif du descriptif
    'whatsapp': str,               # Lien WhatsApp
    'email_date': str,             # Date de réception du mail
    'email_from': str,             # Expéditeur du mail
    'lat': float,                  # Latitude géocodée
    'lng': float,                  # Longitude géocodée
}
```

## Exemple complet

```json
{
    "title": "Atelier de poterie",
    "date": "samedi 13 décembre 2025",
    "location": "Nontron",
    "summary": "Atelier de poterie et céramique pour tous les niveaux",
    "contact_name": "Marie Dupont",
    "phone": "0554321234",
    "email": "marie@example.com",
    "mailcontact": "contact@poterie.fr",
    "whatsapp": "https://chat.whatsapp.com/xyz",
    "email_date": "11 décembre 2025",
    "email_from": "crieur@example.org",
    "lat": 45.5233,
    "lng": 0.7667
}
```

## Fichiers de corrections

### `data/corrections_annonces.json`

Permet de corriger des annonces mal extraites (champs mal parsés).

**Format :**
```json
{
    "clé_originale_du_titre": {
        "titre": "Nouveau titre",
        "location": "Nouveau lieu",
        "date": "Nouvelle date",
        ...
    }
}
```

**Exemple :**
```json
{
    "[LES RENDEZ-VOUS DE LA BOUTIQUE": {
        "title": "Les rendez-vous de la boutique Floriane",
        "location": "Nontron",
        "date": "décembre 2025 (toute la période)",
        "contact_name": "Floriane Tourrilhes"
    },
    "MARCHE GOURMAND": {
        "title": "Marché gourmand de Noel",
        "date": "22 décembre 2025",
        "location": "Saint-Saud-Lacoussière"
    }
}
```

**Comment l'utiliser :**
1. Identifiez une annonce mal extraite dans le HTML généré
2. Notez le titre exact comme il apparaît
3. Ajoutez une entrée dans `corrections_annonces.json`
4. Relancez le programme

---

### `data/corrections_geolocalisation.json`

Corrige les lieux que le géocodeur ne trouve pas ou localise mal.

**Format :**
```json
{
    "lieu_exact_du_texte": {
        "lat": 45.5233,
        "lng": 0.7667
    }
}
```

**Exemple :**
```json
{
    "Place de l'Église 24300 Nontron": {
        "lat": 45.5233,
        "lng": 0.7667
    },
    "Rue des Alliés Piégut-Pluviers": {
        "lat": 45.6247,
        "lng": 0.6868
    },
    "Château de Lasteyrie La Rochebeaucourt": {
        "lat": 45.4836,
        "lng": 0.3797
    },
    "Nontron": {
        "lat": 45.5233,
        "lng": 0.7667
    }
}
```

**Comment l'utiliser :**
1. Identifiez un lieu mal localisé (position incorrecte sur la carte)
2. Trouvez les bonnes coordonnées (Google Maps, OpenStreetMap)
3. Ajoutez ou corrigez l'entrée dans `corrections_geolocalisation.json`
4. Relancez le programme

---

### `data/communes_coordinates.json`

Cache auto-généré des coordonnées déjà géocodées (régénéré à chaque exécution).

**Format :**
```json
{
    "Nontron": [45.5233, 0.7667],
    "Saint-Saud-Lacoussière": [45.5439, 0.8184],
    "Thiviers": [45.4144, 0.9194],
    ...
}
```

**⚠️ Ne pas éditer manuellement** - Régénéré automatiquement.

---

## Flux de traitement

```
Emails IMAP
    ↓
Parsing (extraction titre, date, lieu, contacts)
    ↓
Lookup corrections_annonces.json (correction)
    ↓
Géocodage (conversion lieu → coordonnées GPS)
    ↓
Lookup corrections_geolocalisation.json (correction)
    ↓
Cache communes_coordinates.json (acceleration)
    ↓
Génération HTML (annonces.html)
    ↓
Génération Carte (carte_des_annonces.html)
```

---

## HTML généré

### `output/annonces.html`

Page HTML contenant toutes les annonces groupées par **date de réception du mail**.

**Structure :**
- Chaque date de mail = une section
- Les annonces de la même date s'affichent en grille responsive
- Clic sur une annonce = tooltip avec détails

**Classes CSS utilisées :**
- `.date-section` - Conteneur d'une date
- `.date-section-title` - Titre de la date
- `.events-grid-section` - Grille des annonces
- `.event-card` - Carte d'une annonce
- `.event-description-tooltip` - Tooltip au survol

---

### `output/carte_des_annonces.html`

Carte interactive Leaflet.js montrant tous les événements géolocalisés.

**Fonctionnalités :**
- Marqueurs pour chaque événement
- Popup au clic avec détails (titre, date, lieu, contact)
- Zoom/pan pour explorer
- Layer de tuiles (OpenStreetMap)

---

## Flux de données : Main.py

```
main.py
├── EmailReader.get_emails()
│   └── Récupère les emails IMAP
├── extract_events()
│   ├── Parsing des emails
│   └── Extraction des champs
├── apply_corrections()
│   └── Applique corrections_annonces.json
├── geocoding.geocode_all()
│   └── Géocode les lieux (avec corrections_geolocalisation.json)
├── HTMLGenerator.generate()
│   └── Génère annonces.html
└── generate_map()
    └── Génère carte_des_annonces.html
```

---

## Performance

### Optimisations

- **Cache communes_coordinates.json** : Évite re-géocoder les mêmes lieux
- **Throttle API Nominatim** : Délai entre requêtes pour respecter rate limiting
- **Filtre domaine** : Réduit le nombre d'emails à traiter
- **EMAIL_LIMIT** : Limite la charge de traitement

### Temps typiques

- **10 emails** : ~5 secondes
- **50 emails** : ~15-20 secondes (selon géocodage)
- **100 emails** : ~30-45 secondes

---

## Format des événements en HTML

Les annonces sont affichées sous forme de **cartes** avec les informations :

```html
<div class="event-card">
    <h3>Titre de l'événement</h3>
    <p><strong>Date :</strong> samedi 13 décembre 2025</p>
    <p><strong>Lieu :</strong> Nontron</p>
    <p><strong>Contact :</strong> Marie Dupont</p>
    <p><strong>☎️ :</strong> 05 54 32 12 34</p>
    <p><strong>📧 :</strong> marie@example.com</p>
    <p><strong>💬 :</strong> <a href="whatsapp_link">WhatsApp</a></p>
    <p class="event-description">Description complète...</p>
</div>
```

---
