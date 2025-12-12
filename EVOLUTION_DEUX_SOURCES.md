# 🚀 Évolution du projet Crieur - Deux sources d'annonces

## 📢 Résumé de l'évolution

Le projet **Crieur** a été étendu pour gérer **deux sources d'annonces distinctes** au sein d'un même système :

### Avant (version 1)
- 1 source : emails avec sujet "crieur-des-sorties"
- 1 page : annonces.html
- 1 carte : carte_des_annonces.html

### Après (version 2)
- 2 sources : emails triés par sujet
- 2 pages : annonces.html + expression_libre.html
- 2 cartes : carte_des_annonces.html + carte_expression_libre.html
- **Menu de navigation** pour passer entre les deux pages

---

## 🎯 Les deux sources

### 📋 Sorties
**Sujet email** : `crieur-des-sorties`

Annonces d'**événements de sorties** avec :
- Date et heure de l'événement
- Lieu précis (géolocalisé)
- Descriptif détaillé
- Liens externes
- Contacts organisateurs

**Fichiers générés** :
- `annonces.html` - Page des sorties
- `carte_des_annonces.html` - Carte interactive

### 📢 Expression Libre
**Sujet email** : `crieur-libre-expression`

Annonces en **expression libre** (contributions, infos, news, etc.) avec :
- Titre et descriptif
- Contact auteur
- Liens attachés
- Même structure visuelle que sorties

**Fichiers générés** :
- `expression_libre.html` - Page expression libre
- `carte_expression_libre.html` - Carte interactive

---

## 💻 Architecture technique

### Script principal : `src/main_v2.py`

Remplace `src/main.py` (conservé pour compatibilité).

**Flux d'exécution** :
```
1. Connexion IMAP au dossier configuré
2. Récupération de TOUS les emails
3. Boucle sur deux sources :
   a. Filtre les emails par sujet
   b. Extrait les événements
   c. Génère HTML + Carte
4. Upload FTP (optionnel)
5. Résumé des résultats
```

### Menu de navigation

Chaque page HTML contient un **menu sticky en haut** :

```
┌─────────────────────────────────┐
│ 📋 Sorties | 📢 Expression Libre │  ← Menu actif selon page
└─────────────────────────────────┘
```

**Code HTML généré** :
```html
<div class="top-navigation">
    <a href="annonces.html" class="nav-link">📋 Sorties</a>
    <a href="expression_libre.html" class="nav-link">📢 Expression Libre</a>
</div>
```

**Couleurs** :
- Sorties active : vert GCO (#6b7d1e)
- Expression Libre active : or GCO (#f4c430)

### Modifications du code

**Fichiers modifiés** :
- ✏️ `run.sh` - Lance `main_v2.py`
- ✏️ `src/email_reader.py` - HTMLGenerator enrichie
- ✏️ `public/style.css` - Styles menu navigation
- ✏️ `public/script.js` - Gestion menu actif

**Fichiers créés** :
- ✨ `src/main_v2.py` - Nouveau script principal
- ✨ `docs/DEUX_SOURCES_ANNONCES.md` - Documentation technique

**Fichiers conservés** :
- 📦 `src/main.py` - Legacy (non utilisé)
- 📦 Logique d'extraction (réutilisée)
- 📦 Logique de géolocalisation (réutilisée)
- 📦 Logique FTP (réutilisée)

---

## 🚀 Utilisation

### Lancer la génération
```bash
./run.sh
```

### Configuration requise

`.env` (inchangé) :
```env
EMAIL_ADDRESS=...
EMAIL_PASSWORD=...
MAIL_FOLDER=CE          # Dossier contenant les deux types d'emails
IMAP_SERVER=imap.free.fr
IMAP_PORT=993

# Optionnel
ENABLE_FTP_UPLOAD=true
FTP_HOST=...
FTP_USER=...
FTP_PASSWORD=...
FTP_REMOTE_PATH=/crieur/output
```

### Résultat de l'exécution
```
============================================================
📰 Sorties
============================================================
✓ 77 événement(s) extrait(s)
✓ Carte générée: carte_des_annonces.html

✅ Sorties générée!

============================================================
📰 Expression Libre
============================================================
✓ 6 événement(s) extrait(s)
✓ Carte générée: carte_expression_libre.html

✅ Expression Libre générée!

============================================================
📤 Upload FTP
✓ 4 fichier(s) uploadé(s)

✅ Résumé:
  ✓ Sorties
  ✓ Expression Libre
```

---

## 📊 Comparaison des deux pages

| Aspect | Sorties | Expression Libre |
|--------|---------|------------------|
| **Sujet email** | `crieur-des-sorties` | `crieur-libre-expression` |
| **Titre** | 📅 Annonces Crieur | 📢 Expression Libre |
| **Fichier HTML** | annonces.html | expression_libre.html |
| **Fichier Carte** | carte_des_annonces.html | carte_expression_libre.html |
| **Couleur menu** | Vert (#6b7d1e) | Or (#f4c430) |
| **Lien carte** | 🗺️ Carte des sorties | 🗺️ Carte des contributions |
| **Géolocalisation** | Oui (si lieu présent) | Oui (si lieu présent) |
| **Type de contenu** | Événements structurés | Contributions libres |

---

## 🔧 Extensibilité

Pour ajouter une **troisième source**, modifiez `src/main_v2.py` :

```python
sources = [
    { ... },  # Sorties
    { ... },  # Expression Libre
    {
        'name': 'Nouvelle catégorie',
        'filter': 'crieur-nouvelle-categorie',
        'output_html': 'nouvelle_categorie.html',
        'output_map': 'carte_nouvelle_categorie.html',
        'title': 'Nouvelle Catégorie'
    }
]
```

Puis étendez le menu CSS si souhaité.

---

## 📝 Notes importantes

1. **Indépendance des sources** - Chaque source a ses propres fichiers HTML et carte
2. **Cohérence visuelle** - Même CSS, même template, styles adaptatifs
3. **Performance** - Les deux pages sont générées sequentiellement (pas parallèle)
4. **FTP unique** - Tous les fichiers sont uploadés ensemble en une seule connexion
5. **Compatibilité** - Le code précédent (`main.py`) est conservé pour références

---

## ✅ Tests effectués

- ✓ Génération des deux pages
- ✓ Navigation entre sorties et expression libre
- ✓ Menu actif selon la page
- ✓ Géolocalisation (sorties avec lieu)
- ✓ Upload FTP des 4 fichiers
- ✓ Responsive design (mobile/desktop)

---

## 📚 Documentation complète

Voir [DEUX_SOURCES_ANNONCES.md](docs/DEUX_SOURCES_ANNONCES.md) pour une documentation technique détaillée.

---

**Statut** : ✅ Implémentation complète et testée
**Date** : 12 décembre 2025
**Branch** : main
