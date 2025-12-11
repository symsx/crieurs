# 📊 Crieurs - Email Announcement Reader

Un outil puissant pour lire vos emails d'annonces d'événements et les afficher sous forme de **page HTML interactive** avec **carte géographique** intégrée.

> **Spécialisé pour Zimbra Free** avec support des autres fournisseurs (Gmail, Outlook, etc.)

---

## ✨ Caractéristiques

- 📧 **Lecteur IMAP** : Compatible avec Free, Gmail, Outlook et autres serveurs IMAP
- 📝 **Extraction automatique** : Extrait dates, lieux, contacts, téléphones, emails
- 🗺️ **Carte interactive** : Affiche les événements sur une carte Leaflet.js
- 📱 **Interface responsive** : Adaptée au mobile avec menu burger
- 🎨 **Design moderne** : CSS/JavaScript externalisés, dark mode intégré
- 🔐 **Saisie interactive** : Demande les identifiants si absents du `.env`
- 🏗️ **Corrections manuelles** : Système de corrections pour données malformées
- 📤 **Upload FTP** : Upload automatique des pages HTML vers votre site web

---

## 🚀 Installation rapide

### Prérequis
- Python 3.7+
- `pip` (gestionnaire de paquets Python)

### 1. Cloner le dépôt
```bash
git clone https://github.com/votre-username/crieurs.git
cd crieurs
```

### 2. Installer les dépendances
```bash
pip install -r requirements.txt
```

### 3. Configurer l'accès email

#### Option A : Fichier `.env` (recommandé pour usage répété)
```bash
cp .env.example .env
nano .env
```

Remplissez avec vos identifiants :
```env
EMAIL_ADDRESS=votre.email@free.fr
EMAIL_PASSWORD=votre_mot_de_passe
IMAP_SERVER=imap.free.fr
IMAP_PORT=993
MAIL_FOLDER=CE
EMAIL_LIMIT=50
DOMAIN_FILTER=gco.ouvaton.net
PROMPT_FOR_CREDENTIALS=false
```

#### Option B : Saisie interactive (sans fichier `.env`)
Laissez les champs vides dans `.env` et définissez `PROMPT_FOR_CREDENTIALS=true` :
```env
EMAIL_ADDRESS=
EMAIL_PASSWORD=
PROMPT_FOR_CREDENTIALS=true
```

### 4. Lancer le programme
```bash
./run.sh
```

Les fichiers générés seront disponibles dans le répertoire `output/` :
- `annonces.html` - Page avec toutes les annonces
- `carte_des_annonces.html` - Carte interactive

---

## 📋 Configuration par fournisseur

### Free (Zimbra) - ✅ RECOMMANDÉ
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
EMAIL_PASSWORD=<app-password>  # Génère un mot de passe d'application
```

### Outlook / Microsoft 365
```env
IMAP_SERVER=outlook.office365.com
IMAP_PORT=993
MAIL_FOLDER=INBOX
```

---

## 📁 Structure du projet

```
crieurs/
├── src/
│   ├── main.py                    # Script principal
│   ├── email_reader.py            # Lecteur IMAP et parseur
│   └── geocoding.py               # Géocodage avec Nominatim
├── public/
│   ├── style.css                  # Feuille de style
│   ├── script.js                  # Menu burger et interactions
│   └── script_carte.js            # Logique de la carte
├── output/                        # Fichiers générés (HTML, carte)
├── data/
│   ├── corrections_annonces.json           # Corrections d'annonces
│   ├── corrections_geolocalisation.json    # Corrections de géolocalisation
│   └── communes_coordinates.json           # Cache des coordonnées
├── docs/                          # Documentation
├── .env.example                   # Modèle de configuration
├── .gitignore                     # Fichiers à ignorer
├── requirements.txt               # Dépendances Python
└── run.sh                         # Script de lancement

```

---

## 📖 Documentation

- **[Configuration complète](docs/CONFIGURATION.md)** - Tous les paramètres disponibles
- **[API Geocoding](docs/GEOCODING.md)** - Système de géocodage et corrections
- **[Structure des données](docs/DATA_STRUCTURE.md)** - Format des événements extraits

---

## 🛠️ Utilisation avancée

### Filtrer par domaine d'expédition
```env
DOMAIN_FILTER=gco.ouvaton.net
```

### Limiter le nombre d'emails
```env
EMAIL_LIMIT=20
```

### Toujours saisir les identifiants
```env
PROMPT_FOR_CREDENTIALS=true
```

### Ajouter des corrections manuelles

Editez `data/corrections_annonces.json` pour corriger des annonces malformées :
```json
{
  "[LES RENDEZ-VOUS DE LA BOUTIQUE": {
    "location": "Nontron"
  }
}
```

### Upload FTP automatique

Uploadez automatiquement les fichiers HTML vers votre site :
```env
ENABLE_FTP_UPLOAD=true
FTP_HOST=ftp.votre-site.com
FTP_USER=utilisateur
FTP_PASSWORD=motdepasse
FTP_REMOTE_PATH=/public_html/crieurs/
```

Consultez [FTP_UPLOAD.md](FTP_UPLOAD.md) pour la configuration détaillée.

---

## 🔧 Développement

### Installation en mode développement
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Lancer les tests
```bash
python -m pytest tests/
```

### Modifier le code
- `src/main.py` - Point d'entrée principal
- `src/email_reader.py` - Logique IMAP et parsing
- `src/geocoding.py` - Géocodage des adresses
- `public/style.css` - Styles CSS
- `public/script.js` et `script_carte.js` - Interactivité

---

## 🐛 Troubleshooting

### Erreur : "Identifiants manquants"
→ Remplissez `.env` ou définissez `PROMPT_FOR_CREDENTIALS=true`

### Erreur : "Erreur de connexion IMAP"
→ Vérifiez `IMAP_SERVER`, `IMAP_PORT` et les identifiants

### Certains événements ne s'affichent pas sur la carte
→ Vérifiez `data/corrections_geolocalisation.json` pour les lieux introuvables

### Les annonces ne s'affichent pas en lignes
→ L'affichage en grille est normal. Ajustez `public/style.css` si nécessaire

---

## 📝 Contribution

Les contributions sont bienvenues ! Consultez [CONTRIBUTING.md](docs/CONTRIBUTING.md) pour les directives.

---

## 📄 Licence

Ce projet est sous licence MIT. Voir [LICENSE](LICENSE) pour plus de détails.

---

## 👤 Auteur

Créé par [votre nom/organisation]

## 📧 Support

Pour toute question ou problème, ouvrez une [issue](https://github.com/votre-username/crieurs/issues).
