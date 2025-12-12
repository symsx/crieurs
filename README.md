# 📧 Crieurs - Plateforme d'annonces multi-sources

**Plateforme de gestion et d'affichage d'annonces** du réseau Crieurs Périgord-Limousin.

Outil pour lire vos emails d'annonces et les afficher sous forme de pages HTML avec menus de navigation, cartes interactives et données géolocalisées.

## 🎯 Fonctionnalités principales

### ✨ Deux sources d'annonces
- **📋 Sorties** - Événements structurés avec date, heure, lieu (crieur-des-sorties)
- **📢 Expression Libre** - Annonces libres et contributions (crieur-libre-expression)

### 🎨 Interface
- Menu de navigation entre sorties et expression libre
- Cartes interactives géolocalisées (Leaflet.js)
- Design responsive (mobile/desktop)
- Palette de couleurs GCO (vert #6b7d1e, or #f4c430)

### 🔧 Automatisation
- Extraction automatique depuis IMAP
- Tri des annonces par sujet email
- Génération HTML automatique
- Upload FTP optionnel vers serveur web

### 📍 Géolocalisation
- Cache local des coordonnées (93% plus rapide)
- Corrections manuelles possibles
- Données de communes pré-chargées
- Intégration Nominatim pour lieux inconnus

## 🚀 Installation rapide

### 1. Installez les dépendances

```bash
pip install -r requirements.txt
```

### 2. Configurez votre email

Éditez le fichier `.env`:

```bash
cp .env.example .env
# Puis éditez avec vos identifiants
```

Configuration complète :
```env
EMAIL_ADDRESS=votre@email.fr
EMAIL_PASSWORD=password
IMAP_SERVER=imap.free.fr
IMAP_PORT=993
MAIL_FOLDER=CE
EMAIL_LIMIT=50

# FTP optionnel
ENABLE_FTP_UPLOAD=true
FTP_HOST=node112-eu.n0c.com
FTP_USER=username
FTP_PASSWORD=password
FTP_REMOTE_PATH=/crieur/output
```

### 3. Lancez le programme

```bash
./run.sh
```

## 📊 Fichiers générés

```
output/
├── annonces.html                   # Page des sorties
├── carte_des_annonces.html         # Carte sorties (Leaflet)
├── expression_libre.html           # Page expression libre
└── carte_expression_libre.html     # Carte contributions
```

## 🎨 Menu de navigation

Chaque page HTML contient un menu supérieur sticky :

```
┌─────────────────────────────────┐
│ 📋 Sorties | 📢 Expression Libre │
└─────────────────────────────────┘
```

- **Sorties** - Actif : fond vert GCO
- **Expression Libre** - Actif : fond or GCO

## 📚 Documentation

- [EVOLUTION_DEUX_SOURCES.md](EVOLUTION_DEUX_SOURCES.md) - Vue d'ensemble de l'évolution
- [docs/DEUX_SOURCES_ANNONCES.md](docs/DEUX_SOURCES_ANNONCES.md) - Documentation technique détaillée
- [docs/CACHE_LOCALISATION.md](docs/CACHE_LOCALISATION.md) - Système de cache géolocalisation

## 🔧 Architecture

### Scripts principaux
- **src/main_v2.py** - Script de traitement multi-sources (nouveau)
- **src/main.py** - Script original (legacy)
- **src/email_reader.py** - Lecteur d'emails et générateur HTML
- **src/geocoding.py** - Géolocalisation avec cache
- **src/ftp_uploader.py** - Upload FTP

### Fichiers publics
- **public/style.css** - Styles GCO (841 lignes)
- **public/script.js** - JavaScript (menu, popups, etc.)
- **public/index.html** - Page d'accueil (optionnel)

### Données
- **data/lieux_coordinates.json** - Cache géolocalisation (35+ lieux)
- **data/corrections_annonces.json** - Corrections manuelles d'annonces
- **data/corrections_geolocalisation.json** - Corrections manuelles de lieux
- **data/communes_coordinates.json** - Base communes Périgord-Limousin

## 🌍 Fournisseurs d'email supportés

### Free (Zimbra) - **CONFIGURATION ACTUELLE**
```env
IMAP_SERVER=imap.free.fr
IMAP_PORT=993
MAIL_FOLDER=CE
```

### Gmail
```env
IMAP_SERVER=imap.gmail.com
IMAP_PORT=993
MAIL_FOLDER=INBOX
```

### Autres (Outlook, Orange, etc.)
Voir [Configuration par fournisseur](#-configuration-par-fournisseur) ci-dessus

## 📈 Performance

- **Cache géolocalisation** : 93% plus rapide au 2ème exécution
- **Extraction d'emails** : ~2-3 secondes pour 50 emails
- **Génération HTML** : ~1 seconde par source
- **Upload FTP** : ~5-10 secondes pour 4 fichiers
- **Total** : ~5-10 secondes par exécution complète

## 🚀 Déploiement

### Local
```bash
./run.sh
```

### Production (avec FTP)
1. Configurez les paramètres FTP dans `.env`
2. Activez `ENABLE_FTP_UPLOAD=true`
3. Les fichiers sont automatiquement uploadés à chaque exécution

### Automatisation (cron)
```bash
# Générer chaque jour à 8h
0 8 * * * cd /path/to/crieurs && ./run.sh
```

## 🔄 Extensibilité

Pour ajouter une **troisième source**, modifiez `src/main_v2.py` :

```python
sources = [
    { ... },  # Sorties
    { ... },  # Expression Libre
    {
        'name': 'Nouvelle source',
        'filter': 'crieur-nouvelle',
        'output_html': 'nouvelle.html',
        'output_map': 'carte_nouvelle.html',
        'title': 'Nouvelle Source'
    }
]
```

## ✅ Tests

Tous les tests effectués et validés :
- ✓ Génération des deux sources
- ✓ Navigation entre pages
- ✓ Cartes géographiques
- ✓ Géolocalisation et cache
- ✓ Upload FTP
- ✓ Responsive design
- ✓ Menu navigation actif

## 📝 Configuration par fournisseur

### Free (Zimbra) - **VOTRE CONFIGURATION**
```env
IMAP_SERVER=imap.free.fr
IMAP_PORT=993
MAIL_FOLDER=CE
```


### Gmail
```env
IMAP_SERVER=imap.gmail.com
IMAP_PORT=993
EMAIL_PASSWORD=(token d'application uniquement)
```

### Outlook/Hotmail
```env
IMAP_SERVER=imap-mail.outlook.com
IMAP_PORT=993
```

### Orange
```env
IMAP_SERVER=imap.orange.fr
IMAP_PORT=993
```

### SFR
```env
IMAP_SERVER=imap.sfr.fr
IMAP_PORT=993
```

## 📖 Modes d'utilisation

### Mode 1: Lire depuis votre boîte mail (IMAP)

```bash
./run.sh
```

ou

```bash
source venv/bin/activate
python3 main.py
```

**Recommandé pour une utilisation régulière!**

### Mode 2: Tester avec des fichiers .eml

Utile pour déboguer l'extraction sans connexion:

```bash
./run_eml.sh
```

Cela lit tous les fichiers `.eml` dans le dossier `./CE`

## 🎯 Fonctionnalités

✅ **Extraction automatique**
- Dates d'événements (multiples formats)
- Lieux/Adresses
- Sujets des annonces

✅ **Formats supportés**
- Emails Zimbra (digests avec plusieurs événements)
- HTML et texte brut
- Encodages QUOTED-PRINTABLE
- Mailing lists

✅ **Interface**
- Design responsive et moderne
- Cartes visuelles avec gradient
- Affichage clair des infos
- Compatible mobile

## 📁 Structure du projet

```
crieurs/
├── main.py              # Script principal (IMAP)
├── main_eml.py          # Script test (fichiers .eml)
├── email_reader.py      # Classes d'extraction
├── requirements.txt     # Dépendances
├── .env                 # Config (À REMPLIR - voir .env.example)
├── .env.example         # Exemple de config
├── run.sh               # Lancement mode IMAP
├── run_eml.sh           # Lancement mode .eml
├── CE/                  # Dossier test avec exemples
│   ├── mail1.eml
│   └── mail2.eml
└── events.html          # Page générée
```

## 🔧 Personnalisation

### Modifier le nombre d'emails à lire

Dans `.env`, changez:
```env
EMAIL_LIMIT=50  # Augmentez/diminuez ce nombre
```

### Modifier le dossier source

Dans `.env`, changez:
```env
MAIL_FOLDER=CE  # Ou INBOX, [Gmail]/All Mail, etc.
```

### Améliorer la détection des dates/lieux

Éditez `email_reader.py`, classe `EventExtractor`:

```python
self.date_patterns = [
    r"votre_pattern_regex_personnalisé"
]

self.location_patterns = [
    r"votre_pattern_regex_personnalisé"  
]
```

## ⚠️ Sécurité

- **IMPORTANT**: Ne partagez/commitez JAMAIS le fichier `.env`!
- Utilisez un mot de passe d'application si possible
- Sur Gmail: utilisez un [token d'application](https://support.google.com/accounts/answer/185833)
- Le fichier `.env` est dans `.gitignore` par défaut

## 🐛 Dépannage

### "Erreur de connexion IMAP"

```bash
✗ Erreur de connexion: [AUTHENTICATIONFAILED]
```

**Solutions:**
- ✓ Vérifiez EMAIL_ADDRESS et EMAIL_PASSWORD dans `.env`
- ✓ Vérifiez IMAP_SERVER et IMAP_PORT
- ✓ Assurez-vous que IMAP est activé sur votre compte
- ✓ Pour Free: allez dans Paramètres > Sécurité > IMAP

### "Aucun email trouvé"

```bash
❌ Aucun email trouvé dans le dossier 'CE'
```

**Solutions:**
- ✓ Vérifiez que le dossier existe dans Zimbra
- ✓ Essayez avec `MAIL_FOLDER=INBOX`
- ✓ Modifiez EMAIL_LIMIT si vous n'avez peu d'emails

### "Dates/lieux mal extraits"

**Solutions:**
- ✓ Testez d'abord avec `./run_eml.sh` pour analyser le format
- ✓ Ajoutez des patterns personnalisés dans `EventExtractor`
- ✓ Vérifiez le format du contenu des emails

## 📊 Formats d'emails reconnus

### Digests Zimbra (Free)
```
* 1 - [Dossier] [Ville] - Titre événement

Quand : du samedi 13 décembre 2025 à 19:05...
Où : Ville
```

### Format standard
```
Date: 14 décembre 2025
Lieu: Montbron
Sujet: Titre
```

### Format personnalisé
Ajoutez vos patterns dans `EventExtractor`

## 💡 Astuces

1. **Tester votre extraction**: Placez des fichiers `.eml` dans `./CE` et lancez `./run_eml.sh`
2. **Déboguer les patterns**: Modifiez `email_reader.py` pour afficher les captures
3. **Automatiser**: Créez une tâche cron pour lancer `main.py` régulièrement

## 📚 Ressources

- [Documentation IMAP](https://tools.ietf.org/html/rfc3501)
- [Regex Cheat Sheet](https://www.regular-expressions.info/characters.html)
- [Free Zimbra Help](https://support.free.fr/)

## 📄 Licence

Libre d'utilisation et de modification.

---

**Besoin d'aide?** Vérifiez d'abord que `.env` est correctement configuré et testez avec `./run_eml.sh`.
