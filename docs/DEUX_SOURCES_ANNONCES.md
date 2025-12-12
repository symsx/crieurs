# Évolution du projet Crieur - Deux sources d'annonces

## Vue d'ensemble

Le projet **Crieur** a été évolué pour traiter **deux sources d'annonces distinctes** :

1. **📋 Sorties** - Annonces d'événements de sorties (`crieur-des-sorties`)
2. **📢 Expression Libre** - Annonces en expression libre (`crieur-libre-expression`)

## Architecture

### Structure des fichiers générés

```
output/
├── annonces.html                    # Page des sorties
├── carte_des_annonces.html          # Carte des sorties
├── expression_libre.html            # Page expression libre
└── carte_expression_libre.html      # Carte expression libre
```

### Traitement des emails

Le système récupère les emails d'un **même dossier IMAP** (défini dans `.env` par `MAIL_FOLDER`) et les filtre selon le **sujet** :

- `crieur-des-sorties` → Page annonces.html
- `crieur-libre-expression` → Page expression_libre.html

## Fonctionnement

### Script principal : `src/main_v2.py`

Le nouveau script traite séquentiellement :

1. **Connexion IMAP** - Récupère tous les emails du dossier configuré
2. **Boucle sur les deux sources** :
   - Filtre les emails par sujet
   - Extrait les événements
   - Génère la page HTML
   - Génère la carte interactive
3. **Upload FTP** - Envoie les 4 fichiers HTML au serveur

```python
sources = [
    {
        'name': 'Sorties',
        'filter': 'crieur-des-sorties',
        'output_html': 'annonces.html',
        'output_map': 'carte_des_annonces.html',
        'title': 'Annonces Crieur'
    },
    {
        'name': 'Expression Libre',
        'filter': 'crieur-libre-expression',
        'output_html': 'expression_libre.html',
        'output_map': 'carte_expression_libre.html',
        'title': 'Expression Libre Crieur'
    }
]
```

### Navigation utilisateur

#### Menu de navigation horizontal
Chaque page HTML contient un menu en haut :
- **📋 Sorties** (actif sur annonces.html) - Fond vert GCO
- **📢 Expression Libre** (actif sur expression_libre.html) - Fond or GCO

```html
<div class="top-navigation">
    <a href="annonces.html" class="nav-link active-if-sorties">📋 Sorties</a>
    <a href="expression_libre.html" class="nav-link active-if-libre">📢 Expression Libre</a>
</div>
```

#### Menu mobile (burger)
Le menu burger s'adapte avec les nouveaux liens :
```
📋 Sorties
📢 Expression Libre
─────────────
🗺️ Carte (contextualisée)
```

### Style CSS

```css
/* Menu de navigation supérieur */
.top-navigation {
    background: white;
    border-bottom: 3px solid var(--gco-green);
    position: sticky;
    top: 0;
    z-index: 100;
}

.top-navigation .active-if-sorties {
    background: var(--gco-green);  /* Vert */
    color: white;
}

.top-navigation .active-if-libre {
    background: var(--gco-gold);   /* Or */
    color: #000;
}
```

### Gestion du JavaScript

Le fichier `public/script.js` initialisait le menu selon la page active :

```javascript
function initTopNavigation() {
    const currentPage = window.currentPage || 'sorties';
    // Active le lien approprié selon la page
}

document.addEventListener('DOMContentLoaded', initTopNavigation);
```

La variable `currentPage` est définie dans le HTML généré :
```html
<script>
    window.currentPage = 'sorties'; // ou 'libre'
</script>
```

## Différences entre les deux pages

### Sorties
- **Titre** : "📅 Annonces Crieur"
- **Sujet email** : "crieur-des-sorties"
- **Lien carte** : "🗺️ Carte des sorties"
- **Éléments affichés** :
  - Date/heure de l'événement
  - Lieu
  - Descriptif
  - Lien du site internet
  - Lien agenda
  - Pièces jointes

### Expression Libre
- **Titre** : "📢 Expression Libre Crieur"
- **Sujet email** : "crieur-libre-expression"
- **Lien carte** : "🗺️ Carte des contributions"
- **Éléments affichés** : Même structure que les sorties

## Génération et déploiement

### Exécution locale
```bash
./run.sh
```

Résultat :
```
============================================================
📰 Sorties
============================================================
✓ Email trouvés
✓ Événements extraits
✓ HTML généré
✓ Carte générée

============================================================
📰 Expression Libre
============================================================
✓ Email trouvés
✓ Événements extraits
✓ HTML généré
✓ Carte générée

============================================================
📤 Upload FTP
✓ 4 fichier(s) uploadé(s)

============================================================
✅ Résumé:
  ✓ Sorties
  ✓ Expression Libre
============================================================
```

### Configuration `.env`

```env
EMAIL_ADDRESS=...
EMAIL_PASSWORD=...
MAIL_FOLDER=CE              # Dossier contenant les deux types d'emails

# FTP (optionnel)
ENABLE_FTP_UPLOAD=true
FTP_HOST=...
FTP_USER=...
FTP_PASSWORD=...
FTP_REMOTE_PATH=/crieur/output
```

## Modifications du code

### Nouveaux fichiers
- `src/main_v2.py` - Nouveau script principal

### Fichiers modifiés
- `run.sh` - Appelle `main_v2.py` au lieu de `main.py`
- `src/email_reader.py` - Classe `HTMLGenerator` enrichie
- `public/style.css` - Styles pour le menu de navigation
- `public/script.js` - Gestion du menu actif

### Fichiers inchangés
- Logique d'extraction des emails (réutilisée)
- Logique de géolocalisation (réutilisée)
- Logique d'upload FTP (réutilisée)

## Extension future

Pour ajouter une **troisième source**, il suffit d'ajouter un dictionnaire à la liste `sources` dans `main_v2.py` :

```python
{
    'name': 'Nouvelle catégorie',
    'filter': 'crieur-nouvelle-categorie',
    'output_html': 'nouvelle_categorie.html',
    'output_map': 'carte_nouvelle_categorie.html',
    'title': 'Nouvelle Catégorie Crieur'
}
```

Puis ajouter les couleurs dans le menu CSS si souhaité.

## Notes importantes

1. **Les emails doivent avoir des sujets différents** pour être correctement triés
2. **Le dossier IMAP est commun** aux deux sources - les emails sont filtrés par sujet
3. **Les deux pages partagent le même CSS et JavaScript** - cohérence visuelle garantie
4. **Upload FTP simultané** - Les 4 fichiers sont uploadés ensemble
5. **Chaque page a sa propre carte** - Pas de mélange de localisation entre sorties et contributions

## Statut

✅ **Implémentation complète**
- Navigation entre sorties et expression libre
- Deux pages HTML générées automatiquement
- Deux cartes interactives indépendantes
- Upload FTP intégré
- Menu responsive adapté mobile/desktop
