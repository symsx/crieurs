# 📋 Préparation GitHub - Synthèse

## ✅ Travail effectué

### 1. Structure des répertoires créée
```
src/           → Code Python (à organiser)
public/        → Assets web: style.css, script.js, script_carte.js
data/          → Données: corrections_annonces.json, corrections_geolocalisation.json
output/        → Fichiers générés: annonces.html, carte_des_annonces.html
docs/          → Documentation complète
tests/         → Tests (à remplir)
```

### 2. Fichiers de configuration
- ✅ `.gitignore` complet créé
- ✅ `.env.example` amélioré avec documentation
- ✅ `LICENSE` (MIT) créé
- ✅ `requirements.txt` existant

### 3. Documentation complète
- ✅ `docs/README.md` - Guide complet d'installation et utilisation
- ✅ `docs/CONFIGURATION.md` - Tous les paramètres expliqués
- ✅ `docs/DATA_STRUCTURE.md` - Format des données et corrections
- ✅ `docs/PROJECT_STRUCTURE.md` - Structure du projet et guides dev
- ✅ `docs/CONTRIBUTING.md` - Guide de contribution

### 4. État du `.env` utilisateur
```env
EMAIL_ADDRESS=              # Vide - saisie interactive
EMAIL_PASSWORD=             # Vide - saisie interactive
IMAP_SERVER=imap.free.fr
IMAP_PORT=993
PROMPT_FOR_CREDENTIALS=true # Actif - demande à chaque lancement
MAIL_FOLDER=CE
EMAIL_LIMIT=50
DOMAIN_FILTER=gco.ouvaton.net
```

## 🔄 Actions à effectuer

### Avant GitHub

#### 1. Organiser les fichiers Python et assets
```bash
cd /home/sylvain/Documents/crieurs

# Créer les répertoires
mkdir -p src public data output tests

# Copier les fichiers
cp main.py src/main.py
cp email_reader.py src/email_reader.py
cp geocoding.py src/geocoding.py

cp style.css public/style.css
cp script.js public/script.js
cp script_carte.js public/script_carte.js

cp corrections_annonces.json data/
cp corrections_geolocalisation.json data/
cp communes_coordinates.json data/
```

#### 2. Mettre à jour les imports dans le code

**Dans `src/main.py` :**
```python
# Ancien
from email_reader import EmailReader, HTMLGenerator
from geocoding import Geocoder

# Nouveau
from src.email_reader import EmailReader, HTMLGenerator
from src.geocoding import Geocoder
```

**Dans `src/email_reader.py` :**
```python
# Ancien
from geocoding import Geocoder

# Nouveau
from src.geocoding import Geocoder
```

#### 3. Mettre à jour les chemins dans le code

**Dans `src/main.py` (générer HTML) :**
```python
# Ancien
output_file = "annonces.html"
style_path = "style.css"
script_path = "script.js"

# Nouveau
output_file = "output/annonces.html"
style_path = "../public/style.css"
script_path = "../public/script.js"
```

#### 4. Mettre à jour `run.sh`
```bash
# Ancien
python main.py

# Nouveau
python src/main.py
```

#### 5. Mettre à jour les chemins de données

**Dans `src/geocoding.py` et `src/email_reader.py` :**
```python
# Ancien
coordinates_file = "communes_coordinates.json"
corrections_file = "corrections_geolocalisation.json"

# Nouveau (avec gestion du chemin relatif)
import os
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
coordinates_file = os.path.join(base_dir, "data", "communes_coordinates.json")
corrections_file = os.path.join(base_dir, "data", "corrections_geolocalisation.json")
```

#### 6. Tester complètement
```bash
cd /home/sylvain/Documents/crieurs
./run.sh
# Vérifier que annonces.html et carte_des_annonces.html sont générés dans output/
```

#### 7. Supprimer les fichiers dupliqués
```bash
rm main.py email_reader.py geocoding.py
rm style.css script.js script_carte.js
# NE PAS supprimer les fichiers data (déjà copiés)
```

#### 8. Créer un `.gitignore` complet
```
# Environnement
.env
.env.local
venv/
__pycache__/
*.pyc

# IDE
.vscode/
.idea/

# Outputs (ne pas commiter)
output/
*.html

# Cache
geocoding_cache.json
communes_coordinates.json
.cache/

# Fichiers temporaires
*.log
*.tmp
.DS_Store
```

#### 9. Commits Git

```bash
# Commit 1: Documentation et configuration
git add docs/
git add .env.example
git add .gitignore
git add LICENSE
git commit -m "docs: add comprehensive documentation and license"

# Commit 2: Restructuration du projet
git add src/
git add public/
git add data/
git add output/.gitkeep
git rm main.py email_reader.py geocoding.py
git rm style.css script.js script_carte.js
git commit -m "refactor: organize project structure for GitHub

- Move Python source to src/
- Move assets to public/
- Move config files to data/
- Separate generated output to output/
- Complete documentation in docs/"

# Commit 3: Mise à jour des imports et chemins
git add -A
git commit -m "refactor: update imports and file paths for new structure"
```

### 10. Créer le dépôt GitHub

```bash
# Initialiser git (si pas fait)
git init
git remote add origin https://github.com/votre-username/crieurs.git

# Premier push
git branch -M main
git push -u origin main
```

### 11. Configurer GitHub

1. **Description du dépôt :** "Parse email announcements and generate interactive HTML pages with maps"
2. **Topics :** `email-parser`, `imap`, `geocoding`, `interactive-map`, `python`, `html`
3. **License :** MIT
4. **Readme :** `README.md` (GitHub affichera automatiquement)
5. **Pages :** Activer GitHub Pages sur branche `gh-pages` pour servir les fichiers HTML générés

---

## 📝 Fichiers clés pour GitHub

### Root level
- ✅ `README.md` - Documentation principale
- ✅ `.env.example` - Modèle de configuration
- ✅ `.gitignore` - Fichiers à exclure
- ✅ `LICENSE` - MIT License
- ✅ `requirements.txt` - Dépendances
- ✅ `run.sh` - Script de lancement

### Documentation
- ✅ `docs/README.md` - Setup & usage
- ✅ `docs/CONFIGURATION.md` - Tous les paramètres
- ✅ `docs/DATA_STRUCTURE.md` - Format des données
- ✅ `docs/PROJECT_STRUCTURE.md` - Structure du projet
- ✅ `docs/CONTRIBUTING.md` - Guide de contribution

### Code source (à organiser)
- ❌ `src/main.py` - À créer (copier depuis racine)
- ❌ `src/email_reader.py` - À créer (copier depuis racine)
- ❌ `src/geocoding.py` - À créer (copier depuis racine)

### Assets web (à organiser)
- ❌ `public/style.css` - À créer (copier depuis racine)
- ❌ `public/script.js` - À créer (copier depuis racine)
- ❌ `public/script_carte.js` - À créer (copier depuis racine)

### Données (à organiser)
- ❌ `data/corrections_annonces.json` - À créer
- ❌ `data/corrections_geolocalisation.json` - À créer
- ❌ `data/communes_coordinates.json` - À créer

---

## 🎯 Checklist finale

Avant de pousser sur GitHub:

- [ ] Tous les fichiers Python dans `src/`
- [ ] Tous les CSS/JS dans `public/`
- [ ] Tous les JSON dans `data/`
- [ ] `.env` dans `.gitignore` (jamais commiter!)
- [ ] `output/` dans `.gitignore`
- [ ] Documentation complète dans `docs/`
- [ ] `requirements.txt` à jour
- [ ] `LICENSE` présent
- [ ] `.gitignore` correct
- [ ] Code testé et fonctionnel
- [ ] Commits clairs et organisés
- [ ] Dépôt GitHub créé
- [ ] First push réussi

---

## 💡 Recommandations

1. **Commits atomiques :** Un commit = une seule responsabilité
2. **Messages clairs :** `feat:`, `fix:`, `docs:`, `refactor:` en début
3. **Branches :** `feature/x` pour nouvelles fonctionnalités, `fix/x` pour bugs
4. **Pull Requests :** Avant de merger sur main
5. **Documentation :** À jour avec chaque changement

---

**Prêt pour GitHub ! 🚀**
