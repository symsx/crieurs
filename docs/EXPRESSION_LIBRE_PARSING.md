# Traitement Expression Libre - Parsing Personnalisé

## Vue d'ensemble

Le système a été modifié pour traiter les annonces d'**expression libre** différemment des **sorties** structurées. Les deux sources utilisent maintenant des pipelines de parsing et de rendu distincts.

## Architecture

### 1. Logique de Sélection (main_v2.py)

La fonction `process_annonces_source()` contient maintenant une logique conditionnelle :

```python
if source['filter'] == 'crieur-libre-expression':
    # Pipeline d'expression libre
    events = extract_libre_expression_events(email_content)
else:
    # Pipeline de sorties
    events = consolidate_events(sommaire, messages)
```

### 2. Extraction d'Expression Libre

#### Fonction : `extract_libre_expression_events(email_content)`

**Entrée :** Email brut avec structure :
```
Message-ID: ...
Date: ...

[Auteur] - [Lieu]
-----------------------------------

Titre
====================================

Texte libre contenant le contenu de l'annonce
Peut avoir plusieurs paragraphes
Peut contenir des liens, numéros de téléphone, emails

-------------------------

Contactez directement ...
```

**Processus:**
1. Extrait le sommaire pour obtenir titre + email auteur
2. Récupère chaque message individuel
3. **Parse le texte entre les tirets** (regex: `-{10,}` ... `\-{25,}`)
4. **Nettoie le titre au début** (enlève la première ligne suivie de `=====...`)
5. Extrait les infos de contact :
   - Numéro de téléphone (regex phone)
   - Lien WhatsApp
   - Email de contact

**Sortie :** Structure événement :
```python
{
    'titre': str,              # Du sommaire
    'mailorga': str,           # Email auteur
    'texte_libre': str,        # Texte nettoyé
    'telephone': str,          # Optionnel
    'whatsapp': str,           # Optionnel
    'mailcontact': str,        # Optionnel
    'is_libre_expression': True
    # Champs vides pour sorties:
    'date_heure_sommaire': '',
    'lieu_detail': '',
    'descriptif': '',
    # etc.
}
```

### 3. Conversion au Format HTML

Dans `process_annonces_source()`, la conversion diffère selon le type :

#### Sorties (structurées)
```python
event_html = {
    'subject': event['titre'],
    'date': event['date_heure_sommaire'],      # Rempli
    'location': event['lieu_detail'],          # Rempli
    'description': event['descriptif'],        # Rempli
    'links': [...],                            # Rempli
    'is_libre_expression': False               # 🔑 Marqueur
}
```

#### Expression Libre (texte libre)
```python
event_html = {
    'subject': event['titre'],
    'date': '',                                # Vide
    'location': '',                            # Vide
    'description': event['texte_libre'],       # Texte libre ✅
    'links': None,                             # Aucun lien
    'is_libre_expression': True                # 🔑 Marqueur
}
```

### 4. Rendu HTML (email_reader.py)

La fonction `_generate_event_card()` contient maintenant deux branches :

#### Expression Libre
```html
<div class="event-card event-card-libre">
    <h3>Titre</h3>
    
    <div class="event-libre-text">
        [Texte libre directement visible - PAS de popup]
    </div>
    
    [Infos de contact si présentes]
    
    <div class="event-info">📧 Auteur</div>
</div>
```

**Caractéristiques:**
- ✅ Classe `event-card-libre` (bordure OR au lieu de VERT)
- ✅ Pas de `.event-description-tooltip` (pas de popup)
- ✅ Texte dans `.event-libre-text` (visible directement)
- ✅ Pas de section date/lieu
- ✅ Contact info si disponible

#### Sorties
```html
<div class="event-card">
    <h3>Titre</h3>
    
    <div class="event-description-tooltip">
        [Popup au hover du titre]
    </div>
    
    <div class="event-info">📅 Date</div>
    <div class="event-info">📍 Lieu</div>
    ...
</div>
```

**Caractéristiques:**
- ✅ Classe `event-card` uniquement
- ✅ `.event-description-tooltip` pour popup
- ✅ Section date avec icône 📅
- ✅ Section lieu avec icône 📍
- ✅ Tous les éléments structurés

### 5. Styles CSS

#### .event-card-libre
```css
.event-card-libre {
    border-left-color: var(--gco-gold);  /* OR au lieu de VERT */
}

.event-card-libre:hover {
    border-left-color: var(--gco-green); /* Change au VERT au hover */
}
```

#### .event-libre-text
```css
.event-libre-text {
    color: var(--text-primary);
    line-height: 1.6;
    margin: 15px 0;
    padding: 15px;
    background: var(--bg-light);
    border-radius: 8px;
    word-break: break-word;
    font-size: 0.95em;
}
```

## Résultats

| Aspect | Sorties | Expression Libre |
|--------|---------|------------------|
| **Nombre d'événements** | 77 | 6 |
| **Structure** | Quand/Où/Descriptif | Texte libre |
| **Date affichée** | ✅ Oui | ❌ Non |
| **Lieu affiché** | ✅ Oui | ❌ Non |
| **Popup au hover** | ✅ Oui (tooltip) | ❌ Non |
| **Texte visible** | Popup seulement | ✅ Directement dans tuile |
| **Couleur tuile** | Vert GCO | Or GCO |
| **Liens** | ✅ Oui | ❌ Non |
| **Géolocalisation** | ✅ Oui | ❌ Non |

## Processus de Parsing Expression Libre

```
Email brut
    ↓
extract_sommaire()           → Titre + Email auteur
    ↓
extract_libre_expression_events()
    ├── Parse texte entre tirets (regex)
    ├── Nettoie doublon titre
    ├── Extrait phone/WhatsApp/email
    └── Crée événement simplifié
    ↓
Conversion HTMLGenerator
    ├── Marque is_libre_expression=True
    ├── Utilise texte_libre pour description
    └── Laisse date/location vides
    ↓
_generate_event_card()
    ├── Vérifie is_libre_expression
    ├── Génère template simplifié
    └── Pas de popup ni date/lieu
    ↓
HTML final avec .event-card-libre
    └── Affiche texte directement dans tuile
```

## Points d'Attention

### ✅ Préservation des Sorties

**IMPORTANT:** Aucun changement au pipeline de sorties!

- Fonction `extract_sommaire()` - INCHANGÉE
- Fonction `consolidate_events()` - INCHANGÉE
- Pipeline sorties dans `process_annonces_source()` - INCHANGÉ
- Génération de popup - INCHANGÉE
- 76 sorties générées avec popups fonctionnelles ✅

### ⚠️ Limitations Expression Libre

- **Pas de géolocalisation** : aucune structure d'adresse structurée
- **Pas de liens automtiques** : sauf email/phone extraits du texte
- **Texte varié** : dépend du format envoyé par l'auteur
- **Pas de sommaire détaillé** : affichage direct du texte brut

## Fichiers Modifiés

### `src/main_v2.py`
- Ajout `extract_libre_expression_events()` - 73 lignes
- Modification logique dans `process_annonces_source()` - 30 lignes
- Conversion format HTML conditionnelle - 40 lignes

### `src/email_reader.py`
- Réfactorisation `_generate_event_card()` - 150 lignes (branche expression libre)
- Préservation template sorties - 100 lignes

### `public/style.css`
- Ajout `.event-card-libre` styles - 18 lignes
- Ajout `.event-libre-text` styles - 10 lignes

## Tests Validés

✅ Syntaxe Python - OK (pas d'erreurs)
✅ Extraction sorties - 77 événements générés
✅ Extraction expression libre - 6 événements générés
✅ HTML sorties - 2975 lignes, 76 popups
✅ HTML expression libre - 154 lignes, 0 popups
✅ Navigation - Titre correct sur chaque page
✅ Upload FTP - 4 fichiers uploadés sans erreur
✅ Git commit - Changements pushés sur main
